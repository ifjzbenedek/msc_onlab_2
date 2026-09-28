from src.eval.overlap import Ngram, measure_passage_coverage
from src.eval.schemas.qa_item import QAItem


def find_spanned_pages(
    source_passage: str, start_page: int, page_texts: list[str], ignored_ngrams: set[Ngram]
) -> list[int]:
    spanned_pages = [start_page]
    for next_page in range(start_page + 1, len(page_texts) + 1):
        next_page_text = page_texts[next_page - 1]
        if measure_passage_coverage(source_passage, next_page_text, ignored_ngrams) == 0:
            break
        spanned_pages.append(next_page)
    return spanned_pages


def add_spanned_pages(
    qa_items: list[QAItem],
    page_texts_by_document: dict[str, list[str]],
    ignored_ngrams_by_document: dict[str, set[Ngram]],
) -> None:
    for qa_item in qa_items:
        page_texts = page_texts_by_document[qa_item.source_document]
        ignored_ngrams = ignored_ngrams_by_document[qa_item.source_document]
        for chunk in qa_item.expected_chunks:
            chunk.spanned_pages = find_spanned_pages(
                chunk.text, chunk.pdf_page, page_texts, ignored_ngrams
            )
