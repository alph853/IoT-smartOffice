import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routers import *
from app.services import *
from app.infra.event_bus import InProcEventBus
from app.infra.postgres.db import PostgreSQLConnection
from app.infra.postgres import *
from app.infra.aiohttp import *
from app.infra.thingsboard import *
from app.config import Config


@asynccontextmanager
async def lifespan(app: FastAPI):

    # ---------------------------------------------------------------
    # ------------------ Initialize Infrastructure ------------------
    # ---------------------------------------------------------------

    config = Config("config.json")
    print(f"Server started at {Config.get_wireless_lan_ip()}")

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
    thingsboard_client   = ThingsBoardClient(event_bus)

    await http_client.connect()
    await thingsboard_client.connect()

    app.state.http_client          = http_client
    app.state.event_bus            = event_bus
    app.state.thingsboard_client   = thingsboard_client

    # ---------------------------------------------------------------
    # ------------------- Initialize Repositories -------------------
    # ---------------------------------------------------------------

    device_repository = PostgresDeviceRepository(db)


    # ---------------------------------------------------------------
    # --------------------- Initialize services ---------------------
    # ---------------------------------------------------------------

    device_service = DeviceService(device_repository)

    app.state.device_service = device_service

    # ---------------------------------------------------------------
    # ------------------- Start background tasks --------------------
    # ---------------------------------------------------------------

    device_service.start()


    yield


    # ----------------- Shutdown -----------------
    print("Cleaning up services...")
    device_service.stop()
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

