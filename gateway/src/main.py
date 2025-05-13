from contextlib import asynccontextmanager
import asyncio
from loguru import logger
import signal

from .container import Container
from src.config import ConfigUtils


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

    mqtt_cloud_client     = container.thingsboard_client()
    mqtt_gateway_client   = container.mosquitto_client()
    await mqtt_cloud_client.connect()
    await mqtt_gateway_client.connect()

    mqtt_cloud_listener   = container.thingsboard_listener()
    mqtt_gateway_listener = container.mosquitto_listener()
    await mqtt_cloud_listener.start()
    await mqtt_gateway_listener.start()

    # scheduler     = container.scheduler()

    # await scheduler.start()

    # ------------------------- Services -------------------------

    registration_service = container.registration_service()
    telemetry_service    = container.telemetry_service()
    # auto_dispatcher      = container.auto_dispatcher()

    await registration_service.subscribe_events()
    await telemetry_service.subscribe_events()

    # --------
    yield
    # --------

    logger.info("Shutting down...")
    try:
        await mqtt_gateway_client.disconnect()
        await mqtt_cloud_client.disconnect()
        await mqtt_gateway_listener.stop()
        await mqtt_cloud_listener.stop()
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