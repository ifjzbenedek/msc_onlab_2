import json
from pathlib import Path

from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.storage.files import write_text_atomically


def load_answers(path: Path) -> dict[str, GeneratedAnswer]:
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {question_id: GeneratedAnswer(**record) for question_id, record in records.items()}


def save_answers(answers: dict[str, GeneratedAnswer], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = {question_id: answer.model_dump() for question_id, answer in answers.items()}
    write_text_atomically(path, json.dumps(records, ensure_ascii=False, indent=2))
