CREATE_TABLE = """
-- 1. OFFICE
CREATE TABLE office (
  id            SERIAL PRIMARY KEY,
  room          TEXT              NOT NULL,
  building      TEXT              NOT NULL,
  name          TEXT              NOT NULL,
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
  mode          TEXT              NOT NULL,
  name          TEXT              NOT NULL,
  registered_at TIMESTAMPTZ       NOT NULL DEFAULT now(),
  mac_addr      TEXT              NOT NULL UNIQUE,
  description   TEXT,
  fw_version    TEXT,
  last_seen_at  TIMESTAMPTZ       NOT NULL DEFAULT now(),
  model         TEXT,
  office_id     INTEGER           REFERENCES office(id)  ON DELETE SET NULL,
  gateway_id    INTEGER           REFERENCES gateway(id) ON DELETE SET NULL,
  status        TEXT              NOT NULL DEFAULT 'online',
  access_token  TEXT              UNIQUE
);

-- 5. SENSOR  (extends capability)
CREATE TABLE sensor (
  id         SERIAL PRIMARY KEY,
  device_id  INTEGER NOT NULL
               REFERENCES device(id) ON DELETE CASCADE,
  unit       TEXT     NOT NULL,
  name       TEXT     NOT NULL,
  type       TEXT     NOT NULL
);

-- 6. ACTUATOR (extends capability)
CREATE TABLE actuator (
  id         SERIAL PRIMARY KEY,
  device_id  INTEGER NOT NULL
               REFERENCES device(id) ON DELETE CASCADE,
  name        TEXT     NOT NULL,
  type        TEXT     NOT NULL
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
  cap_id        INTEGER           NOT NULL
                   REFERENCES sensor(cap_id)   ON DELETE CASCADE,
  ts            TIMESTAMPTZ       NOT NULL DEFAULT now()
);

-- 11. ACTIVITY_LOG
CREATE TABLE activity_log (
  id            SERIAL PRIMARY KEY,
  in_mode       TEXT              NOT NULL,
  params        JSONB,
  description   TEXT,
  cap_id        INTEGER           REFERENCES capability(id) ON DELETE SET NULL,
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
  device_id     INTEGER           REFERENCES device(id) ON DELETE CASCADE
);


"""