from .device_endpoints import router as device_router
from .ws import router as ws_router
from .office_endpoints import router as office_router
from .notification_endpoints import router as notification_router

__all__ = ["device_router", "ws_router", "office_router", "notification_router"]
