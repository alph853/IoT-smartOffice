from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import uvicorn

from app.api.routers import *
from app.services import *
from app.infra.event_bus import InProcEventBus
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres import *
from app.infra.aiohttp import *
from app.infra.thingsboard import *
from app.config import Config


logger.remove()
logger.add(
    sink=sys.stdout,
    format="<level>{level}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>\t{message}</level>"
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # ---------------------------------------------------------------
    # ------------------ Initialize Infrastructure ------------------
    # ---------------------------------------------------------------

    config = Config("config.json")
    logger.info(f"Server started at {Config.get_wireless_lan_ip()}")

    db = PostgreSQLConnection(
        host=config.postgres.host,
        port=config.postgres.port,
        user=config.postgres.user,
        password=config.postgres.password,
        database=config.postgres.database
    )
    await db.initialize()

    http_client          = AiohttpClient()
    event_bus            = InProcEventBus()
    thingsboard_client   = ThingsboardClient(event_bus,
        http_client = http_client,
        broker_url  = config.thingsboard.url,
        broker_port = config.thingsboard.port,
        client_id   = config.thingsboard.client_id,
        username    = config.thingsboard.username,
        password    = config.thingsboard.password,
        api         = config.thingsboard.api,
        device_id   = config.thingsboard.device_id,
        device_name = config.thingsboard.device_name
    )

    await http_client.connect()
    await thingsboard_client.connect()

    app.state.http_client          = http_client
    app.state.event_bus            = event_bus
    app.state.thingsboard_client   = thingsboard_client

    # ---------------------------------------------------------------
    # ------------------- Initialize Repositories -------------------
    # ---------------------------------------------------------------

    device_repository       = PostgresDeviceRepository(db)
    notification_repository = PostgresNotificationRepository(db)
    office_repository       = PostgresOfficeRepository(db)


    # ---------------------------------------------------------------
    # --------------------- Initialize services ---------------------
    # ---------------------------------------------------------------

    device_service          = DeviceService(event_bus, device_repository, thingsboard_client)
    broadcast_service       = BroadcastService(event_bus, thingsboard_client)
    notification_service    = NotificationService(event_bus, notification_repository, office_repository)

    app.state.device_service       = device_service
    app.state.broadcast_service    = broadcast_service
    app.state.notification_service = notification_service

    # ---------------------------------------------------------------
    # ------------------- Start background tasks --------------------
    # ---------------------------------------------------------------

    await device_service.start()
    await notification_service.start()
    await broadcast_service.start()

    yield


    # ----------------- Shutdown -----------------
    await device_service.stop()
    await notification_service.stop()
    await broadcast_service.stop()

    await thingsboard_client.disconnect()
    await http_client.disconnect()


app = FastAPI(title="YoloFarm API", lifespan=lifespan)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Welcome to YoloFarm API", "version": "1.0.0"}


app.include_router(device_router)
app.include_router(ws_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
