from pydantic import BaseModel

from src.domain.models import Topic, Sensor, Actuator


class RegisterRequestEvent(BaseModel):
    id: str | None = None
    mac_addr: str
    fw_version: str
    model: str
    name: str
    description: str | None = None
    capabilities: dict[str, list[Sensor | Actuator]]


class InvalidMessageEvent(BaseModel):
    topic: Topic
    payload: str
    error: str


class TestEvent(BaseModel):
    payload: str
