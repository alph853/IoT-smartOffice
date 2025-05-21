from pydantic import BaseModel


class RPCResponse(BaseModel):
    status: str
    data: dict | None = None
    request_id: str | None = None
