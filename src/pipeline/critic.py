from pathlib import Path

from src.corpus.schemas.chunk import Chunk
from src.llm.cli_client import ask_model_cached_with_usage
from src.pipeline.baseline import format_context
from src.pipeline.constants import (
    CRITIC_CONFIDENCE_FACTORS,
    CRITIC_SCHEMA,
    CRITIC_USER_PROMPT_TEMPLATE,
    LLM_CALLS_PER_CRITIC,
    NO_SUPPORT,
)
from src.pipeline.crag import answer_with_crag
from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.retrieval.system import RetrievalSystem


def build_critic_prompt(question: str, answer: str, cited_chunks: list[Chunk]) -> str:
    return CRITIC_USER_PROMPT_TEMPLATE.format(question=question, answer=answer, context=format_context(cited_chunks))


def answer_with_critic(
    system: RetrievalSystem, question: str, answer_prompt_path: Path, critic_prompt_path: Path
) -> GeneratedAnswer:
    generated = answer_with_crag(system, question, answer_prompt_path)
    if not generated.answerable or not generated.cited_chunk_ids:
        return generated
    chunks_by_id = {chunk.id: chunk for chunk in system.chunks}
    cited_chunks = [chunks_by_id[chunk_id] for chunk_id in generated.cited_chunk_ids]
    response, _ = ask_model_cached_with_usage(
        critic_prompt_path, build_critic_prompt(question, generated.answer, cited_chunks), CRITIC_SCHEMA
    )
    support = response.output["support"]
    return generated.model_copy(
        update={
            "answerable": support != NO_SUPPORT,
            "critic_support": support,
            "confidence": generated.confidence * CRITIC_CONFIDENCE_FACTORS[support],
            "llm_calls": generated.llm_calls + LLM_CALLS_PER_CRITIC,
            "input_tokens": generated.input_tokens + response.input_tokens,
            "output_tokens": generated.output_tokens + response.output_tokens,
            "llm_seconds": generated.llm_seconds + response.seconds,
        }
    )
