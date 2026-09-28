import json
from pathlib import Path

from src.eval.schemas.qa_item import QAItem


def load_qa_items(path: Path) -> list[QAItem]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return [QAItem(**record) for record in records]


def save_qa_items(qa_items: list[QAItem], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [qa_item.model_dump() for qa_item in qa_items]
    json_text = json.dumps(records, ensure_ascii=False, indent=2)
    path.write_text(json_text, encoding="utf-8", newline="\n")
