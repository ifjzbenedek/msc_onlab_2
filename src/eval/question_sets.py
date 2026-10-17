from pathlib import Path

from src.eval.b_set import load_b_set
from src.eval.qa_dataset import load_qa_items
from src.eval.splits import draw_evaluation_subset, load_id_list


def collect_answer_questions(qa_path: Path, test_ids_path: Path, b_set_path: Path) -> dict[str, str]:
    qa_items = {qa_item.id: qa_item for qa_item in load_qa_items(qa_path)}
    test_items = [qa_items[qa_id] for qa_id in load_id_list(test_ids_path)]
    questions = {qa_id: qa_items[qa_id].question for qa_id in draw_evaluation_subset(test_items)}
    if b_set_path.exists():
        questions |= {item.id: item.question for item in load_b_set(b_set_path)}
    return questions
