from pydantic import BaseModel

from src.eval.schemas.cited_excerpt import CitedExcerpt


class ReviewCase(BaseModel):
    id: str
    group: str
    language: str
    question: str
    source: list[str]
    answer: str
    cited: list[CitedExcerpt]
