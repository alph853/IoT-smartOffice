import paho.mqtt.publish as publish
import json
import time
import random

def publish_sensor_data():
    print("Starting publish_sensor_data function...")
    
    # Generate random sensor data
    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(40.0, 80.0), 2)
    
    print(f"Generated data - Temperature: {temperature}°C, Humidity: {humidity}%")
    
    # Create payload
    payload = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": int(time.time() * 1000)  # milliseconds
    }
    
    print(f"Payload: {json.dumps(payload)}")
    
    try:
        print("Attempting to publish to MQTT...")
        publish.single(
            topic="v1/devices/me/telemetry",
            payload=json.dumps(payload),
            hostname="host.docker.internal",
            port=1883,
            qos=1  # Add QoS level
        )
        print(f"✓ Successfully published: {payload}")
        return True
    except Exception as e:
        print(f"✗ Error publishing: {e}")
        return False

if __name__ == "__main__":
    print("=== MQTT Debug Publisher ===")
    print("Publishing sensor data every 5 seconds for 3 iterations...")
    
    # Publish sensor data for 3 iterations
    for i in range(3):
        print(f"\n--- Iteration {i+1} ---")
        success = publish_sensor_data()
        if success:
            print("Waiting 5 seconds...")
            time.sleep(5)
        else:
            print("Failed to publish, stopping...")
            break
    
    print("\n=== Debug session complete ===")
