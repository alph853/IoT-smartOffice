# Smart Office IoT Gateway

An intelligent IoT gateway service that bridges physical IoT devices with the Smart Office backend system. Features advanced AI-powered image processing, device management, and real-time communication capabilities.

## Features

### Core Capabilities
- **Device Registration & Discovery**: Automatic device onboarding and management
- **MQTT Message Routing**: Intelligent message routing and protocol translation
- **Real-time Communication**: Bidirectional device communication with low latency
- **Device State Management**: Centralized device state tracking and synchronization
- **Protocol Translation**: Multi-protocol support and translation

### AI & Machine Learning
- **OpenAI CLIP Integration**: Advanced image understanding and processing
- **Computer Vision**: Real-time image analysis with OpenCV
- **Machine Learning Analytics**: scikit-learn powered device analytics
- **Image Similarity**: Content-based image matching and classification
- **Intelligent Automation**: AI-driven decision making for device control

### Advanced Features
- **Redis Caching**: High-performance caching for device states and analytics
- **Background Processing**: Asynchronous task processing and scheduling
- **Health Monitoring**: Device health monitoring and anomaly detection
- **Scalable Architecture**: Microservice-ready design with dependency injection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    IoT Gateway Service                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Device    │  │  AI/ML      │  │   Communication     │  │
│  │ Management  │  │ Processing  │  │     Layer           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Registration│  │  Analytics  │  │   Message Router    │  │
│  │   Service   │  │   Service   │  │     Service         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    MQTT     │  │    Redis    │  │   OpenAI CLIP +     │  │
│  │   Client    │  │   Cache     │  │   Computer Vision   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                    ┌─────────────────────┐
                    │     IoT Devices     │
                    │ (Sensors/Actuators) │
                    └─────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- Redis 6+
- MQTT Broker (Mosquitto recommended)
- CUDA-compatible GPU (optional, for AI acceleration)

### Installation

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd IoT-smartOffice/gateway
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create `config.json` with your settings:
   ```json
   {
     "mqtt": {
       "broker_host": "localhost",
       "broker_port": 1883,
       "username": "your_username",
       "password": "your_password",
       "client_id": "smartoffice_gateway"
     },
     "redis": {
       "host": "localhost",
       "port": 6379,
       "password": "your_redis_password"
     },
     "ai": {
       "clip_model": "ViT-B/32",
       "enable_gpu": true,
       "batch_size": 16
     }
   }
   ```

4. **Download AI Models**
   ```bash
   # Models will be downloaded automatically on first run
   # Or pre-download with:
   python -c "import clip; clip.load('ViT-B/32')"
   ```

### Running the Gateway

#### Development Mode
```bash
# Auto-restart on code changes
watchfiles "python -m src.main" src
```

#### Production-ready Mode
```bash
python -m src.main
```

## Device Registration

### Registration Request
Devices can register themselves by sending a JSON payload:

```json
{
    "id": "device_001",
    "mac_addr": "AA:BB:CC:DD:EE:FF", 
    "fw_version": "1.2.3",
    "model": "SmartSensor_v2",
    "name": "Temperature Sensor - Room 101",
    "description": "High-precision temperature and humidity sensor",
    "capabilities": {
        "sensors": [
            {
                "name": "temperature",
                "description": "Ambient temperature sensor",
                "unit": "celsius",
                "type": "float"
            },
            {
                "name": "humidity", 
                "description": "Relative humidity sensor",
                "unit": "percent",
                "type": "float"
            }
        ],
        "actuators": [
            {
                "name": "led_indicator",
                "description": "Status LED indicator", 
                "type": "boolean"
            }
        ]
    }
}
```

### Registration Response
The gateway responds with MQTT configuration and topics:

```json
{
    "status": "registered",
    "device_id": "device_001_12345",
    "mqtt_url": "mqtt://localhost:1883",
    "mqtt_username": "device_001",
    "mqtt_password": "generated_secure_password",
    "topics": {
        "telemetry": "devices/device_001/telemetry",
        "commands": "devices/device_001/commands",
        "status": "devices/device_001/status"
    },
    "heartbeat_interval": 60
}
```

## Device Communication

### Telemetry Data
Devices send sensor data in this format:

```json
{
    "device_id": "device_001",
    "timestamp": "2024-01-15T10:30:45.123Z",
    "metrics": {
        "temperature": 22.5,
        "humidity": 65.2,
        "battery_level": 87
    },
    "location": {
        "room": "101",
        "building": "A",
        "floor": 1
    }
}
```

### Device Commands
The gateway sends commands to devices:

```json
{
    "command_id": "cmd_12345",
    "command": "set_actuator_state",
    "parameters": {
        "actuator_name": "led_indicator",
        "state": true,
        "brightness": 75
    },
    "timestamp": 1705312245
}
```

### Command Response
Devices acknowledge commands:

```json
{
    "command_id": "cmd_12345",
    "status": "executed",
    "result": {
        "previous_state": false,
        "new_state": true
    },
    "execution_time": "2024-01-15T10:30:47.456Z"
}
```

## AI & Machine Learning Features

### Image Processing with CLIP
The gateway can analyze images from camera-enabled devices:

```python
# Automatic image classification
image_features = clip_service.encode_image(image_data)
text_features = clip_service.encode_text(["person", "vehicle", "package"])
similarity = compute_similarity(image_features, text_features)
```

## Configuration

### Configuration File Structure
```json
{
  "mqtt": {
    "broker_host": "localhost",
    "broker_port": 1883,
    "keepalive": 60,
    "username": "gateway_user",
    "password": "secure_password",
    "client_id": "smartoffice_gateway",
    "clean_session": true
  },
  "redis": {
    "host": "localhost", 
    "port": 6379,
    "password": "redis_password",
    "db": 0,
    "decode_responses": true
  },
  "ai": {
    "clip_model": "ViT-B/32",
    "enable_gpu": true,
    "batch_size": 16,
    "cache_embeddings": true,
    "similarity_threshold": 0.7
  },
  "device_management": {
    "registration_timeout": 300,
    "heartbeat_interval": 60,
    "max_offline_time": 180,
    "auto_provision": true
  },
  "security": {
    "enable_tls": false,
    "cert_file": "/path/to/cert.pem",
    "key_file": "/path/to/key.pem",
    "ca_file": "/path/to/ca.pem"
  }
}
```
