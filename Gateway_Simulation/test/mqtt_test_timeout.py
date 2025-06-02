import paho.mqtt.client as mqtt
import json
import time
import random
import threading

class MQTTPublisher:
    def __init__(self, host="host.docker.internal", port=1883):
        self.host = host
        self.port = port
        self.client = mqtt.Client()
        self.connected = False
        self.publish_result = None
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✓ Connected to MQTT broker at {self.host}:{self.port}")
            self.connected = True
        else:
            print(f"✗ Failed to connect to MQTT broker. Return code: {rc}")
            self.connected = False
    
    def on_publish(self, client, userdata, mid):
        print(f"✓ Message {mid} published successfully")
        self.publish_result = True
    
    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected from MQTT broker. Return code: {rc}")
        self.connected = False
    
    def connect_with_timeout(self, timeout=5):
        """Connect to MQTT broker with timeout"""
        print(f"Connecting to MQTT broker {self.host}:{self.port}...")
        
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            
            # Wait for connection with timeout
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                return True
            else:
                print(f"✗ Connection timeout after {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def publish_sensor_data(self, timeout=5):
        """Publish sensor data with timeout"""
        if not self.connected:
            print("✗ Not connected to MQTT broker")
            return False
        
        # Generate random sensor data
        temperature = round(random.uniform(20.0, 30.0), 2)
        humidity = round(random.uniform(40.0, 80.0), 2)
        
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": int(time.time() * 1000)
        }
        
        print(f"Publishing: {json.dumps(payload)}")
        
        try:
            self.publish_result = None
            result = self.client.publish("v1/devices/me/telemetry", json.dumps(payload), qos=1)
            
            # Wait for publish confirmation with timeout
            start_time = time.time()
            while self.publish_result is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.publish_result:
                return True
            else:
                print(f"✗ Publish timeout after {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"✗ Publish error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    print("=== MQTT Publisher with Timeout ===")
    
    publisher = MQTTPublisher()
    
    # Try to connect
    if not publisher.connect_with_timeout(timeout=10):
        print("Failed to connect to MQTT broker. Exiting...")
        return
    
    # Publish 3 messages
    success_count = 0
    for i in range(3):
        print(f"\n--- Publishing message {i+1}/3 ---")
        
        if publisher.publish_sensor_data(timeout=10):
            success_count += 1
            print("✓ Message published successfully")
        else:
            print("✗ Failed to publish message")
        
        if i < 2:  # Don't wait after last message
            print("Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n=== Summary ===")
    print(f"Successfully published {success_count}/3 messages")
    
    # Disconnect
    publisher.disconnect()
    print("Disconnected from MQTT broker")

if __name__ == "__main__":
    main()
