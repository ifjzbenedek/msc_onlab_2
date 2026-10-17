from pydantic import BaseModel


class HealthStatus(BaseModel):
    ready: bool
