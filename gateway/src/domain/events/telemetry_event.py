from pydantic import BaseModel


class TelemetryEvent(BaseModel):
    id: str
    timestamp: int
    data: dict
