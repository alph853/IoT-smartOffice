#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <Wire.h>


/* -------------------------------------
 * ---------- Device Info --------------
 * ------------------------------------- */

#define FW_VERSION      "1.0.0"
#define MODEL           "Yolo_UNO_S3_AIOT"
#define NAME            "OhStem Yolo UNO S3 AIoT Board"
#define DESCRIPTION     "A compact Arduino-form development board powered by ESP32-S3 with dual-core 240 MHz, 16 MB Flash, 8 MB PSRAM, AI accelerator, 12 Grove ports, STEMMA QT, GVS servo headers, onboard NeoPixel RGB LED, Wi-Fi & Bluetooth, USB-C/DC power, and multi-language programming support."
#define OFFICE_ID       "1"

/* -------------------------------------
 * ---------- Pin definitions ----------
 * ------------------------------------- */

#define LED_PIN GPIO_NUM_48
#define LDR_PIN GPIO_NUM_1
#define CAMERA_PIN 0
#define NEO_PIXEL_PIN GPIO_NUM_6
#define FAN_PIN GPIO_NUM_18

#define SDA_PIN GPIO_NUM_11
#define SCL_PIN GPIO_NUM_12


bool init_setup();

#endif // CONFIG_H