from pydantic import BaseModel


class Judgment(BaseModel):
    verdict: str
    reason: str
    input_tokens: int
    output_tokens: int
    seconds: float
