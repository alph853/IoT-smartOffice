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
Supported Colors: white, yellow, purple, orange, pink
```json
{
    "method": "setLighting",
    "params": {
        "actuator_id": 342,
        "brightness": 100,
        "color": ["white", "yellow", [255,100,128], [120,120,100]]
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

