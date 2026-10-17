from pydantic import BaseModel


class Citation(BaseModel):
    document: str
    section: str
    text: str
    title: str | None = None
    paragraph: str | None = None
