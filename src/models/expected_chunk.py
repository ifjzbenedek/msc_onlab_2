from pydantic import BaseModel


class ExpectedChunk(BaseModel):
    chunk_id: str
    pdf_page: int
    text: str
