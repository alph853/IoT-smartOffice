#include <wifi_task.h>


bool isWiFiConnected() {
    return WiFi.status() == WL_CONNECTED;
}

void initWiFi() {
    Serial.println("[INFO] Connecting to AP ...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (!isWiFiConnected()) {
        vTaskDelay(pdMS_TO_TICKS(500));
        Serial.print(".");
    }
    Serial.println("[INFO] Connected to AP");
}


void wifiTask(void *pvParameters) {
    initWiFi();

    while (true) {
        if (!isWiFiConnected()) {
            Serial.println("[INFO] Lost connection to WiFi, reconnecting...");
            initWiFi();
            vTaskDelay(pdMS_TO_TICKS(5000));
            continue;
        }
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}