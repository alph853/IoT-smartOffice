#!/usr/bin/env python3
"""
Provision multiple devices via a ThingsBoard gateway using TBGatewayMqttClient.
"""

import logging
from time import sleep, time
from tb_gateway_mqtt import TBGatewayMqttClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


THINGSBOARD_HOST = 'app.coreiot.io'
GATEWAY_TOKEN      = 'g316u7decaqvzze7kbe1'
DEVICE_NAMES = [
    'TemperatureSensor-01',
    'HumiditySensor-02',
]


def on_message(client, userdata, message):
    print(f"Received message on topic: {message.topic}")
    print(f"Message payload: {message.payload}")


gateway = TBGatewayMqttClient(THINGSBOARD_HOST, username=GATEWAY_TOKEN)
gateway.connect()  # ← establishes the MQTT connection :contentReference[oaicite:5]{index=5}
connected = False

try:
    while True:
        if connected:
            sleep(2)
            continue

        for device in DEVICE_NAMES:
            logging.info(f'Provisioning device: {device}')
            gateway.gw_subscribe_to_all_attributes(device)

            gateway.gw_connect_device(device)  # ← publishes to v1/gateway/connect :contentReference[oaicite:6]{index=6}

            attrs = {"firmwareVersion": "1.0.0", "location": "Warehouse"}
            gateway.gw_send_attributes(device, attrs)  # :contentReference[oaicite:7]{index=7}

            telemetry = {"ts": int(round(time() * 1000)), "values": {"temperature": 23.5}}
            gateway.gw_send_telemetry(device, telemetry)  # :contentReference[oaicite:8]{index=8}

            sleep(0.5)
        connected = True
        logging.info('All devices provisioned and gateway disconnected.')
except KeyboardInterrupt:
    logging.info('Keyboard interrupt')
    gateway.gw_disconnect_device(device)  # ← publishes to v1/gateway/disconnect :contentReference[oaicite:9]{index=9}
    gateway.disconnect()

