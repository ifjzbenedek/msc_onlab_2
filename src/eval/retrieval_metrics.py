from collections import Counter, defaultdict
from typing import NamedTuple

from src.corpus.schemas.chunk import Chunk
from src.eval.constants import MIN_PASSAGE_COVERAGE, MIN_SECTION_SHARE, RECALL_CUTOFFS
from src.eval.corpus_coverage import build_passage_ngrams, measure_corpus_coverage
from src.eval.overlap import Ngram
from src.eval.schemas.qa_item import QAItem
from src.eval.schemas.recall_result import RecallResult
from src.retrieval.hybrid import Search


class SectionKey(NamedTuple):
    document: str
    label: str


def build_ngrams_by_section(
    chunks: list[Chunk], ngrams_by_chunk: dict[str, set[Ngram]]
) -> dict[SectionKey, set[Ngram]]:
    ngrams_by_section: defaultdict[SectionKey, set[Ngram]] = defaultdict(set)
    for chunk in chunks:
        ngrams_by_section[SectionKey(chunk.document, chunk.section)] |= ngrams_by_chunk[chunk.id]
    return ngrams_by_section


def find_expected_sections(
    qa_item: QAItem, ngrams_by_section: dict[SectionKey, set[Ngram]], ignored_ngrams: set[Ngram]
) -> list[set[SectionKey]]:
    expected_sections = []
    for expected_chunk in qa_item.expected_chunks:
        passage_ngrams = build_passage_ngrams(expected_chunk.text, ignored_ngrams)
        if not passage_ngrams:
            continue
        shares = {
            section: len(passage_ngrams & ngrams) / len(passage_ngrams)
            for section, ngrams in ngrams_by_section.items()
            if section.document == qa_item.source_document
        }
        sections = {section for section, share in shares.items() if share >= MIN_SECTION_SHARE}
        if not sections:
            largest = max(shares, key=shares.get)
            sections = {largest} if shares[largest] > 0 else set()
        expected_sections.append(sections)
    return expected_sections


def is_retrieval_hit(
    qa_item: QAItem,
    retrieved_chunks: list[Chunk],
    ngrams_by_chunk: dict[str, set[Ngram]],
    ignored_ngrams: set[Ngram],
) -> bool:
    retrieved_ngrams = set().union(*(ngrams_by_chunk[chunk.id] for chunk in retrieved_chunks))
    return measure_corpus_coverage(qa_item, retrieved_ngrams, ignored_ngrams) >= MIN_PASSAGE_COVERAGE


def finds_any_expected_section(expected_sections: list[set[SectionKey]], retrieved_chunks: list[Chunk]) -> bool:
    retrieved = {SectionKey(chunk.document, chunk.section) for chunk in retrieved_chunks}
    return any(sections & retrieved for sections in expected_sections)


def finds_all_expected_sections(expected_sections: list[set[SectionKey]], retrieved_chunks: list[Chunk]) -> bool:
    retrieved = {SectionKey(chunk.document, chunk.section) for chunk in retrieved_chunks}
    return any(sections and sections <= retrieved for sections in expected_sections)


def convert_to_rates(hits: Counter, question_count: int) -> dict[int, float]:
    return {cutoff: hits[cutoff] / question_count for cutoff in RECALL_CUTOFFS}


def measure_recall(
    questions: list[tuple[QAItem, str]],
    search: Search,
    ngrams_by_chunk: dict[str, set[Ngram]],
    ignored_ngrams_by_document: dict[str, set[Ngram]],
    expected_sections_by_id: dict[str, list[set[SectionKey]]],
) -> RecallResult:
    text_hits, any_section_hits, all_section_hits = Counter(), Counter(), Counter()
    for qa_item, question_text in questions:
        retrieved = search(question_text, max(RECALL_CUTOFFS))
        ignored_ngrams = ignored_ngrams_by_document[qa_item.source_document]
        expected_sections = expected_sections_by_id[qa_item.id]
        for cutoff in RECALL_CUTOFFS:
            top_chunks = retrieved[:cutoff]
            text_hits[cutoff] += is_retrieval_hit(qa_item, top_chunks, ngrams_by_chunk, ignored_ngrams)
            any_section_hits[cutoff] += finds_any_expected_section(expected_sections, top_chunks)
            all_section_hits[cutoff] += finds_all_expected_sections(expected_sections, top_chunks)
    return RecallResult(
        text=convert_to_rates(text_hits, len(questions)),
        any_section=convert_to_rates(any_section_hits, len(questions)),
        all_sections=convert_to_rates(all_section_hits, len(questions)),
    )
