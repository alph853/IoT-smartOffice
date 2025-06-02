import paho.mqtt.publish as publish
import json

# Simple test
payload = {"temperature": 25.5, "humidity": 60.0}

try:
    publish.single(
        topic="v1/devices/me/telemetry",
        payload=json.dumps(payload),
        hostname="host.docker.internal",
        port=1883,
        qos=1
    )
    print(f"✅ Successfully published to v1/devices/me/telemetry: {payload}")
except Exception as e:
    print(f"❌ Error: {e}")
