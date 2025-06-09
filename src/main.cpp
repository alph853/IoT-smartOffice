#include "main.h"


void setup() {
    // Initialize Serial
    if (!init_setup()) {
        return;
    }
    // Create RTOS tasks
    xTaskCreate(wifiTask, "wifiTask", 4096, NULL, 2, NULL);
    xTaskCreate(connectGatewayTask, "connectGatewayTask", 4096, NULL, 2, NULL);
    xTaskCreate(sendTelemetryTask, "sendTelemetryTask", 4096, NULL, 2, NULL);
}


void loop() {
    // Empty as we're using RTOS tasks
}