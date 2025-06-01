# IoT Gateway Modifications

This document describes three major modifications made to the smart office IoT gateway system.

## 1. Last Will and Testament (LWT) Service

### Overview
Implemented a service to handle MQTT Last Will and Testament messages from devices. When a device disconnects unexpectedly, it publishes its MAC address to the LWT topic, and the gateway marks it as offline.

### Implementation Details
- **File**: `src/services/lwt_service.py`
- **Topic**: `gateway/lwt` (configured in config.json)
- **Payload**: MAC address of the disconnected device

### Features
- Subscribes to the LWT topic on startup
- When receiving LWT message:
  - Looks up device by MAC address in Redis cache
  - Updates device status to OFFLINE in cache
  - Calls backend API to update device status
  - Logs the status change

### Configuration
Add the following to your `config.json` under `mosquitto.topics`:
```json
"lwt": {
    "topic": "gateway/lwt",
    "qos": 1,
    "retain": 1,
    "description": "Device is offline",
    "src": "device",
    "dst": "gateway"
}
```

## 2. Error Data Handling in Telemetry

### Overview
Enhanced the telemetry service to detect error data (when sensor values are "E") and handle them appropriately.

### Implementation Details
- **Modified File**: `src/services/telemetry.py`
- **Error Detection**: Checks for "E" values in telemetry data

### Features
- Detects when any telemetry field contains "E"
- Updates device status to ERROR in:
  - Local Redis cache
  - Backend server via HTTP API
- Sends error notification (if notification service is configured)
- Still forwards telemetry data to cloud for logging

### Notification Format
```json
{
    "title": "Device Error: {device_name}",
    "message": "Device {device_name} reported error data in fields: {error_fields}",
    "type": "error",
    "device_id": {device_id}
}
```

## 3. AI Multimedia Retrieval Service

### Overview
Integrated an AI-powered multimedia processing and retrieval system for smart office camera devices.

### Architecture
```
Camera Device → Telemetry → AI Service → Backend (pgvector)
                                ↓
                          Tag Extraction
                                ↓
                          Search Index
```

### Components

#### AI Service (`src/services/ai/ai_service.py`)
- Monitors telemetry events for camera devices
- Processes images in batches for efficiency
- Manages image storage and metadata
- Sends processed data to backend for pgvector storage

#### Tag Retrieval (`src/services/ai/tag_retrieval.py`)
- TF-IDF based tag search
- Maintains searchable index of image tags
- Supports tag-based similarity search

#### CLIP Retrieval (`src/services/ai/clip_retrieval.py`)
- Placeholder for natural language search
- In production, would use CLIP model for semantic search

#### Inference Processor (`src/services/ai/inference_processor.py`)
- Processes images to extract tags
- Currently uses simulated tags (demo mode)
- In production, would use RAM (Recognize Anything Model)

### Features
- **Image Capture**: Processes base64-encoded images from camera telemetry
- **Duplicate Detection**: Uses perceptual hashing to avoid processing similar images
- **Batch Processing**: Groups images for efficient inference
- **Tag Extraction**: Extracts semantic tags from images
- **Search Capabilities**:
  - Tag-based search using TF-IDF
  - Natural language search (placeholder for CLIP)
  - Hybrid search combining both methods
- **Backend Integration**: Sends processed data to backend for pgvector storage

### Data Flow
1. Camera sends image in telemetry: `{"image": "base64_encoded_data"}`
2. AI service saves and queues image
3. Batch processor extracts tags
4. Tags and embeddings sent to backend
5. Backend stores in pgvector for similarity search

### API Endpoints (Backend)
The service expects the following endpoint on the backend:
- `POST /multimedia/images` - Store processed image data with embeddings

### Search Interface
```python
results = await ai_service.search_images(
    query="person computer office",
    search_type="hybrid",  # "tag", "nl", or "hybrid"
    k=10
)
```

## Installation

### Dependencies
Install base dependencies:
```bash
pip install -r requirements.txt
```

For AI service (additional):
```bash
pip install -r requirements_ai.txt
```

### Production Notes
For production deployment of the AI service:
1. Install deep learning dependencies (PyTorch, Transformers)
2. Download model weights:
   - RAM model for tag extraction
   - CLIP model for semantic search
3. Configure GPU support for inference
4. Adjust batch size based on available memory

## Service Integration

All three services are integrated into the gateway lifecycle:

### Container Registration (`src/container.py`)
- LWT service with MQTT and HTTP client dependencies
- Enhanced telemetry service with HTTP client and notification support
- AI multimedia service with event bus and HTTP client

### Main Application (`src/main.py`)
- Services start automatically on gateway startup
- Graceful shutdown saves AI model states and metadata
- All services properly stop on shutdown

## Testing

### LWT Testing
1. Connect a device to the gateway
2. Set the device's LWT message to its MAC address
3. Disconnect the device abruptly
4. Check logs for offline status update

### Error Data Testing
1. Send telemetry with error values:
   ```json
   {"temperature": "E", "humidity": 45}
   ```
2. Check device status changes to ERROR
3. Verify notification is sent

### AI Service Testing
1. Send image telemetry from camera device:
   ```json
   {"image": "base64_encoded_jpeg_data"}
   ```
2. Check logs for image processing
3. Use search API to find images by tags

## Future Enhancements

1. **LWT Service**: Add reconnection detection and automatic status recovery
2. **Error Handling**: Implement error recovery strategies and alerts
3. **AI Service**: 
   - Integrate real deep learning models
   - Add video stream processing
   - Implement real-time alerts for detected objects
   - Add face recognition for access control 