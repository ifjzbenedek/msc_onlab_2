from pydantic import BaseModel


class BSetItem(BaseModel):
    id: str
    question: str
    language: str
    answerable: bool
    gold_chunk_ids: list[str]
    gold_sections: list[str]
    reference_answer: str | None = None
    note: str = ""
