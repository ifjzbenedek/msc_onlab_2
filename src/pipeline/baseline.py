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


def answer_from_chunks(
    question: str, ranked: list[tuple[Chunk, float]], retrieval_seconds: float, prompt_path: Path
) -> GeneratedAnswer:
    context_chunks = [chunk for chunk, _ in ranked[:ANSWER_CONTEXT_CHUNK_COUNT]]
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
        confidence=ranked[0][1] if ranked else 0.0,
    )


def generate_answer(system: RetrievalSystem, question: str, prompt_path: Path) -> GeneratedAnswer:
    start = time.perf_counter()
    ranked = retrieve(system, question)
    return answer_from_chunks(question, ranked, time.perf_counter() - start, prompt_path)


