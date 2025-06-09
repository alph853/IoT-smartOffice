# IoT Smart Office System

An ESP32 based IoT device for smart office monitoring and control, featuring environmental sensors, actuator control, and MQTT gateway communication.

## Overview

This system provides comprehensive smart office functionality including:
- **Environmental Monitoring**: Temperature, humidity, and light intensity sensing
- **Device Control**: NeoPixel LED lighting, fan control, and status indicators
- **Gateway Communication**: MQTT-based device registration and remote control
- **Real-time Telemetry**: Continuous sensor data transmission
- **Multi-tasking Architecture**: FreeRTOS-based concurrent task execution

## Hardware Specifications

### Pin Configuration
```
LED_PIN         GPIO_NUM_48
LDR_PIN         GPIO_NUM_1
NEO_PIXEL_PIN   GPIO_NUM_6
FAN_PIN         GPIO_NUM_18
SDA_PIN         GPIO_NUM_11
SCL_PIN         GPIO_NUM_12
CAMERA_PIN      GPIO_NUM_0
```

### Sensors & Actuators

#### Sensors
- **DHT20**: Temperature and humidity sensor (I2C interface)
- **LDR-5528**: Light-dependent resistor for luminosity measurement

#### Actuators
- **NeoPixel LED Strip**: 4-LED RGB strip for ambient lighting
- **Mini Fan**: On/off control for air circulation
- **Status LED**: Built-in indicator for system status

## Software Architecture

### Task Structure (FreeRTOS)
```
├── wifiTask              # WiFi connection management
├── connectGatewayTask    # MQTT gateway communication
└── sendTelemetryTask     # Periodic sensor data transmission
```

### Core Components

#### 1. WiFi Management (`wifi_task.cpp`)
- Automatic WiFi connection and reconnection
- Connection status monitoring
- Network failure recovery

#### 2. Gateway Communication (`gateway_client.cpp`)
- MQTT broker connection
- Device registration with gateway
- Command reception and execution
- Telemetry data publishing

#### 3. Sensor Telemetry (`telemetry.cpp`)
- DHT20 temperature/humidity reading
- LDR light intensity measurement
- JSON payload formatting
- Periodic data transmission (5-second intervals)

#### 4. Device Control (`control.cpp`)
- NeoPixel LED strip control
- Fan state management
- RGB color setting for ambiance

## MQTT Communication Protocol

### Topics Structure
```
gateway/register/request
gateway/register/response/{mac_address}
gateway/telemetry/{device_id}
gateway/control/command/{device_id}
gateway/control/response/{device_id}
```

### Message Formats

#### Device Registration
```json
{
  "mac_addr": "AA:BB:CC:DD:EE:FF",
  "fw_version": "1.0.0",
  "model": "Yolo_UNO_S3_AIOT",
  "name": "OhStem Yolo UNO S3 AIoT Board",
  "description": "Smart office IoT device",
  "office_id": "1",
  "sensors": [
    {"name": "DHT20", "unit": "°C, %", "type": "dht20"},
    {"name": "LDR-5528", "unit": "%", "type": "ldr"}
  ],
  "actuators": [
    {"name": "Build-in Status LED", "type": "indicator"},
    {"name": "NeoPixel 4 LED strip", "type": "led4RGB"},
    {"name": "Mini Fan", "type": "fan"}
  ]
}
```

#### Telemetry Data
```json
{
  "temperature": "23.5",
  "humidity": "45.2",
  "luminousity": "0.68"
}
```

#### Control Commands
```json
{
  "method": "setLighting",
  "params": {
    "actuator_id": 1,
    "request_id": "req_123",
    "color": [[255,0,0], [0,255,0], [0,0,255], [255,255,255]]
  }
}
```

## Configuration

### Network Settings
```cpp
// WiFi Configuration
WIFI_SSID = "your_wifi_name"
WIFI_PASSWORD = "your_wifi_password"

// MQTT Gateway
mqttServer = "192.168.1.164"
mqttPort = 1883
```

## Setup Instructions

### Prerequisites
- Arduino IDE or PlatformIO
- ESP32-S3 board support package
- Required libraries (see Dependencies section)

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone <repository_url>
   cd IoT-smartOffice
   ```

2. **Install Dependencies**
   ```cpp
   #include <WiFi.h>
   #include <PubSubClient.h>
   #include <ArduinoJson.h>
   #include <DHT20.h>
   #include <Adafruit_NeoPixel.h>
   ```

3. **Configure Network**
   - Update WiFi credentials in `include/wifi_task.h`
   - Set MQTT broker IP in `include/gateway_client.h`

4. **Hardware Setup**
   - Connect DHT20 sensor to I2C pins (SDA: GPIO11, SCL: GPIO12)
   - Connect LDR to GPIO1
   - Connect NeoPixel strip to GPIO6
   - Connect fan to GPIO18

5. **Upload Firmware**
   - Select ESP32-S3 board in Arduino IDE
   - Compile and upload the code

## API Reference

### Supported Commands

#### Test Command
```json
{"method": "test"}
```

#### Set Lighting
```json
{
  "method": "setLighting",
  "params": {
    "actuator_id": 1,
    "color": [[R,G,B], [R,G,B], [R,G,B], [R,G,B]]
  }
}
```

#### Fan Control
```json
{
  "method": "setFanState",
  "params": {
    "actuator_id": 2,
    "state": true
  }
}
```
