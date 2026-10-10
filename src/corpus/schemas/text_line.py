from pydantic import BaseModel


class TextLine(BaseModel):
    page: int
    text: str
    is_emphasized: bool
