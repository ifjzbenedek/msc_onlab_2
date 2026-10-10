from pydantic import BaseModel


class Citation(BaseModel):
    document: str
    section: str
    text: str
    paragraph: str | None = None
