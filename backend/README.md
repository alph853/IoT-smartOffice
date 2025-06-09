# Smart Office Backend

A high-performance FastAPI-based backend service for the Smart Office IoT system, providing real-time device management, WebSocket communication, and comprehensive API endpoints for IoT device control and monitoring.

## Features

### Core Capabilities
- **RESTful API**: Comprehensive REST endpoints for all system operations
- **Real-time Communication**: WebSocket support for live device updates
- **Device Management**: Complete CRUD operations for IoT devices and sensors
- **Smart Notifications**: Context-aware notification system with filtering
- **Scheduling System**: Advanced scheduling and automation capabilities
- **Multimedia Support**: Image and multimedia content management
- **ThingsBoard Integration**: Seamless integration with ThingsBoard IoT platform
- **Database Management**: PostgreSQL with pgvector for advanced queries

### Technical Features
- **Asynchronous Operations**: Full async/await support for high performance
- **Dependency Injection**: Clean architecture with dependency injection
- **Event-Driven Architecture**: In-process event bus for loose coupling
- **Background Tasks**: Scheduled tasks and background processing
- **Health Monitoring**: Built-in health checks and monitoring
- **Structured Logging**: Comprehensive logging with Loguru

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   REST API  │  │  WebSocket  │  │   Background Tasks  │  │
│  │   Routes    │  │   Handler   │  │   & Schedulers      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Service Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Device    │  │Notification │  │    Office & Media   │  │
│  │   Service   │  │   Service   │  │     Services        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Repository Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ PostgreSQL  │  │    Redis    │  │   ThingsBoard API   │  │
│  │ Repository  │  │   Cache     │  │     Client          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ with pgvector extension
- Redis 6+
- ThingsBoard instance (optional)

### Installation

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd IoT-smartOffice/backend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create `config.json` with your settings:
   ```json
   {
     "postgres": {
       "host": "localhost",
       "port": 5432,
       "user": "your_user",
       "password": "your_password",
       "database": "smartoffice"
     },
     "thingsboard": {
       "url": "your_thingsboard_url",
       "port": 1883,
       "username": "your_username",
       "password": "your_password",
       "api": "http://your_thingsboard_api",
       "device_id": "your_device_id",
       "device_name": "SmartOffice"
     }
   }
   ```

4. **Database Setup**
   ```bash
   # Create database and enable pgvector
   psql -U postgres -c "CREATE DATABASE smartoffice;"
   psql -U postgres -d smartoffice -c "CREATE EXTENSION vector;"
   ```

### Running the Application

#### Development Mode
```bash
fastapi dev app/main.py
```
- Runs on `http://localhost:8000`
- Auto-reload on code changes
- Debug mode enabled

#### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Device Control Commands

#### Set Lighting
```json
{
    "method": "setLighting",
    "params": {
        "actuator_id": 342,
        "brightness": 100,
        "color": ["white", "yellow", [255,100,128]]
    }
}
```

#### Control Fan
```json
{
    "method": "setFanState",
    "params": {
        "actuator_id": 161,
        "state": true
    }
}
```

#### Set Device Mode
```json
{
    "method": "setMode",
    "params": {
        "actuator_id": 161,
        "mode": "auto"
    }
}
```

### Supported Colors
- **Named Colors**: `white`, `yellow`, `purple`, `orange`, `pink`
- **RGB Arrays**: `[red, green, blue]` (0-255 each)

## Database Schema

### Key Tables
- **devices**: Device registration and metadata
- **sensors**: Sensor definitions and current readings
- **actuators**: Actuator definitions and states
- **notifications**: System notifications and alerts
- **schedules**: Automation schedules and rules
- **multimedia**: Multimedia content and metadata

### Vector Support
The system uses PostgreSQL with pgvector for:
- Similarity searches
- ML model embeddings
- Advanced analytics queries

### Configuration File (config.json)
```json
{
  "postgres": {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "smartoffice"
  },
  "thingsboard": {
    "url": "localhost",
    "port": 1883,
    "client_id": "smartoffice-backend",
    "username": "your_username",
    "password": "your_password",
    "api": "http://localhost:8080",
    "device_id": "your_device_id",
    "device_name": "SmartOffice"
  },
  "redis": {
    "host": "localhost",
    "port": 6379
  }
}
```


## API Documentation

Once running, access swagger API documentation:
- **Swagger UI**: `http://localhost:8000/docs`

