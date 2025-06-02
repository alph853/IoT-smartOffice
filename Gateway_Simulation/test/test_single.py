# Test single publish
import paho.mqtt.publish as publish
import json

payload = {
    "temperature": 25.5,
    "humidity": 60.0
}

try:
    publish.single(
        topic="v1/devices/me/telemetry",
        payload=json.dumps(payload),
        hostname="host.docker.internal",
        port=1883,
        qos=1
    )
    print(f"✅ Successfully published: {payload}")
except Exception as e:
    print(f"❌ Error: {e}")
