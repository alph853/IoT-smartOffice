from pydantic import BaseModel


class ControlResponseEvent(BaseModel):
    id: str
    timestamp: int
    data: dict

class ControlCommandEvent(BaseModel):
    id: str
    timestamp: int
    data: dict
