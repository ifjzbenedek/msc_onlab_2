import re

SAME_ROW_BASELINE_TOLERANCE = 2.0
MIN_WORD_GAP = 1.0
HEADING_FONT_SIZE_RATIO = 1.3
MIN_FONT_SIZE_RATIO = 0.77
FOOTER_START_RATIO = 0.94
TABLE_CELL_SEPARATOR = " | "

SYMBOL_FONT_OPERATORS = {0xF0B4: "×", 0xF0D7: "·", 0xF0E5: "∑"}
SYMBOL_FONT_BRACKET_PIECES = {0xF0E9: None, 0xF0EB: None, 0xF0F9: None, 0xF0FB: None}
SYMBOL_FONT_TRANSLATION_TABLE = str.maketrans(SYMBOL_FONT_OPERATORS | SYMBOL_FONT_BRACKET_PIECES)

CORPUS_DOCUMENTS = ("bme_tvsz.pdf", "munka_torvenykonyve.pdf")
SKIPPED_PAGES_BY_DOCUMENT = {"bme_tvsz.pdf": {1, 2, 3}}

SECTION_START_PATTERN = re.compile(r"^(?P<label>\d+(?:/[A-Z])?\. §|\d+\. melléklet)\s*(?P<rest>.*)$")
BRACKET_TITLE_PATTERN = re.compile(r"^,?\s*\[(?P<title>[^\]]*)\]\s*(?P<body>.*)$")
TITLE_OPENING_BRACKET = "["
TITLE_CLOSING_BRACKET = "]"
NUMBERED_HEADING_PATTERN = re.compile(r"^\d+(?:/[A-Z])?\.\s+(?P<title>\S.*)$")
ANNEX_LABEL_ENDING = "melléklet"
PREAMBLE_LABEL = "preambulum"

HYPHEN = "-"
ATTACHED_HYPHEN_AT_END_PATTERN = re.compile(r"\S-$")
LINE_END_WORD_PATTERN = re.compile(r"(\w+)-$")
LINE_START_WORD_PATTERN = re.compile(r"^(\w+)")
HYPHENATED_WORD_PATTERN = re.compile(r"\w+-\w+")
UNIT_START_PATTERN = re.compile(r"^(\(\d+[a-z]?\)|\d+[a-z]?\.)\s")
UNIT_END_CHARACTERS = (".", ":", ";")
MAX_CHUNK_CHARACTERS = 3000
DOCUMENT_SHORT_NAMES = {"bme_tvsz.pdf": "TVSZ", "munka_torvenykonyve.pdf": "Mt."}
CHUNK_HEADER_FORMAT = "{document} – {label} {title}"
CHUNK_ID_FORMAT = "{document}:{label}:{part}"
