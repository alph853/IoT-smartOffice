import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("sensor/temperature")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} -> {msg.payload.decode()}")

# Test subscriber
def test_subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("host.docker.internal", 1883, 60)
    client.loop_forever()

# Test publisher with various formats
def test_publisher():
    client = mqtt.Client()
    client.connect("host.docker.internal", 1883, 60)
    
    # Test different payload formats
    test_payloads = [
        # Standard format
        {"temperature": 25.5, "humidity": 60.0},
        
        # With device info
        {
            "deviceName": "IoT_Gateway",
            "deviceType": "sensor",
            "temperature": 26.0,
            "humidity": 65.0
        },
        
        # ThingsBoard telemetry format
        {
            "ts": int(time.time() * 1000),
            "values": {
                "temperature": 27.0,
                "humidity": 70.0
            }
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        topic = f"sensor/temperature"
        client.publish(topic, json.dumps(payload), qos=1)
        print(f"Test {i+1} published: {payload}")
        time.sleep(2)
    
    client.disconnect()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sub":
        test_subscriber()
    else:
        test_publisher()
