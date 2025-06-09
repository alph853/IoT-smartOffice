#ifndef TELEMETRY_H
#define TELEMETRY_H

// include
#include "config.h"
#include <Arduino.h>
#include "gateway_client.h"
// #include <LiquidCrystal_I2C.h>
#include "DHT20.h"


extern bool isRegistered;
extern uint32_t TELEMETRY_INTERVAL;
extern DHT20 dht20;
extern String topicTelem;

// extern LiquidCrystal_I2C lcd;


// Task functions
bool sensorIsConnected(uint8_t address);
void sendTelemetryTask(void *pvParameters);
#endif

