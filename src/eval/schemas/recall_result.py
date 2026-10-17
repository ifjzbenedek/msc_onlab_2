from pydantic import BaseModel


class RecallResult(BaseModel):
    text: dict[int, float]
    any_section: dict[int, float]
    all_sections: dict[int, float]
