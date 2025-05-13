from pydantic import BaseModel
from enum import Enum


class Entity(str, Enum):
    DEVICE = "device"
    GATEWAY = "gateway"
    CLOUD = "cloud"


class Topic(str, Enum):
    TEST = "test/topic"
    REGISTER_REQUEST = "gateway/register/request"
    REGISTER_RESPONSE = "gateway/register/response/{device_id}"
    TELEMETRY = "gateway/telemetry/#"
    CONTROL_COMMAND = "gateway/control/commands/{device_id}"
    CONTROL_RESPONSE = "gateway/control/response/#"

    CLOUD_RPC_REQUEST = "v1/devices/me/rpc/request"
    CLOUD_RPC_RESPONSE = "v1/devices/me/rpc/response"
    CLOUD_TELEMETRY = "v1/devices/me/telemetry"


class MqttTopic(BaseModel):
    topic: Topic
    qos: int
    retain: int
    description: str | None = None
    src: Entity
    dst: Entity


