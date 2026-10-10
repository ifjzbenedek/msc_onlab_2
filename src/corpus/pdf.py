from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import pymupdf
from pymupdf.table import Table

from src.corpus.constants import (
    FOOTER_START_RATIO,
    HEADING_FONT_SIZE_RATIO,
    MIN_FONT_SIZE_RATIO,
    MIN_WORD_GAP,
    SAME_ROW_BASELINE_TOLERANCE,
    SYMBOL_FONT_TRANSLATION_TABLE,
    TABLE_CELL_SEPARATOR,
)
from src.corpus.schemas.text_line import TextLine


def extract_page_texts(pdf_path: Path) -> list[str]:
    with pymupdf.open(pdf_path) as pdf:
        return [page.get_text() for page in pdf]


def iterate_spans(page: pymupdf.Page) -> Iterator[dict]:
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            yield from line["spans"]


def find_body_font_size(pdf: pymupdf.Document) -> float:
    character_count_by_size: Counter[float] = Counter()
    for page in pdf:
        for span in iterate_spans(page):
            character_count_by_size[span["size"]] += len(span["text"].strip())
    body_font_size, _ = character_count_by_size.most_common(1)[0]
    return body_font_size


def get_baseline(span: dict) -> float:
    return span["origin"][1]


def get_left_edge(span: dict) -> float:
    return span["bbox"][0]


def get_right_edge(span: dict) -> float:
    return span["bbox"][2]


def group_spans_into_rows(spans: list[dict]) -> list[list[dict]]:
    rows: list[list[dict]] = []
    for span in sorted(spans, key=get_baseline):
        if rows and get_baseline(span) - get_baseline(rows[-1][0]) <= SAME_ROW_BASELINE_TOLERANCE:
            rows[-1].append(span)
        else:
            rows.append([span])
    return [sorted(row, key=get_left_edge) for row in rows]


def join_row_text(row: list[dict]) -> str:
    text = row[0]["text"]
    for previous_span, span in zip(row, row[1:]):
        gap = get_left_edge(span) - get_right_edge(previous_span)
        separator = " " if gap > MIN_WORD_GAP else ""
        text += separator + span["text"]
    return " ".join(text.translate(SYMBOL_FONT_TRANSLATION_TABLE).split())


def starts_with_emphasis(row: list[dict], body_font_size: float) -> bool:
    first_span = row[0]
    is_bold = bool(first_span["flags"] & pymupdf.TEXT_FONT_BOLD)
    is_large = first_span["size"] >= HEADING_FONT_SIZE_RATIO * body_font_size
    return is_bold or is_large


def belongs_to_page_text(
    span: dict, body_font_size: float, footer_start: float, tables: list[Table]
) -> bool:
    is_blank = not span["text"].strip()
    is_small = span["size"] < MIN_FONT_SIZE_RATIO * body_font_size
    is_in_footer = get_baseline(span) >= footer_start
    is_in_table = any(pymupdf.Rect(table.bbox).contains(span["origin"]) for table in tables)
    return not (is_blank or is_small or is_in_footer or is_in_table)


def join_table_cells(cells: list[str | None]) -> str:
    cell_texts = [" ".join(cell.split()) for cell in cells if cell]
    return TABLE_CELL_SEPARATOR.join(cell_texts)


def read_table_lines(table: Table, page_number: int) -> list[TextLine]:
    return [
        TextLine(page=page_number, text=join_table_cells(cells), is_emphasized=False)
        for cells in table.extract()
    ]


def read_page_lines(page: pymupdf.Page, page_number: int, body_font_size: float) -> list[TextLine]:
    tables = page.find_tables().tables
    footer_start = FOOTER_START_RATIO * page.rect.height
    spans = [
        span for span in iterate_spans(page)
        if belongs_to_page_text(span, body_font_size, footer_start, tables)
    ]
    text_lines = [
        TextLine(
            page=page_number,
            text=join_row_text(row),
            is_emphasized=starts_with_emphasis(row, body_font_size),
        )
        for row in group_spans_into_rows(spans)
    ]
    table_lines = [line for table in tables for line in read_table_lines(table, page_number)]
    return [line for line in text_lines + table_lines if line.text]


def read_document_lines(pdf_path: Path, skipped_pages: set[int]) -> list[TextLine]:
    lines: list[TextLine] = []
    with pymupdf.open(pdf_path) as pdf:
        body_font_size = find_body_font_size(pdf)
        for page_number, page in enumerate(pdf, start=1):
            if page_number not in skipped_pages:
                lines += read_page_lines(page, page_number, body_font_size)
    return lines
