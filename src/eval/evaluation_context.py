from dataclasses import dataclass

from src.corpus.schemas.chunk import Chunk
from src.eval.constants import LETTER_WORD_PATTERN
from src.eval.corpus_coverage import build_corpus_ngrams
from src.eval.overlap import Ngram, find_boilerplate_ngrams
from src.eval.retrieval_metrics import SectionKey, build_ngrams_by_section
from src.eval.schemas.b_set_item import BSetItem
from src.eval.schemas.qa_item import QAItem


@dataclass
class EvaluationContext:
    qa_items_by_id: dict[str, QAItem]
    b_items_by_id: dict[str, BSetItem]
    chunks_by_id: dict[str, Chunk]
    ngrams_by_chunk: dict[str, set[Ngram]]
    ngrams_by_section: dict[SectionKey, set[Ngram]]
    ignored_ngrams_by_document: dict[str, set[Ngram]]


def build_evaluation_context(
    qa_items: list[QAItem],
    b_items: list[BSetItem],
    chunks: list[Chunk],
    page_texts_by_document: dict[str, list[str]],
) -> EvaluationContext:
    ngrams_by_chunk = {chunk.id: build_corpus_ngrams([chunk]) for chunk in chunks}
    return EvaluationContext(
        qa_items_by_id={qa_item.id: qa_item for qa_item in qa_items},
        b_items_by_id={item.id: item for item in b_items},
        chunks_by_id={chunk.id: chunk for chunk in chunks},
        ngrams_by_chunk=ngrams_by_chunk,
        ngrams_by_section=build_ngrams_by_section(chunks, ngrams_by_chunk),
        ignored_ngrams_by_document={
            document: find_boilerplate_ngrams(page_texts, LETTER_WORD_PATTERN)
            for document, page_texts in page_texts_by_document.items()
        },
    )


def build_text_context(qa_items: list[QAItem], b_items: list[BSetItem], chunks: list[Chunk]) -> EvaluationContext:
    return EvaluationContext(
        qa_items_by_id={qa_item.id: qa_item for qa_item in qa_items},
        b_items_by_id={item.id: item for item in b_items},
        chunks_by_id={chunk.id: chunk for chunk in chunks},
        ngrams_by_chunk={},
        ngrams_by_section={},
        ignored_ngrams_by_document={},
    )
