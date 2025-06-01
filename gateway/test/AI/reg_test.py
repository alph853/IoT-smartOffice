#!/usr/bin/env python3
import json
import time
import paho.mqtt.client as mqtt
import uuid

# MQTT broker settings
BROKER_URL = "192.168.1.196"
BROKER_PORT = 1883

# Topics
REQUEST_TOPIC = "gateway/register/request"
TELEMETRY_TOPIC = "gateway/telemetry/{device_id}"

# Device registration payload
device_mac = f"AA:BB:CC:{uuid.uuid4().hex[:6].upper()}"
# device_mac = f"AA:BB:CC"
# device_mac = f"CC:BA:97:0D:E2:44"
device_id = None

# Sample device registration payload
registration_payload = {
    "name": "Test Device Another Office",
    "mac_addr": device_mac,
    "fw_version": "1.0.0",
    "model": "Test_Model",
    "description": "A test device for registration",
    "office_id": 3,
    "sensors": [
        {
            "name": "DHT20",
            "description": "Measures ambient temperature",
            "type": "dht20"
        },
    ],
    "actuators": [
        {
            "name": "LED Light",
            "type": "rgb"
        },
        {
            "name": "Fan",
            "type": "fan"
        }
    ]
}

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the response topic using wildcard
    client.subscribe(f"gateway/register/response/{device_mac.replace(':', '')}")

    # Publish the registration request
    print("Publishing device registration request...")
    client.publish(
        REQUEST_TOPIC,
        json.dumps(registration_payload),
        qos=1
    )
    print(f"Request published for device: {device_mac}")

def on_message(client, userdata, msg):
    global device_id
    print(f"Received message on topic: {msg.topic}")
    try:
        payload = msg.payload.decode()
        payload = json.loads(payload)

        if msg.topic.startswith(f"gateway/register/response/{device_mac.replace(':', '')}"):
            device_id = payload.get("device_id")
            print(f"Device ID: {device_id}")
            # Subscribe to control commands after getting device_id
            client.subscribe(f"gateway/control/commands/{device_id}")
            return

        if device_id and msg.topic.startswith(f"gateway/control/commands/{device_id}"):
            print(f"Control command: {payload}")
            client.publish(
                f"gateway/control/response/{device_id}",
                json.dumps({"status": "success", "request_id": payload.get("request_id")}),
                qos=1
            )
        else:
            print(f"Error: {payload}")
    except Exception as e:
        print(f"Error: {e}")

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
print(f"Connecting to MQTT broker at {BROKER_URL}:{BROKER_PORT}...")
client.connect(BROKER_URL, BROKER_PORT, 60)
client.loop_start()


temp = 20
humidity = 50
# Start the loop
try:
    while True:
        if not device_id:
            time.sleep(5)
            continue

        client.publish(
            TELEMETRY_TOPIC.format(device_id=device_id),
            json.dumps({"temperature": temp, "humidity": humidity}),
            qos=1,
            retain=True
        )
        time.sleep(2)
        temp += 1
        humidity += 1
except KeyboardInterrupt:
    print("Script interrupted by user")
    client.disconnect()