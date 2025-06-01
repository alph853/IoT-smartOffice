import asyncio
from dependency_injector import containers, providers

from src.services import *

from src.infra.event_bus import InProcEventBus
from src.infra.mqtt import ThingsboardClient, MosquittoClient
from src.infra.scheduler import APScheduler
from src.infra.http import HttpClient
from src.infra.redis import RedisCacheClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    loop   = providers.Singleton(asyncio.get_event_loop)

    event_bus   = providers.Singleton(InProcEventBus)

    http_client = providers.Singleton(
        HttpClient,
        url=config.backend.url,
        api=config.backend.api,
    )
    cache_client = providers.Singleton(
        RedisCacheClient,
        host=config.redis.host,
        port=config.redis.port.as_int(),
        db=config.redis.db.as_int(),
        http_client=http_client,
        event_bus=event_bus,
    )
    mosquitto_client = providers.Singleton(
        MosquittoClient,
        broker_url   = config.mosquitto.url,
        broker_port  = config.mosquitto.port.as_int(),
        event_bus    = event_bus,
        cache_client = cache_client,
        topics       = config.mosquitto.topics,
    )
    thingsboard_client = providers.Singleton(
        ThingsboardClient,
        broker_url   = config.thingsboard.url,
        broker_port  = config.thingsboard.port.as_int(),
        password     = config.thingsboard.password,
        username     = config.thingsboard.username,
        client_id    = config.thingsboard.client_id,
        device_name  = config.thingsboard.device_name,
        event_bus    = event_bus,
        topics       = config.thingsboard.topics,
        loop         = loop,
    )

    scheduler = providers.Singleton(
        APScheduler,
        event_bus = event_bus,
        schedules = config.schedules,
    )

    registration_service = providers.Singleton(
        RegistrationService,
        gw_client=mosquitto_client,
        cloud_client=thingsboard_client,
        event_bus=event_bus,
        http_client=http_client,
        cache_client=cache_client,
        gateway_id=config.gateway.id,
    )
    telemetry_service = providers.Singleton(
        TelemetryService,
        event_bus=event_bus,
        cache_client=cache_client,
        cloud_client=thingsboard_client,
        http_client=http_client,
    )
    control_service = providers.Singleton(
        ControlService,
        event_bus=event_bus,
        gw_client=mosquitto_client,
        cache_client=cache_client,
        cloud_client=thingsboard_client,
    )
    lwt_service = providers.Singleton(
        LWTService,
        event_bus=event_bus,
        cache_client=cache_client,
        http_client=http_client,
        mqtt_gateway_client=mosquitto_client,
    )
    ai_multimedia_service = providers.Singleton(
        AIMultimediaService,
        event_bus=event_bus,
        http_client=http_client,
        cache_client=cache_client,
    )
    # auto_dispatcher = providers.Singleton(
    #     AutoDispatcherService,
    #     event_bus=event_bus,
    #     rules=config.auto_rules,
    # )
