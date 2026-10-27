from pathlib import Path

from src.llm.cli_client import ask_model_cached_with_usage
from src.llm.schemas.model_response import ModelResponse
from src.pipeline.constants import (
    FOREIGN_FUNCTION_WORDS,
    HUNGARIAN_FUNCTION_WORDS,
    QUESTION_WORD_PATTERN,
    TRANSLATION_SCHEMA,
)


def is_foreign_question(question: str) -> bool:
    words = [word.lower() for word in QUESTION_WORD_PATTERN.findall(question)]
    foreign_word_count = sum(word in FOREIGN_FUNCTION_WORDS for word in words)
    hungarian_word_count = sum(word in HUNGARIAN_FUNCTION_WORDS for word in words)
    return foreign_word_count > hungarian_word_count


def translate_question(question: str, prompt_path: Path) -> ModelResponse:
    response, _ = ask_model_cached_with_usage(prompt_path, question, TRANSLATION_SCHEMA)
    return response
