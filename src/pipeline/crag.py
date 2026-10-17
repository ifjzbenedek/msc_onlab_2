import time
from pathlib import Path
from typing import NamedTuple

from src.corpus.schemas.chunk import Chunk
from src.pipeline.baseline import answer_from_chunks
from src.pipeline.constants import (
    AMBIGUOUS_DECISION,
    CORRECT_DECISION,
    CRAG_CORRECT_THRESHOLD,
    CRAG_INCORRECT_THRESHOLD,
    EXPANDED_CANDIDATE_COUNTS,
    INCORRECT_DECISION,
)
from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.pipeline.schemas.retrieved_chunk import RetrievedChunk
from src.retrieval.system import RetrievalSystem, retrieve


class CragRetrieval(NamedTuple):
    ranked: list[tuple[Chunk, float]]
    decision: str
    expansions: int


def find_top_score(ranked: list[tuple[Chunk, float]]) -> float:
    return ranked[0][1] if ranked else 0.0


def decide_action(ranked: list[tuple[Chunk, float]]) -> str:
    top_score = find_top_score(ranked)
    if top_score >= CRAG_CORRECT_THRESHOLD:
        return CORRECT_DECISION
    if top_score < CRAG_INCORRECT_THRESHOLD:
        return INCORRECT_DECISION
    return AMBIGUOUS_DECISION


def retrieve_with_crag(system: RetrievalSystem, question: str) -> CragRetrieval:
    ranked = retrieve(system, question)
    decision = decide_action(ranked)
    expansions = 0
    for candidate_count in EXPANDED_CANDIDATE_COUNTS:
        if decision == CORRECT_DECISION:
            break
        ranked = retrieve(system, question, candidate_count)
        decision = decide_action(ranked)
        expansions += 1
    return CragRetrieval(ranked=ranked, decision=decision, expansions=expansions)


def build_abstention(question: str, retrieval: CragRetrieval, retrieval_seconds: float) -> GeneratedAnswer:
    return GeneratedAnswer(
        question=question,
        answerable=False,
        answer="",
        cited_chunk_ids=[],
        retrieved_chunks=[RetrievedChunk(chunk_id=chunk.id, score=score) for chunk, score in retrieval.ranked],
        retrieval_seconds=retrieval_seconds,
        llm_calls=0,
        input_tokens=0,
        output_tokens=0,
        llm_seconds=0.0,
        confidence=find_top_score(retrieval.ranked),
        crag_decision=retrieval.decision,
        expansions=retrieval.expansions,
    )


def answer_with_crag(system: RetrievalSystem, question: str, prompt_path: Path) -> GeneratedAnswer:
    start = time.perf_counter()
    retrieval = retrieve_with_crag(system, question)
    retrieval_seconds = time.perf_counter() - start
    if retrieval.decision == INCORRECT_DECISION:
        return build_abstention(question, retrieval, retrieval_seconds)
    generated = answer_from_chunks(question, retrieval.ranked, retrieval_seconds, prompt_path)
    return generated.model_copy(update={"crag_decision": retrieval.decision, "expansions": retrieval.expansions})
