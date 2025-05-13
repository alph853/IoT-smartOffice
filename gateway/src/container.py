from dependency_injector import containers, providers

from src.infra.event_bus import InProcEventBus
from src.infra.mqtt import ThingsboardClient, MosquittoListener
from src.infra.scheduler import APScheduler
from src.services.registration import RegistrationService
from src.services.telemetry import TelemetryService
from src.services.auto_dispatcher import AutoDispatcherService

from src.config import ConfigUtils
from src.domain.models import MqttTopic
from src.infra.mqtt import MosquittoClient, MosquittoListener, ThingsboardClient, ThingsboardListener
from src.infra.http import HttpClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    gateway_topics = providers.Singleton(
        ConfigUtils.get_mqtt_topics,
        config.gateway_topics,
    )
    thingsboard_topics   = providers.Singleton(
        ConfigUtils.get_mqtt_topics,
        config.thingsboard_topics,
    )

    event_bus   = providers.Singleton(InProcEventBus)
    thingsboard_client = providers.Singleton(
        ThingsboardClient,
        broker_url  = config.thingsboard.url,
        broker_port = config.thingsboard.port.as_int(),
        password    = config.thingsboard.password,
        username    = config.thingsboard.username,
        client_id   = config.thingsboard.client_id,
        event_bus   = event_bus,
        topics      = thingsboard_topics,
    )
    mosquitto_client = providers.Singleton(
        MosquittoClient,
        broker_url  = config.mosquitto.url,
        broker_port = config.mosquitto.port.as_int(),
        event_bus   = event_bus,
        topics      = gateway_topics,
    )
    http_client = providers.Singleton(
        HttpClient,
    )
    thingsboard_listener = providers.Singleton(
        ThingsboardListener,
        msg_generator = thingsboard_client.provided.messages,
        event_bus     = event_bus,
    )
    mosquitto_listener = providers.Singleton(
        MosquittoListener,
        msg_generator = mosquitto_client.provided.messages,
        event_bus     = event_bus,
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
    )
    telemetry_service = providers.Singleton(
        TelemetryService,
        cloud_client=thingsboard_client,
        event_bus=event_bus,
    )
    # auto_dispatcher = providers.Singleton(
    #     AutoDispatcherService,
    #     event_bus=event_bus,
    #     rules=config.auto_rules,
    # )
