#!/usr/bin/env python3
import json
import time
import paho.mqtt.client as mqtt
import uuid
import signal
import sys

# MQTT broker settings
BROKER_URL = "192.168.1.196"
BROKER_PORT = 1883

# Topics
REQUEST_TOPIC = "gateway/register/request"
TELEMETRY_TOPIC = "gateway/telemetry/{device_id}"
LWT_TOPIC = "gateway/lwt"

# Device registration payload
device_mac = f"AA:BB:CC:{uuid.uuid4().hex[:6].upper()}"
# device_mac = f"AA:BB:CC:EE:FF"
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

# Global client reference for signal handler
mqtt_client = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nGraceful shutdown initiated...')
    if mqtt_client:
        # Publish a clean disconnect message before disconnecting
        if device_id:
            mqtt_client.publish(
                f"gateway/status/{device_id}",
                json.dumps({"status": "disconnecting", "reason": "user_shutdown"}),
                qos=1
            )
        mqtt_client.disconnect()
    sys.exit(0)

def force_disconnect():
    """Simulate an unexpected disconnection (triggers LWT)"""
    print("Simulating unexpected disconnection (this will trigger LWT)...")
    if mqtt_client:
        # Force disconnect without proper cleanup to trigger LWT
        mqtt_client.socket().close()
    sys.exit(1)

# MQTT client callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the response topic using original MAC format
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
    global device_id
    print(f"Received message on topic: {msg.topic}")
    try:
        payload = msg.payload.decode()
        payload = json.loads(payload)

        if msg.topic.startswith(f"gateway/register/response/{device_mac}"):
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

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection (rc={rc}). LWT should be triggered.")
    else:
        print("Clean disconnection.")

# Set up MQTT client with LWT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Configure Last Will and Testament (LWT)
# This message will be published automatically by the broker if the client disconnects unexpectedly
lwt_payload = device_mac  # LWT service expects the MAC address as payload
client.will_set(
    topic=LWT_TOPIC,
    payload=lwt_payload,
    qos=1,
    retain=False
)

print(f"LWT configured: Topic={LWT_TOPIC}, Payload={lwt_payload}")

# Set global reference for signal handler
mqtt_client = client

# Set up signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)

# Connect to broker
print(f"Connecting to MQTT broker at {BROKER_URL}:{BROKER_PORT}...")
client.connect(BROKER_URL, BROKER_PORT, 60)
client.loop_start()

print("\nTest commands:")
print("- Press Ctrl+C for graceful shutdown (no LWT)")
print("- Type 'lwt' and press Enter to simulate unexpected disconnection (triggers LWT)")
print("- Type 'error' and press Enter to send error telemetry")
print("- Just press Enter to continue normal operation\n")

temp = 20
humidity = 50
error_mode = False

# Start the loop
try:
    while True:
        if not device_id:
            time.sleep(5)
            continue

        # Check for user input (non-blocking)
        import select
        import sys
        
        if select.select([sys.stdin], [], [], 0.1)[0]:
            user_input = input().strip().lower()
            if user_input == 'lwt':
                force_disconnect()
            elif user_input == 'error':
                error_mode = not error_mode
                print(f"Error mode {'enabled' if error_mode else 'disabled'}")
            elif user_input == 'help':
                print("\nCommands:")
                print("- 'lwt': Trigger Last Will Testament")
                print("- 'error': Toggle error telemetry mode")
                print("- 'help': Show this help")
                print("- Ctrl+C: Graceful shutdown")

        # Prepare telemetry data
        if error_mode:
            telemetry_data = {"temperature": "E", "humidity": "E"}
            print(f"Sending ERROR telemetry: {telemetry_data}")
        else:
            telemetry_data = {"temperature": temp, "humidity": humidity}

        client.publish(
            TELEMETRY_TOPIC.format(device_id=device_id),
            json.dumps(telemetry_data),
            qos=1,
            retain=True
        )
        
        time.sleep(2)
        if not error_mode:
            temp += 1
            humidity += 1
            
except KeyboardInterrupt:
    signal_handler(signal.SIGINT, None)
except Exception as e:
    print(f"Unexpected error: {e}")
    if mqtt_client:
        mqtt_client.disconnect()