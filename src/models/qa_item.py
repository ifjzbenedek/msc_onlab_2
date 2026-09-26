from typing import Literal

from pydantic import BaseModel

from src.models.expected_chunk import ExpectedChunk


class QAItem(BaseModel):
    id: str
    question: str
    source_document: str
    difficulty: Literal["easy", "medium", "hard"]
    expected_pdf_pages: list[int]
    expected_chunks: list[ExpectedChunk]
    reference_answer: str | None = None
