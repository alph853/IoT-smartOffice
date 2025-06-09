# 🏢 Smart Office IoT System

A comprehensive Internet of Things (IoT) solution for modern smart offices, featuring real-time device monitoring, intelligent automation, and seamless control through multiple interfaces.

## Features

### Core Capabilities
- **Real-time Device Management**: Monitor and control IoT devices across office spaces
- **Intelligent Automation**: AI-powered device automation and scheduling
- **Multi-platform Access**: Web API and Android mobile application
- **Live Communication**: WebSocket-based real-time updates
- **Smart Notifications**: Context-aware alerts and notifications
- **Multimedia Integration**: Image processing and multimedia management
- **Advanced Analytics**: Device usage analytics and reporting

### Device Support
- **Sensors**: Temperature, humidity, light, motion, and environmental sensors
- **Actuators**: Smart lighting (RGB, brightness control), fans, etc
- **Smart Controls**: Automated and manual device state management
- **Scheduling**: Time-based and rule-based automation


## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- MQTT Broker (e.g., Mosquitto)
- Android Studio (for mobile app development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd IoT-smartOffice
   ```

2. **Set up the Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Configure config.json with your database and service settings
   fastapi dev app/main.py
   ```

3. **Set up the Gateway**
   ```bash
   cd gateway
   pip install -r requirements.txt
   python -m src.main
   ```

4. **Set up the Android App**
   ```bash
   cd frontend
   ./gradlew build
   # Open in Android Studio for development
   ```

### Configuration

Create configuration files for each service:

- `backend/config.json`: Database, ThingsBoard, and service configuration
- `gateway/config.json`: Gateway-specific settings and AI model configuration
- Update MQTT broker settings in both backend and gateway

## Components

### Backend (`/backend`)
FastAPI-based REST API and WebSocket server providing:
- Device management endpoints
- Real-time WebSocket communication
- User notification system
- Scheduling and automation
- Multimedia processing
- Integration with ThingsBoard IoT platform

**Key Technologies**: FastAPI, PostgreSQL, Redis, WebSocket, MQTT, AsyncIO

### Gateway (`/gateway`)
Intelligent IoT gateway service featuring:
- Device registration and discovery
- MQTT message routing
- AI-powered image processing (OpenAI CLIP)
- Machine learning analytics
- Computer vision capabilities
- Device state management

**Key Technologies**: Python, MQTT, OpenAI CLIP, scikit-learn, OpenCV, Redis

### Android App (`/frontend`)
Native Android application offering:
- Intuitive device control interface
- Real-time monitoring dashboards
- Push notifications
- Room-based device organization
- Manual and automated control modes

**Key Technologies**: Android (Kotlin/Java), Gradle, Material Design

## Usage Examples

### Device Control via WebSocket
```json
{
    "method": "setLighting",
    "params": {
        "actuator_id": 342,
        "brightness": 85,
        "color": ["white", "yellow"]
    }
}
```

### Fan Control
```json
{
    "method": "setFanState",
    "params": {
        "actuator_id": 161,
        "state": true
    }
}
```

### Mode Setting
```json
{
    "method": "setMode",
    "params": {
        "actuator_id": 161,
        "mode": "auto"
    }
}
```

## Development Workflow

### Backend Development
```bash
cd backend
fastapi dev app/main.py  # Development server with hot reload
```

### Gateway Development
```bash
cd gateway
watchfiles "python -m src.main" src  # Auto-restart on changes
```

### Frontend Development
```bash
cd frontend
./gradlew assembleDebug  # Build debug APK
```

## API Documentation

Once the backend is running, access swagger API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
