from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    document: str
    section: str
    page_start: int
    page_end: int
    text: str
    paragraph: str | None = None
    language: str = "hu"
    version: str | None = None
