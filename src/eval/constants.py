import re

WORDS_PER_NGRAM = 6
HYPHENATED_LINE_BREAK_PATTERN = re.compile(r"(\w)-[ \t]*\n\s*(\w)")
WORD_PATTERN = re.compile(r"\w+")
LETTER_WORD_PATTERN = re.compile(r"[^\W\d_]+")
MIN_PASSAGE_COVERAGE = 0.5
MIN_SECTION_SHARE = 0.25
RECALL_CUTOFFS = (1, 3, 10)
ORIGINAL_QUESTION_STYLE = "original"
RERANKED_EVALUATION_STYLES = ("original", "english", "casual")

TARGET_PRECISION = 0.95
RISK_COVERAGE_PRINTED_POINTS = 10
CRAG_THRESHOLD_GRID = (0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9)
CRAG_TUNING_STYLES = RERANKED_EVALUATION_STYLES
CRAG_EXPANSION_BANDS = ((0.0, 0.01), (0.01, 0.05), (0.05, 0.2), (0.2, 0.5))
ANSWER_CONTEXT_CUTOFF = 3
SYSTEM_NAMES = ("baseline", "crag", "full", "llm_crag")

JUDGE_USER_PROMPT_TEMPLATE = (
    "Kérdés:\n{question}\n\nForrásszöveg:\n{source}\n\nA rendszer válasza:\n{answer}"
    "\n\nA válaszban hivatkozott szabályzat-részletek:\n{cited}"
)
SOURCE_TEXT_SEPARATOR = "\n\n---\n\n"
CORRECT_VERDICT = "correct"
PARTIALLY_CORRECT_VERDICT = "partially_correct"
INCORRECT_VERDICT = "incorrect"
JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": [CORRECT_VERDICT, PARTIALLY_CORRECT_VERDICT, INCORRECT_VERDICT]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
    "additionalProperties": False,
}

JUDGE_REVIEW_SYSTEM = "baseline"
JUDGE_REVIEW_SAMPLE_SIZE = 50
REVIEW_DATA_PLACEHOLDER = "__REVIEW_DATA__"
REVIEW_KEY_PLACEHOLDER = "__REVIEW_KEY__"
REVIEW_KEY_LENGTH = 12
SCRIPT_END_TAG = "</"
ESCAPED_SCRIPT_END_TAG = "<\\/"
SOFT_LINE_BREAK_PATTERN = re.compile(r"\n(?!\(\d)")
JOINED_LINE_BREAK = r"\1\2"
FULOP_GROUP = "fulop"
B_SET_GROUP = "b"
FULOP_LANGUAGE = "hu"
VERDICTS_FIELD = "verdicts"

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
EVALUATION_QUESTIONS_PER_STRATUM = 25
