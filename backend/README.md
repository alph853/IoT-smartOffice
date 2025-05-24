# Smart Office Backend

## Setup

```bash
pip install -r requirements.txt
```

## Run

### Development
```bash
fastapi dev backend/app/main.py
```

### Production
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Websocket

- Set Mode

```json
{
    "method": "setMode",
    "params": {
        "actuator_id": 161,
        "mode": "auto"
    }
}
```

- Set Lighting
```json
{
    "method": "setLighting",
    "params": {
        "actuator_id": 161,
        "brightness": 100,
        "color": "red"
    }
}
```

- Set Fan State
```json
{
    "method": "setFanState",
    "params": {
        "actuator_id": 161,
        "state": true
    }
}
```

