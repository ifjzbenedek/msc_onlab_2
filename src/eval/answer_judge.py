import json
from pathlib import Path

from src.eval.constants import JUDGE_SCHEMA, JUDGE_USER_PROMPT_TEMPLATE, SOURCE_TEXT_SEPARATOR
from src.eval.schemas.judgment import Judgment
from src.llm.cli_client import ask_model_cached_with_usage
from src.storage.files import write_text_atomically


def build_judge_prompt(question: str, source_texts: list[str], answer: str, cited_texts: list[str]) -> str:
    return JUDGE_USER_PROMPT_TEMPLATE.format(
        question=question,
        source=SOURCE_TEXT_SEPARATOR.join(source_texts),
        answer=answer,
        cited=SOURCE_TEXT_SEPARATOR.join(cited_texts),
    )


def judge_answer(
    question: str, source_texts: list[str], answer: str, cited_texts: list[str], prompt_path: Path
) -> Judgment:
    response, _ = ask_model_cached_with_usage(
        prompt_path, build_judge_prompt(question, source_texts, answer, cited_texts), JUDGE_SCHEMA
    )
    return Judgment(
        verdict=response.output["verdict"],
        reason=response.output["reason"],
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        seconds=response.seconds,
    )


def load_judgments(path: Path) -> dict[str, Judgment]:
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {question_id: Judgment(**record) for question_id, record in records.items()}


def save_judgments(judgments: dict[str, Judgment], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records = {question_id: judgment.model_dump() for question_id, judgment in judgments.items()}
    write_text_atomically(path, json.dumps(records, ensure_ascii=False, indent=2))
