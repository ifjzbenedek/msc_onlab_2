import time
from pathlib import Path

from src.corpus.schemas.chunk import Chunk
from src.llm.cli_client import ask_model_cached_with_usage
from src.pipeline.constants import (
    ANSWER_CONTEXT_CHUNK_COUNT,
    ANSWER_SCHEMA,
    ANSWER_USER_PROMPT_TEMPLATE,
    CONTEXT_BLOCK_SEPARATOR,
    CONTEXT_BLOCK_TEMPLATE,
    LLM_CALLS_PER_ANSWER,
)
from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.pipeline.schemas.retrieved_chunk import RetrievedChunk
from src.retrieval.system import RetrievalSystem, retrieve


def format_context(chunks: list[Chunk]) -> str:
    return CONTEXT_BLOCK_SEPARATOR.join(
        CONTEXT_BLOCK_TEMPLATE.format(chunk_id=chunk.id, text=chunk.text) for chunk in chunks
    )


def build_answer_prompt(question: str, chunks: list[Chunk]) -> str:
    return ANSWER_USER_PROMPT_TEMPLATE.format(question=question, context=format_context(chunks))


def answer_from_context(
    question: str,
    context: list[tuple[Chunk, float]],
    ranked: list[tuple[Chunk, float]],
    retrieval_seconds: float,
    prompt_path: Path,
) -> GeneratedAnswer:
    context_chunks = [chunk for chunk, _ in context]
    response, _ = ask_model_cached_with_usage(prompt_path, build_answer_prompt(question, context_chunks), ANSWER_SCHEMA)
    context_ids = {chunk.id for chunk in context_chunks}
    return GeneratedAnswer(
        question=question,
        answerable=response.output["answerable"],
        answer=response.output["answer"],
        cited_chunk_ids=[chunk_id for chunk_id in response.output["cited_chunk_ids"] if chunk_id in context_ids],
        retrieved_chunks=[RetrievedChunk(chunk_id=chunk.id, score=score) for chunk, score in ranked],
        retrieval_seconds=retrieval_seconds,
        llm_calls=LLM_CALLS_PER_ANSWER,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        llm_seconds=response.seconds,
        confidence=context[0][1] if context else 0.0,
    )


def answer_from_chunks(
    question: str, ranked: list[tuple[Chunk, float]], retrieval_seconds: float, prompt_path: Path
) -> GeneratedAnswer:
    return answer_from_context(question, ranked[:ANSWER_CONTEXT_CHUNK_COUNT], ranked, retrieval_seconds, prompt_path)


def add_model_costs(
    generated: GeneratedAnswer, llm_calls: int, input_tokens: int, output_tokens: int, llm_seconds: float
) -> GeneratedAnswer:
    return generated.model_copy(
        update={
            "llm_calls": generated.llm_calls + llm_calls,
            "input_tokens": generated.input_tokens + input_tokens,
            "output_tokens": generated.output_tokens + output_tokens,
            "llm_seconds": generated.llm_seconds + llm_seconds,
        }
    )


def generate_answer(system: RetrievalSystem, question: str, prompt_path: Path) -> GeneratedAnswer:
    start = time.perf_counter()
    ranked = retrieve(system, question)
    return answer_from_chunks(question, ranked, time.perf_counter() - start, prompt_path)


