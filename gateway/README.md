
## Installations

```bash
pip install -r requirements.txt

```

## Development

```bash
watchfiles "python -m src.main" src
```

## Run

```bash
python -m src.main
```

## Payload Schema

Device registration request
```json
{
    // Optional, if not provided, the gateway will generate an id
    // for the current session
    "id": "string",
    "mac_addr": "string",
    "fw_version": "string",
    "model": "string",
    "name": "string",
    "description": "string",
    "capabilities": {
        "sensors": [
            {
                "name": "string",
                "description": "string",
                "unit": "string",
                "type": "string"
            }
        ],
        "actuators": [
            {
                "name": "string",
                "description": "string",
                "type": "string"
            }
        ]
    }
}
```

Device registration response
```json
{
    "status": "string",
    "mqtt_url": "string",
    "mqtt_username": "string",
    "mqtt_password": "string",
    "topics": {
        "telemetry": "string",
        "commands": "string"
    }
}


Device telemetry
```json
{
    "id": "string",
    "timestamp": "ISO8601",
    "metrics": {
        "metric_name": "number"
    }
}
```

Device command
```json
{
    "command": "string",
    "parameters": {},
    "ts": "integer"
}
```

