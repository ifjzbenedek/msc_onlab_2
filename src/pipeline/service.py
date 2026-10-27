from functools import cache

import config
from src.corpus.constants import CHUNK_HEADER_FORMAT, DOCUMENT_SHORT_NAMES
from src.corpus.schemas.chunk import Chunk
from src.pipeline.constants import (
    CHUNK_HEADER_SEPARATOR,
    HIGH_RELIABILITY,
    HIGH_RELIABILITY_MIN_CONFIDENCE,
    INCORRECT_DECISION,
    MEDIUM_RELIABILITY,
    RELATED_CHUNK_COUNT,
)
from src.pipeline.critic import answer_with_critic
from src.pipeline.schemas.answer import Answer
from src.pipeline.schemas.citation import Citation
from src.pipeline.schemas.generated_answer import GeneratedAnswer
from src.retrieval.system import RetrievalSystem, load_retrieval_system


def extract_section_title(chunk: Chunk) -> str | None:
    header = chunk.text.partition(CHUNK_HEADER_SEPARATOR)[0]
    header_without_title = CHUNK_HEADER_FORMAT.format(
        document=DOCUMENT_SHORT_NAMES[chunk.document], label=chunk.section, title=""
    ).rstrip()
    if not header.startswith(header_without_title):
        return None
    return header.removeprefix(header_without_title).strip() or None


def build_citation(chunk: Chunk) -> Citation:
    return Citation(
        document=DOCUMENT_SHORT_NAMES[chunk.document],
        section=chunk.section,
        text=chunk.text.partition(CHUNK_HEADER_SEPARATOR)[2],
        title=extract_section_title(chunk),
        paragraph=chunk.paragraph,
    )


def build_citations(system: RetrievalSystem, chunk_ids: list[str]) -> list[Citation]:
    chunks_by_id = {chunk.id: chunk for chunk in system.chunks}
    return [build_citation(chunks_by_id[chunk_id]) for chunk_id in chunk_ids]


def find_related_chunk_ids(generated: GeneratedAnswer) -> list[str]:
    if generated.crag_decision == INCORRECT_DECISION:
        return []
    if generated.cited_chunk_ids:
        return generated.cited_chunk_ids
    return [retrieved.chunk_id for retrieved in generated.retrieved_chunks[:RELATED_CHUNK_COUNT]]


def to_api_answer(system: RetrievalSystem, generated: GeneratedAnswer) -> Answer:
    if not generated.has_cited_answer():
        return Answer(abstained=True, citations=build_citations(system, find_related_chunk_ids(generated)))
    reliability = HIGH_RELIABILITY if generated.confidence >= HIGH_RELIABILITY_MIN_CONFIDENCE else MEDIUM_RELIABILITY
    return Answer(
        abstained=False,
        text=generated.answer,
        reliability=reliability,
        citations=build_citations(system, generated.cited_chunk_ids),
    )


@cache
def load_default_system() -> RetrievalSystem:
    return load_retrieval_system(
        config.CHUNKS_PATH, config.DENSE_INDEX_PATH, config.EMBED_MODEL, config.RERANK_MODEL, config.RERANK_SCORES_PATH
    )


def answer_question(question: str) -> Answer:
    system = load_default_system()
    generated = answer_with_critic(system, question, config.ANSWER_PROMPT_PATH, config.CRITIC_PROMPT_PATH)
    return to_api_answer(system, generated)
