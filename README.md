# Source code to connect to devices and run Gateway

- setLedState
- setBlinkState

## Protocols

- Gateway -> Serial:
  - LED_{device_id}=(0/1)
  - BLINK_{device_id}={interval}?
  - PUMP_{device id}={duration}

- Serial -> Gateway:
  - device_id:key=value(,key=value)*

- Gateway -> CoreIoT:

```json
{
  device_id: {
    "ts": {current timestamp},
    "type": {device type, e.g LED, CAMERA},
    "values": {a json of key-value pairs, e.g {"temp":20, "humi": 50}}
  }
}
```
