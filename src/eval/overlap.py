from collections import Counter

from src.eval.constants import HYPHENATED_LINE_BREAK_PATTERN, WORD_PATTERN, WORDS_PER_NGRAM

type Ngram = tuple[str, ...]


def split_into_words(text: str) -> list[str]:
    dehyphenated_text = HYPHENATED_LINE_BREAK_PATTERN.sub(r"\1\2", text)
    return WORD_PATTERN.findall(dehyphenated_text.lower())


def build_ngrams(words: list[str], words_per_ngram: int = WORDS_PER_NGRAM) -> set[Ngram]:
    last_start = len(words) - words_per_ngram
    return {tuple(words[start:start + words_per_ngram]) for start in range(last_start + 1)}


def find_boilerplate_ngrams(page_texts: list[str]) -> set[Ngram]:
    page_count_per_ngram = Counter(
        ngram for page_text in page_texts for ngram in build_ngrams(split_into_words(page_text))
    )
    return {ngram for ngram, page_count in page_count_per_ngram.items() if page_count > 1}


def measure_passage_coverage(
    source_passage: str, candidate_text: str, ignored_ngrams: set[Ngram]
) -> float:
    passage_words = split_into_words(source_passage)
    if not passage_words:
        return 0.0
    words_per_ngram = min(WORDS_PER_NGRAM, len(passage_words))
    passage_ngrams = build_ngrams(passage_words, words_per_ngram) - ignored_ngrams
    if not passage_ngrams:
        return 0.0
    candidate_ngrams = build_ngrams(split_into_words(candidate_text), words_per_ngram)
    found_ngrams = passage_ngrams & candidate_ngrams
    return len(found_ngrams) / len(passage_ngrams)
