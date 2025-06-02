import paho.mqtt.publish as publish
import json
import time
import random

def publish_sensor_data():
    # Generate random sensor data
    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(40.0, 80.0), 2)
    
    # Create payload
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": int(time.time() * 1000)  # milliseconds
    }
    
    try:
        publish.single(
            topic="v1/devices/me/telemetry",
            payload=json.dumps(payload),
            hostname="host.docker.internal",
            port=1883,
            qos=1  # Add QoS level
        )
        print(f"Published: {payload}")
    except Exception as e:
        print(f"Error publishing: {e}")

if __name__ == "__main__":
    # Publish sensor data every 5 seconds
    for i in range(10):
        publish_sensor_data()
        time.sleep(5)