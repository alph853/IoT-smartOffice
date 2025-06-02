import paho.mqtt.client as mqtt
import json
import time
import random

class SensorDevice:
    def __init__(self, device_id, host="localhost", port=1883):
        self.device_id = device_id
        self.host = host
        self.port = port
        self.client = mqtt.Client(client_id=f"sensor_{device_id}")
        print(f"[DEBUG] Initializing SensorDevice with client_id=sensor_{device_id}, host={host}, port={port}")
        self.connected = False
        self.publish_result = None
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"[DEBUG] on_connect called for client_id={client._client_id.decode()} with rc={rc}")
        if rc == 0:
            print(f"✓ Device {self.device_id} connected to Mosquitto at {self.host}:{self.port}")
            self.connected = True
        else:
            print(f"✗ Device {self.device_id} failed to connect. Return code: {rc}")
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized",
                7: "Connection refused - no route to host or port closed"
            }
            print(f"Error meaning: {error_messages.get(rc, 'Unknown error')}")
            self.connected = False
    
    def on_publish(self, client, userdata, mid):
        print(f"✓ Device {self.device_id} - Message {mid} published successfully")
        self.publish_result = True
    
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Device {self.device_id} - Unexpected disconnection. Return code: {rc}")
        else:
            print(f"Device {self.device_id} - Disconnected from Mosquitto")
        self.connected = False
    
    def connect_with_timeout(self, timeout=10):
        """Connect to Mosquitto broker with timeout"""
        print(f"Device {self.device_id} connecting to Mosquitto at {self.host}:{self.port}...")
        
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
                print(f"✗ Device {self.device_id} - Connection timeout after {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"✗ Device {self.device_id} - Connection error: {e}")
            return False
    
    def publish_telemetry(self, temperature, humidity, timeout=10):
        """Publish sensor data via Gateway topic"""
        if not self.connected:
            print(f"✗ Device {self.device_id} - Not connected to Mosquitto")
            return False
        
        # Create telemetry payload for ThingsBoard Gateway
        payload = {
            "deviceName": f"Sensor_{self.device_id}",
            "deviceType": "TemperatureHumidity", 
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": int(time.time() * 1000)
        }
        
        print(f"Device {self.device_id} publishing: {json.dumps(payload)}")
        
        try:
            self.publish_result = None
            # Publish to the topic that Gateway subscribes to
            result = self.client.publish("v1/devices/me/telemetry", json.dumps(payload), qos=0)
            
            # Wait for publish confirmation with timeout
            start_time = time.time()
            while self.publish_result is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.publish_result:
                return True
            else:
                print(f"✗ Device {self.device_id} - Publish timeout after {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"✗ Device {self.device_id} - Publish error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Mosquitto"""
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    print("=== IoT Sensor Network via Gateway ===")
    print("Sensors → Mosquitto MQTT Broker → ThingsBoard Gateway → ThingsBoard Platform")
    print()
    
    # Create multiple sensor devices
    sensors = [
        SensorDevice("001", host="host.docker.internal"),
        SensorDevice("002", host="host.docker.internal"),
        SensorDevice("003", host="host.docker.internal"),
    ]
    
    # Connect all sensors
    connected_sensors = []
    for sensor in sensors:
        if sensor.connect_with_timeout(timeout=10):
            connected_sensors.append(sensor)
        else:
            print(f"Failed to connect sensor {sensor.device_id}")
    
    if not connected_sensors:
        print("No sensors connected. Exiting...")
        return
        
    print(f"\n✓ {len(connected_sensors)} sensors connected successfully")
    
    # Simulate sensor readings
    rounds = 5
    for round_num in range(rounds):
        print(f"\n=== Round {round_num + 1}/{rounds} ===")
        
        for sensor in connected_sensors:
            # Generate realistic sensor data
            if sensor.device_id == "001":  # Room 1 - warmer
                temp = round(random.uniform(22.0, 28.0), 2)
                humidity = round(random.uniform(45.0, 65.0), 2)
            elif sensor.device_id == "002":  # Room 2 - cooler
                temp = round(random.uniform(18.0, 24.0), 2)
                humidity = round(random.uniform(40.0, 60.0), 2)
            else:  # Warehouse - more variable
                temp = round(random.uniform(15.0, 35.0), 2)
                humidity = round(random.uniform(30.0, 85.0), 2)
            
            print(f"Sensor {sensor.device_id}: {temp}°C, {humidity}%")
            sensor.publish_telemetry(temp, humidity)
            
            time.sleep(1)  # Small delay between sensors
        
        if round_num < rounds - 1:
            print("Waiting 10 seconds before next round...")
            time.sleep(10)
    
    print(f"\n=== Data Collection Complete ===")
    print("Check ThingsBoard Gateway logs for data processing:")
    print("docker-compose logs -f tb-gateway")
    print()
    print("Check ThingsBoard platform dashboard:")
    print("1. Go to app.coreiot.io")
    print("2. Navigate to Devices")  
    print("3. Check 'Latest telemetry' for temperature/humidity data")
    
    # Disconnect all sensors
    for sensor in connected_sensors:
        sensor.disconnect()
    
    print("\nAll sensors disconnected")

if __name__ == "__main__":
    main()
