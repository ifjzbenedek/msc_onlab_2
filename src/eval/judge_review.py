import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from statistics import mean

from src.eval.answer_metrics import find_cited_chunks, find_source_texts
from src.eval.constants import (
    B_SET_GROUP,
    ESCAPED_SCRIPT_END_TAG,
    FULOP_GROUP,
    FULOP_LANGUAGE,
    HYPHENATED_LINE_BREAK_PATTERN,
    JOINED_LINE_BREAK,
    JUDGE_REVIEW_SAMPLE_SIZE,
    REVIEW_DATA_PLACEHOLDER,
    REVIEW_KEY_LENGTH,
    REVIEW_KEY_PLACEHOLDER,
    SCRIPT_END_TAG,
    SOFT_LINE_BREAK_PATTERN,
    SPLIT_SEED,
    VERDICTS_FIELD,
)
from src.eval.evaluation_context import EvaluationContext
from src.eval.schemas.cited_excerpt import CitedExcerpt
from src.eval.schemas.review_case import ReviewCase
from src.pipeline.constants import CHUNK_HEADER_SEPARATOR
from src.pipeline.schemas.generated_answer import GeneratedAnswer


def draw_review_sample(judged_ids: list[str]) -> list[str]:
    sample_size = min(JUDGE_REVIEW_SAMPLE_SIZE, len(judged_ids))
    return sorted(random.Random(SPLIT_SEED).sample(sorted(judged_ids), sample_size))


def clean_source_for_reading(text: str) -> str:
    joined_text = HYPHENATED_LINE_BREAK_PATTERN.sub(JOINED_LINE_BREAK, text)
    return SOFT_LINE_BREAK_PATTERN.sub(" ", joined_text)


def split_chunk_header(chunk_text: str) -> CitedExcerpt:
    header, _, body = chunk_text.partition(CHUNK_HEADER_SEPARATOR)
    return CitedExcerpt(header=header, text=body)


def build_review_case(question_id: str, generated: GeneratedAnswer, context: EvaluationContext) -> ReviewCase:
    is_fulop_question = question_id in context.qa_items_by_id
    source_texts = find_source_texts(question_id, context)
    return ReviewCase(
        id=question_id,
        group=FULOP_GROUP if is_fulop_question else B_SET_GROUP,
        language=FULOP_LANGUAGE if is_fulop_question else context.b_items_by_id[question_id].language,
        question=generated.question,
        source=[clean_source_for_reading(text) for text in source_texts] if is_fulop_question else source_texts,
        answer=generated.answer,
        cited=[split_chunk_header(chunk.text) for chunk in find_cited_chunks(generated, context)],
    )


def build_review_key(question_ids: list[str]) -> str:
    return hashlib.sha256(",".join(question_ids).encode("utf-8")).hexdigest()[:REVIEW_KEY_LENGTH]


def render_review_page(template: str, cases: list[ReviewCase], review_key: str) -> str:
    cases_json = json.dumps([case.model_dump() for case in cases], ensure_ascii=False)
    safe_cases_json = cases_json.replace(SCRIPT_END_TAG, ESCAPED_SCRIPT_END_TAG)
    return template.replace(REVIEW_DATA_PLACEHOLDER, safe_cases_json).replace(REVIEW_KEY_PLACEHOLDER, review_key)


def load_written_verdicts(path: Path) -> dict[str, str]:
    return json.loads(path.read_text(encoding="utf-8"))[VERDICTS_FIELD]


def compute_agreement[Label](pairs: list[tuple[Label, Label]]) -> float:
    return mean(first == second for first, second in pairs)


def compute_cohens_kappa[Label](pairs: list[tuple[Label, Label]]) -> float:
    first_counts = Counter(first for first, _ in pairs)
    second_counts = Counter(second for _, second in pairs)
    expected = sum(first_counts[label] * second_counts[label] for label in first_counts) / len(pairs) ** 2
    if expected == 1:
        return 1.0
    return (compute_agreement(pairs) - expected) / (1 - expected)
