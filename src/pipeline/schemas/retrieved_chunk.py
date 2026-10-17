from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: str
    score: float
