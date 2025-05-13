#!/usr/bin/env python3
"""
Provision multiple devices via a ThingsBoard gateway using TBGatewayMqttClient.
"""

import logging
from time import sleep, time
from tb_gateway_mqtt import TBGatewayMqttClient

# Configure logging (optional)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Gateway connection parameters
THINGSBOARD_HOST = 'app.coreiot.io'      # or your TB server hostname
GATEWAY_TOKEN      = 'g316u7decaqvzze7kbe1'

# List of device names to provision
DEVICE_NAMES = [
    'TemperatureSensor-01',
    'HumiditySensor-02',
]

def main():
    # 1. Initialize and connect the gateway client
    gateway = TBGatewayMqttClient(THINGSBOARD_HOST, username=GATEWAY_TOKEN)
    gateway.connect()  # ← establishes the MQTT connection :contentReference[oaicite:5]{index=5}

    # 2. Loop through device names and provision each
    for device in DEVICE_NAMES:
        logging.info(f'Provisioning device: {device}')
        gateway.gw_connect_device(device)  # ← publishes to v1/gateway/connect :contentReference[oaicite:6]{index=6}

        attrs = {"firmwareVersion": "1.0.0", "location": "Warehouse"}
        gateway.gw_send_attributes(device, attrs)  # :contentReference[oaicite:7]{index=7}

        telemetry = {"ts": int(round(time() * 1000)), "values": {"temperature": 23.5}}
        gateway.gw_send_telemetry(device, telemetry)  # :contentReference[oaicite:8]{index=8}

        gateway.gw_disconnect_device(device)  # ← publishes to v1/gateway/disconnect :contentReference[oaicite:9]{index=9}
        sleep(0.5)

    # 3. Disconnect the gateway itself
    gateway.disconnect()  # ← closes the MQTT connection :contentReference[oaicite:10]{index=10}
    logging.info('All devices provisioned and gateway disconnected.')




if __name__ == '__main__':
    main()
