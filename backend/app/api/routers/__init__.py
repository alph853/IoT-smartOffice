from .device_endpoints import router as device_router
from .ws import router as ws_router

__all__ = ["device_router", "ws_router"]
