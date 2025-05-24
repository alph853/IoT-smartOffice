from pydantic import BaseModel


class Office(BaseModel):
    id: int | None = None
    room: str | None = None
    building: str | None = None
    description: str | None = None
    name: str

