from contextlib import asynccontextmanager
import asyncio
import sys
from loguru import logger
import signal

from .container import Container
from src.config import ConfigUtils


logger.remove()
logger.add(
    sink=sys.stdout,
    format="<level>{level}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>\t{message}</level>"
)


@asynccontextmanager
async def lifespan(container: Container):
    # ------------------------------------------------------------
    logger.info("Starting up...")
    # ------------------------------------------------------------

    broker_ip = ConfigUtils.get_wireless_lan_ip()
    if broker_ip:
        container.config.mosquitto.url.override(broker_ip)
        logger.info(f"Using broker IP via wireless LAN: {broker_ip}")
    else:
        logger.warning("Could not discover LAN IP")
    logger.info(f"Using broker URL: {container.config.mosquitto.url()}:{container.config.mosquitto.port()}")

    # --------------------- Infrastructures ----------------------

    http_client           = container.http_client()
    cache_client          = container.cache_client()
    mqtt_cloud_client     = container.thingsboard_client()
    mqtt_gateway_client   = container.mosquitto_client()
    await http_client.connect()
    await cache_client.connect()
    await mqtt_cloud_client.connect()
    await mqtt_gateway_client.connect()

    # scheduler     = container.scheduler()

    # await scheduler.start()

    # ------------------------- Services -------------------------

    registration_service = container.registration_service()
    telemetry_service    = container.telemetry_service()
    # auto_dispatcher      = container.auto_dispatcher()

    await registration_service.start()
    await telemetry_service.start()

    # --------
    yield
    # --------

    logger.info("Shutting down...")
    try:
        await mqtt_gateway_client.disconnect()
        await mqtt_cloud_client.disconnect()

        await registration_service.stop()
        await telemetry_service.stop()
        logger.info("Gateway shutdown successfully")
    except Exception as e:
        logger.error(f"Error shutting down gateway: {e}")


async def main():
    container = Container()
    container.config.from_json(ConfigUtils.get_config_path("config.json"))

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _on_signal():
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _on_signal)

    async with lifespan(container):
        await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())