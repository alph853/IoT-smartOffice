#include "telemetry.h"


DHT20 dht20;
uint32_t TELEMETRY_INTERVAL = 5000;

const float LIGHT_MAX = 4100;
const float LIGHT_MIN = 0;


bool sensorIsConnected(uint8_t address) {
    Wire.beginTransmission(address);
    return (Wire.endTransmission() == 0);
}


void sendTelemetryTask(void *pvParameters) {
    dht20.begin();

    String temperature;
    String humidity;
    String luminousity;
    int error_code = 0;

    while (!isRegistered) {
        vTaskDelay(pdMS_TO_TICKS(TELEMETRY_INTERVAL));
    }
    Serial.println("[INFO] Telemetry task started");

    while (true) {
        if (!sensorIsConnected(0x38)) {
            error_code = 1;
            temperature = "E";
            humidity = "E";
        } else {
            dht20.read();
            float temp = dht20.getTemperature();
            float hum = dht20.getHumidity();

            if (!isnan(temp)) {
                temperature = String(temp);
            } else {
                temperature = "E";
                error_code = 2;
            }

            if (!isnan(hum)) {
                humidity = String(hum);
            } else {
                humidity = "E";
                error_code = 2;
            }
        }

        float lux = analogRead(LDR_PIN) / (LIGHT_MAX - LIGHT_MIN);
        if (!isnan(lux)) {
            luminousity = String(lux);
        } else {
            luminousity = "E";
            error_code = 2;
        }

        static const size_t JSON_CAPACITY =
            JSON_OBJECT_SIZE(3)      // temperature, humidity, luminousity
        + 256;                     // extra for strings

        StaticJsonDocument<JSON_CAPACITY> payload;
        payload["temperature"] = temperature;
        payload["humidity"] = humidity;
        payload["luminousity"] = luminousity;

        Serial.println(payload.as<String>());

        size_t json_len = measureJson(payload);
        mqtt_client.beginPublish(topicTelem.c_str(), json_len, false);
        serializeJson(payload, mqtt_client);
        mqtt_client.endPublish();

        vTaskDelay(pdMS_TO_TICKS(TELEMETRY_INTERVAL));
    }
}
