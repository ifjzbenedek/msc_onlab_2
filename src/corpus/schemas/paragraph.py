from pydantic import BaseModel


class Paragraph(BaseModel):
    text: str
    page_start: int
    page_end: int
