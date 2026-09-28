from pydantic import BaseModel, Field


class ExpectedChunk(BaseModel):
    chunk_id: str
    pdf_page: int
    text: str
    spanned_pages: list[int] = Field(default_factory=list)
