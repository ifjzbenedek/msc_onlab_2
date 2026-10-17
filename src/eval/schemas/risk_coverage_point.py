from pydantic import BaseModel


class RiskCoveragePoint(BaseModel):
    threshold: float
    coverage: float
    precision: float
