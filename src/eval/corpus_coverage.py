from src.corpus.schemas.chunk import Chunk
from src.eval.constants import LETTER_WORD_PATTERN
from src.eval.overlap import Ngram, build_ngrams, split_into_words
from src.eval.schemas.qa_item import QAItem


def build_corpus_ngrams(chunks: list[Chunk]) -> set[Ngram]:
    return {
        ngram
        for chunk in chunks
        for ngram in build_ngrams(split_into_words(chunk.text, LETTER_WORD_PATTERN))
    }


def build_passage_ngrams(passage_text: str, ignored_ngrams: set[Ngram]) -> set[Ngram]:
    return build_ngrams(split_into_words(passage_text, LETTER_WORD_PATTERN)) - ignored_ngrams


def measure_corpus_coverage(
    qa_item: QAItem, corpus_ngrams: set[Ngram], ignored_ngrams: set[Ngram]
) -> float:
    best_coverage = 0.0
    for expected_chunk in qa_item.expected_chunks:
        passage_ngrams = build_passage_ngrams(expected_chunk.text, ignored_ngrams)
        if passage_ngrams:
            best_coverage = max(best_coverage, len(passage_ngrams & corpus_ngrams) / len(passage_ngrams))
    return best_coverage
