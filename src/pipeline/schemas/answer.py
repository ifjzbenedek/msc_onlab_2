from typing import Literal

from pydantic import BaseModel, Field

from src.pipeline.schemas.citation import Citation


class Answer(BaseModel):
    abstained: bool
    text: str | None = None
    reliability: Literal["high", "medium"] | None = None
    citations: list[Citation] = Field(default_factory=list)
