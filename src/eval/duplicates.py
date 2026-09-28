from collections import defaultdict

from src.eval.constants import DIFFICULTY_ORDER
from src.eval.schemas.qa_item import QAItem


def normalize_question_text(question: str) -> str:
    return " ".join(question.lower().split())


def merge_duplicate_group(group: list[QAItem]) -> QAItem:
    easiest_difficulty = min((item.difficulty for item in group), key=DIFFICULTY_ORDER.index)
    merged_pages = sorted({page for item in group for page in item.expected_pdf_pages})
    merged_chunks = [chunk for item in group for chunk in item.expected_chunks]
    return group[0].model_copy(update={
        "difficulty": easiest_difficulty,
        "expected_pdf_pages": merged_pages,
        "expected_chunks": merged_chunks,
    })


def merge_duplicate_questions(qa_items: list[QAItem]) -> list[QAItem]:
    items_by_question: defaultdict[str, list[QAItem]] = defaultdict(list)
    for qa_item in qa_items:
        items_by_question[normalize_question_text(qa_item.question)].append(qa_item)
    return [merge_duplicate_group(group) for group in items_by_question.values()]
