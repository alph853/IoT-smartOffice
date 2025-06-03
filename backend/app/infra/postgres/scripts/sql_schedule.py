# Schedule table SQL queries

# Get all schedules
GET_ALL_SCHEDULES = """
SELECT id, name, actuator_id, schedule_type, days_of_week, start_time, end_time, 
       setting, priority, is_active, created_at, updated_at
FROM schedule
ORDER BY priority DESC, updated_at DESC;
"""

# Get schedule by ID
GET_SCHEDULE_BY_ID = """
SELECT id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
       setting, priority, is_active, created_at, updated_at
FROM schedule
WHERE id = $1;
"""

# Get schedules by actuator ID
GET_SCHEDULES_BY_ACTUATOR_ID = """
SELECT id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
       setting, priority, is_active, created_at, updated_at
FROM schedule
WHERE actuator_id = $1
ORDER BY priority DESC, updated_at DESC;
"""

# Create schedule
CREATE_SCHEDULE = """
INSERT INTO schedule (name, actuator_id, schedule_type, days_of_week, start_time, end_time,
                      setting, priority, is_active)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
RETURNING id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
          setting, priority, is_active, created_at, updated_at;
"""

# Update schedule
UPDATE_SCHEDULE = """
UPDATE schedule
SET name = COALESCE($2, name),
    actuator_id = COALESCE($3, actuator_id),
    schedule_type = COALESCE($4, schedule_type),
    days_of_week = COALESCE($5, days_of_week),
    start_time = COALESCE($6, start_time),
    end_time = COALESCE($7, end_time),
    setting = COALESCE($8, setting),
    priority = COALESCE($9, priority),
    is_active = COALESCE($10, is_active),
    updated_at = NOW()
WHERE id = $1
RETURNING id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
          setting, priority, is_active, created_at, updated_at;
"""

# Delete schedule
DELETE_SCHEDULE = """
DELETE FROM schedule WHERE id = $1;
"""

# Get active schedules
GET_ACTIVE_SCHEDULES = """
SELECT id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
       setting, priority, is_active, created_at, updated_at
FROM schedule
WHERE is_active = TRUE
ORDER BY priority DESC, updated_at DESC;
"""

# Get schedules by type
GET_SCHEDULES_BY_TYPE = """
SELECT id, name, actuator_id, schedule_type, days_of_week, start_time, end_time,
       setting, priority, is_active, created_at, updated_at
FROM schedule
WHERE schedule_type = $1
ORDER BY priority DESC, updated_at DESC;
"""
