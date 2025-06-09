#include "config.h"


bool init_setup() {
    Serial.begin(115200);
    delay(1000);


    // // Initialize hardware
    // Wire.begin(SDA_PIN, SCL_PIN);
    // pinMode(LDR_PIN, INPUT);
    // pinMode(LED_PIN, OUTPUT);
    // // pinMode(BUTTON_A_PIN, INPUT);
    // // pinMode(BUTTON_B_PIN, INPUT);
    // // pinMode(PIR_PIN, INPUT);

    // pinMode(CAMERA_PIN, OUTPUT);
    // digitalWrite(CAMERA_PIN, HIGH);

    // pinMode(PUMP_PIN, OUTPUT);
    // digitalWrite(PUMP_PIN, LOW);

    return true;
}