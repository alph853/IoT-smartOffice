#!/usr/bin/env python3
import json
import time
import paho.mqtt.client as mqtt
import uuid

# MQTT broker settings
BROKER_URL = "192.168.1.164"
BROKER_PORT = 1883

# Topics
REQUEST_TOPIC = "gateway/register/request"
RESPONSE_TOPIC_TEMPLATE = "gateway/register/response/{device_id}"

# Device registration payload
device_mac = f"AA:BB:CC:{uuid.uuid4().hex[:6].upper()}"


# Sample device registration payload
registration_payload = {
    "name": "Test Device",
    "mac_addr": device_mac,
    "fw_version": "1.0.0",
    "model": "Test_Model",
    "description": "A test device for registration",
    "office_id": 1,
    "sensors": [
        {
            "name": "Temperature Sensor",
            "description": "Measures ambient temperature",
            "unit": "°C",
            "type": "Temperature"
        },
        {
            "name": "Humidity Sensor",
            "description": "Measures relative humidity",
            "unit": "%",
            "type": "Humidity"
        }
    ],
    "actuators": [
        {
            "name": "LED Light",
            "description": "RGB LED indicator",
            "type": "Lighting"
        },
        {
            "name": "Buzzer",
            "description": "Sound notification",
            "type": "Audio"
        }
    ]
}

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the response topic using wildcard
    client.subscribe(f"gateway/register/response/{device_mac}")
    
    # Publish the registration request
    print("Publishing device registration request...")
    client.publish(
        REQUEST_TOPIC,
        json.dumps(registration_payload),
        qos=1
    )
    print(f"Request published for device: {device_mac}")

def on_message(client, userdata, msg):
    print(f"Received message on topic: {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Response payload: {json.dumps(payload, indent=2)}")
    except json.JSONDecodeError:
        print(f"Raw payload: {msg.payload.decode()}")

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
print(f"Connecting to MQTT broker at {BROKER_URL}:{BROKER_PORT}...")
client.connect(BROKER_URL, BROKER_PORT, 60)

# Start the loop
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Script interrupted by user")
    client.disconnect() 