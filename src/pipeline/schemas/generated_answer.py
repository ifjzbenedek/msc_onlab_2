from pydantic import BaseModel

from src.pipeline.schemas.retrieved_chunk import RetrievedChunk


class GeneratedAnswer(BaseModel):
    question: str
    answerable: bool
    answer: str
    cited_chunk_ids: list[str]
    retrieved_chunks: list[RetrievedChunk]
    retrieval_seconds: float
    llm_calls: int
    input_tokens: int
    output_tokens: int
    llm_seconds: float
    confidence: float = 0.0
    crag_decision: str | None = None
    expansions: int = 0
    critic_support: str | None = None
