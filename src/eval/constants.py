import re

WORDS_PER_NGRAM = 6
HYPHENATED_LINE_BREAK_PATTERN = re.compile(r"(\w)-[ \t]*\n\s*(\w)")
WORD_PATTERN = re.compile(r"\w+")

DIFFICULTY_ORDER = ("easy", "medium", "hard")

COVER_AND_TOC_PAGES = {"bme_tvsz.pdf": {1, 2, 3}}
SPLIT_SEED = 42
DEV_QUESTIONS_PER_STRATUM = 10
TEST_QUESTIONS_PER_STRATUM = 33
