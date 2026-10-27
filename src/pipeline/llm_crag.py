import time
from pathlib import Path

from src.llm.schemas.model_response import ModelResponse
from src.pipeline.baseline import add_model_costs, answer_from_context
from src.pipeline.constants import (
    ANSWER_CONTEXT_CHUNK_COUNT,
    LLM_CALLS_PER_TRANSLATION,
    RETRIED_ANSWER_ATTEMPTS,
    RETRY_CONTEXT_CHUNK_COUNT,
)
from src.pipeline.query_translation import is_foreign_question, translate_question
from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.retrieval.system import RetrievalSystem, retrieve


def find_search_question(question: str, translate_prompt_path: Path) -> tuple[str, ModelResponse | None]:
    if not is_foreign_question(question):
        return question, None
    translation = translate_question(question, translate_prompt_path)
    return translation.output["translation"], translation


def combine_attempts(first: GeneratedAnswer, second: GeneratedAnswer) -> GeneratedAnswer:
    combined = add_model_costs(second, first.llm_calls, first.input_tokens, first.output_tokens, first.llm_seconds)
    return combined.model_copy(update={"answer_attempts": RETRIED_ANSWER_ATTEMPTS})


def add_translation(generated: GeneratedAnswer, search_question: str, translation: ModelResponse) -> GeneratedAnswer:
    translated = add_model_costs(
        generated, LLM_CALLS_PER_TRANSLATION, translation.input_tokens, translation.output_tokens, translation.seconds
    )
    return translated.model_copy(update={"search_question": search_question})


def answer_with_llm_crag(
    system: RetrievalSystem, question: str, answer_prompt_path: Path, translate_prompt_path: Path
) -> GeneratedAnswer:
    search_question, translation = find_search_question(question, translate_prompt_path)
    start = time.perf_counter()
    ranked = retrieve(system, search_question)
    retrieval_seconds = time.perf_counter() - start
    first_context = ranked[:ANSWER_CONTEXT_CHUNK_COUNT]
    retry_context = ranked[ANSWER_CONTEXT_CHUNK_COUNT:ANSWER_CONTEXT_CHUNK_COUNT + RETRY_CONTEXT_CHUNK_COUNT]
    generated = answer_from_context(question, first_context, ranked, retrieval_seconds, answer_prompt_path)
    if not generated.has_cited_answer() and retry_context:
        retried = answer_from_context(question, retry_context, ranked, retrieval_seconds, answer_prompt_path)
        generated = combine_attempts(generated, retried)
    if translation is None:
        return generated
    return add_translation(generated, search_question, translation)
