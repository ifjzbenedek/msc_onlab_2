from src.corpus.constants import (
    ANNEX_LABEL_ENDING,
    BRACKET_TITLE_PATTERN,
    NUMBERED_HEADING_PATTERN,
    PREAMBLE_LABEL,
    SECTION_START_PATTERN,
    TITLE_CLOSING_BRACKET,
    TITLE_OPENING_BRACKET,
)
from src.corpus.schemas.section import Section
from src.corpus.schemas.text_line import TextLine


def is_section_start(line: TextLine) -> bool:
    return line.is_emphasized and SECTION_START_PATTERN.match(line.text) is not None


def has_unclosed_title(line: TextLine) -> bool:
    return (
        is_section_start(line)
        and TITLE_OPENING_BRACKET in line.text
        and TITLE_CLOSING_BRACKET not in line.text
    )


def merge_wrapped_titles(lines: list[TextLine]) -> list[TextLine]:
    merged_lines: list[TextLine] = []
    for line in lines:
        if merged_lines and has_unclosed_title(merged_lines[-1]):
            title_start = merged_lines[-1]
            merged_lines[-1] = title_start.model_copy(update={"text": f"{title_start.text} {line.text}"})
        else:
            merged_lines.append(line)
    return merged_lines


def extract_heading_title(heading_lines: list[TextLine]) -> str:
    numbered_indexes = [
        index for index, line in enumerate(heading_lines) if NUMBERED_HEADING_PATTERN.match(line.text)
    ]
    title_start = numbered_indexes[-1] if numbered_indexes else len(heading_lines) - 1
    title_text = " ".join(line.text for line in heading_lines[title_start:])
    numbered_heading = NUMBERED_HEADING_PATTERN.match(title_text)
    return numbered_heading["title"] if numbered_heading else title_text


def start_section(line: TextLine, heading_title: str) -> Section:
    section_start = SECTION_START_PATTERN.match(line.text)
    label, rest = section_start["label"], section_start["rest"]
    bracket_title = BRACKET_TITLE_PATTERN.match(rest)
    if bracket_title:
        title, body = bracket_title["title"], bracket_title["body"]
    elif label.endswith(ANNEX_LABEL_ENDING):
        title, body = rest, ""
    else:
        title, body = heading_title, rest
    body_lines = [line.model_copy(update={"text": body, "is_emphasized": False})] if body else []
    return Section(label=label, title=title, lines=body_lines)


def split_into_sections(lines: list[TextLine]) -> list[Section]:
    sections: list[Section] = []
    pending_headings: list[TextLine] = []
    heading_title = ""
    for line in merge_wrapped_titles(lines):
        if is_section_start(line):
            if pending_headings:
                heading_title = extract_heading_title(pending_headings)
            sections.append(start_section(line, heading_title))
            pending_headings = []
        elif line.is_emphasized:
            pending_headings.append(line)
        else:
            if not sections:
                sections.append(Section(label=PREAMBLE_LABEL, title="", lines=[]))
            sections[-1].lines.extend([*pending_headings, line])
            pending_headings = []
    return sections
