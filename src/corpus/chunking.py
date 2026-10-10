from src.corpus.constants import (
    ATTACHED_HYPHEN_AT_END_PATTERN,
    CHUNK_HEADER_FORMAT,
    CHUNK_ID_FORMAT,
    DOCUMENT_SHORT_NAMES,
    HYPHEN,
    HYPHENATED_WORD_PATTERN,
    LINE_END_WORD_PATTERN,
    LINE_START_WORD_PATTERN,
    MAX_CHUNK_CHARACTERS,
    TABLE_CELL_SEPARATOR,
    UNIT_END_CHARACTERS,
    UNIT_START_PATTERN,
)
from src.corpus.schemas.chunk import Chunk
from src.corpus.schemas.paragraph import Paragraph
from src.corpus.schemas.section import Section
from src.corpus.schemas.text_line import TextLine


def collect_hyphenated_words(lines: list[TextLine]) -> set[str]:
    return {word.lower() for line in lines for word in HYPHENATED_WORD_PATTERN.findall(line.text)}


def is_word_break(text: str, next_text: str, hyphenated_words: set[str]) -> bool:
    left_word = LINE_END_WORD_PATTERN.search(text)
    right_word = LINE_START_WORD_PATTERN.match(next_text)
    if not (left_word and right_word):
        return False
    is_between_lowercase = left_word[1][-1].islower() and right_word[1][0].islower()
    compound = f"{left_word[1]}{HYPHEN}{right_word[1]}".lower()
    return is_between_lowercase and compound not in hyphenated_words


def join_lines(lines: list[TextLine], hyphenated_words: set[str]) -> str:
    text = lines[0].text
    for line in lines[1:]:
        if not ATTACHED_HYPHEN_AT_END_PATTERN.search(text):
            text += " " + line.text
        elif is_word_break(text, line.text, hyphenated_words):
            text = text.removesuffix(HYPHEN) + line.text
        else:
            text += line.text
    return text


def starts_new_unit(previous_text: str, text: str) -> bool:
    is_table_row = TABLE_CELL_SEPARATOR in text
    is_numbered_start = UNIT_START_PATTERN.match(text) is not None
    return is_table_row or (is_numbered_start and previous_text.endswith(UNIT_END_CHARACTERS))


def split_into_units(lines: list[TextLine]) -> list[list[TextLine]]:
    units: list[list[TextLine]] = [[lines[0]]]
    for previous_line, line in zip(lines, lines[1:]):
        if starts_new_unit(previous_line.text, line.text):
            units.append([line])
        else:
            units[-1].append(line)
    return units


def build_paragraphs(lines: list[TextLine], hyphenated_words: set[str]) -> list[Paragraph]:
    return [
        Paragraph(text=join_lines(unit, hyphenated_words), page_start=unit[0].page, page_end=unit[-1].page)
        for unit in split_into_units(lines)
    ]


def pack_paragraphs(paragraphs: list[Paragraph], max_characters: int) -> list[list[Paragraph]]:
    parts: list[list[Paragraph]] = [[]]
    part_length = 0
    for paragraph in paragraphs:
        if parts[-1] and part_length + len(paragraph.text) > max_characters:
            parts.append([])
            part_length = 0
        parts[-1].append(paragraph)
        part_length += len(paragraph.text)
    return parts


def build_chunk(document: str, section: Section, part_number: int, paragraphs: list[Paragraph]) -> Chunk:
    header = CHUNK_HEADER_FORMAT.format(
        document=DOCUMENT_SHORT_NAMES[document], label=section.label, title=section.title
    ).strip()
    body = "\n".join(paragraph.text for paragraph in paragraphs)
    return Chunk(
        id=CHUNK_ID_FORMAT.format(document=document, label=section.label, part=part_number),
        document=document,
        section=section.label,
        page_start=paragraphs[0].page_start,
        page_end=paragraphs[-1].page_end,
        text=f"{header}\n{body}",
    )


def chunk_document(document: str, sections: list[Section]) -> list[Chunk]:
    sections_with_text = [section for section in sections if section.lines]
    hyphenated_words = collect_hyphenated_words(
        [line for section in sections_with_text for line in section.lines]
    )
    chunks: list[Chunk] = []
    for section in sections_with_text:
        paragraphs = build_paragraphs(section.lines, hyphenated_words)
        for part_number, part in enumerate(pack_paragraphs(paragraphs, MAX_CHUNK_CHARACTERS), start=1):
            chunks.append(build_chunk(document, section, part_number, part))
    return chunks
