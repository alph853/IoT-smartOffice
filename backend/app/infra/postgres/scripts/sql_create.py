CREATE_TABLE = """
-- 1. OFFICE
CREATE TABLE office (
  id            SERIAL PRIMARY KEY,
  room          TEXT,
  building      TEXT,
  name          TEXT,
  description   TEXT,
);

-- 2. GATEWAY
CREATE TABLE gateway (
  id            SERIAL PRIMARY KEY,
  name          TEXT              NOT NULL,
  status        TEXT              NOT NULL
);

CREATE TABLE monitor (
	office_id      INTEGER           REFERENCES office(id)  ON DELETE SET NULL,
	gateway_id     INTEGER           REFERENCES gateway(id) ON DELETE SET NULL,
	PRIMARY KEY (office_id, gateway_id)
);


-- 3. DEVICE
CREATE TABLE device (
  id            SERIAL PRIMARY KEY,
  name          TEXT              UNIQUE NOT NULL,
  registered_at TIMESTAMPTZ       NOT NULL DEFAULT now(),
  mac_addr      TEXT              NOT NULL UNIQUE,
  description   TEXT,
  fw_version    TEXT,
  last_seen_at  TIMESTAMPTZ       NOT NULL DEFAULT now(),
  model         TEXT,
  office_id     INTEGER           REFERENCES office(id)  ON DELETE SET NULL,
  gateway_id    INTEGER           REFERENCES gateway(id) ON DELETE SET NULL,
  status        TEXT              NOT NULL DEFAULT 'online',
  access_token  TEXT              UNIQUE,
  thingsboard_name TEXT           NOT NULL,          
  device_id       TEXT            NOT NULL,
);

ALTER TABLE device
ADD CONSTRAINT device_name_unique UNIQUE (name);

-- 5. SENSOR
CREATE TABLE sensor (
  id         SERIAL PRIMARY KEY,
  device_id  INTEGER NOT NULL
               REFERENCES device(id) ON DELETE CASCADE
               DEFERRABLE INITIALLY DEFERRED,
  unit       TEXT,
  name       TEXT     NOT NULL,
  type       TEXT     NOT NULL
);

-- 6. ACTUATOR
CREATE TABLE actuator (
  id         SERIAL PRIMARY KEY,
  device_id  INTEGER NOT NULL
               REFERENCES device(id) ON DELETE CASCADE
               DEFERRABLE INITIALLY DEFERRED,
  name        TEXT     NOT NULL,
  type        TEXT     NOT NULL,
  mode        TEXT     NOT NULL,
  setting     JSONB    NOT NULL
);
  

-- 8. SCHEDULE
CREATE TABLE schedule (
  id            SERIAL PRIMARY KEY,
  end_min       SMALLINT          NOT NULL,
  start_min     SMALLINT          NOT NULL,
  days          TEXT              NOT NULL,
  active        BOOLEAN           NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ       NOT NULL DEFAULT now(),
  cmd_id        INTEGER,
  device_id     INTEGER           REFERENCES device(id) ON DELETE CASCADE
);

-- 9. CONTROL  (linking an actuator capability to a schedule)
CREATE TABLE control (
  cap_id        INTEGER           NOT NULL
                   REFERENCES actuator(cap_id) ON DELETE CASCADE,
  sched_id      INTEGER           NOT NULL
                   REFERENCES schedule(id)   ON DELETE CASCADE,
  params        JSONB,
  PRIMARY KEY (cap_id, sched_id)
);

-- 10. SENSOR_READING
CREATE TABLE sensor_reading (
  id            SERIAL PRIMARY KEY,
  data          JSONB             NOT NULL,
  sensor_id     INTEGER           NOT NULL
                   REFERENCES sensor(id)   ON DELETE CASCADE,
  ts            TIMESTAMPTZ       NOT NULL DEFAULT now()
);

-- 11. ACTIVITY_LOG
CREATE TABLE activity_log (
  id            SERIAL PRIMARY KEY,
  in_mode       TEXT              NOT NULL,
  params        JSONB,
  description   TEXT,
  actuator_id   INTEGER           REFERENCES actuator(id) ON DELETE SET NULL,
  ts            TIMESTAMPTZ       NOT NULL DEFAULT now()
);

-- 12. FOOTAGE
CREATE TABLE footage (
  id            SERIAL PRIMARY KEY,
  embeddings    JSONB,
  file_name     TEXT              NOT NULL,
  objects       JSONB,
  device_id     INTEGER           REFERENCES device(id) ON DELETE CASCADE
);

-- 13. NOTIFICATION
CREATE TABLE notification (
  id            SERIAL PRIMARY KEY,
  message       TEXT              NOT NULL,
  read_status   BOOLEAN           NOT NULL DEFAULT FALSE,
  type          TEXT              NOT NULL,
  title         TEXT,
  device_id     INTEGER           REFERENCES device(id) ON DELETE CASCADE,
  ts            TIMESTAMPTZ       NOT NULL DEFAULT now()
);


-- 14. SCHEDULE
DROP TABLE IF EXISTS schedule CASCADE;

CREATE TABLE schedule (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    actuator_id   INTEGER NOT NULL REFERENCES actuator(id) ON DELETE CASCADE,
    schedule_type TEXT NOT NULL CHECK (schedule_type IN ('lighting', 'fan')),
    days_of_week  INTEGER[] NOT NULL,
    start_time    TIME NOT NULL,
    end_time      TIME NOT NULL,
    setting       JSONB NOT NULL,
    priority      INTEGER NOT NULL DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_schedule_actuator_id ON schedule(actuator_id);
CREATE INDEX idx_schedule_active ON schedule(is_active);
CREATE INDEX idx_schedule_type ON schedule(schedule_type);


"""