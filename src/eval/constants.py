import re

WORDS_PER_NGRAM = 6
HYPHENATED_LINE_BREAK_PATTERN = re.compile(r"(\w)-[ \t]*\n\s*(\w)")
WORD_PATTERN = re.compile(r"\w+")
LETTER_WORD_PATTERN = re.compile(r"[^\W\d_]+")
MIN_PASSAGE_COVERAGE = 0.5

DIFFICULTY_ORDER = ("easy", "medium", "hard")

COVER_AND_TOC_PAGES = {"bme_tvsz.pdf": {1, 2, 3}}
DOCUMENTS_WITH_AMENDMENT_FOOTNOTES = {"bme_tvsz.pdf"}
AMENDMENT_QUESTION_PATTERN = re.compile(
    r"szenátusi határozat|lábjegyzet|módosították|"
    r"hatálybalép|hatályba lép|lép\w* hatályba|hatályos",
    re.IGNORECASE,
)

SPLIT_SEED = 42
DEV_QUESTIONS_PER_STRATUM = 10
TEST_QUESTIONS_PER_STRATUM = 40
