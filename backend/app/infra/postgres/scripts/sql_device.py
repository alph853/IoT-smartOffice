
GET_ALL_DEVICES = """
SELECT * FROM device
"""

GET_DEVICE_BY_ID = """
SELECT * FROM device WHERE id = $1
"""

CREATE_DEVICE = """
INSERT INTO device (name, mode, registered_at, mac_addr, description, fw_version, last_seen_at, model, office_id, gateway_id, status, access_token)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
RETURNING id, name, mode, registered_at, mac_addr, description, fw_version, last_seen_at, model, office_id, gateway_id, status, access_token
"""

UPDATE_DEVICE = """
"""

DELETE_DEVICE = """
"""

CREATE_SENSOR = """
INSERT INTO sensor (name, type, unit, device_id)
VALUES ($1, $2, $3, $4)
RETURNING id, name, type, unit, device_id
"""

CREATE_ACTUATOR = """
INSERT INTO actuator (name, type, device_id)
VALUES ($1, $2, $3)
RETURNING id, name, type, device_id
"""

GET_ALL_SENSORS = """
SELECT * FROM sensor
"""

GET_SENSOR_BY_ID = """
SELECT * FROM sensor WHERE id = $1
"""

GET_ALL_ACTUATORS = """
SELECT * FROM actuator
"""

GET_ACTUATOR_BY_ID = """
SELECT * FROM actuator WHERE id = $1
"""

CREATE_SENSOR_READING = """
INSERT INTO sensor_reading (id, data, cap_id, ts)
VALUES ($1, $2, $3, $4)
"""

GET_ALL_SENSOR_READINGS = """
SELECT * FROM sensor_reading
"""



