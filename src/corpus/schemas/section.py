from pydantic import BaseModel

from src.corpus.schemas.text_line import TextLine


class Section(BaseModel):
    label: str
    title: str
    lines: list[TextLine]
