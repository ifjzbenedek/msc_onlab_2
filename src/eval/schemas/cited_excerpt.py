from pydantic import BaseModel


class CitedExcerpt(BaseModel):
    header: str
    text: str
