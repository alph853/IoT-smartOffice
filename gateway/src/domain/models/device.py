from pydantic import BaseModel


class Sensor(BaseModel):
    name: str
    description: str
    unit: str
    type: str


class Actuator(BaseModel):
    name: str
    description: str
    type: str
