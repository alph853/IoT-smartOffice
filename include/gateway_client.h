#pragma once

#include <config.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <control.h>


constexpr char   mqttServer[] = "192.168.1.164";
constexpr uint16_t mqttPort   = 1883;

constexpr char   mqttUser[]   = "";
constexpr char   mqttPass[]   = "";

extern const char* topicRegReq;

extern String topicRegRes;
extern String topicTelem;
extern String topicCmdReq;
extern String topicCmdRes;


extern String       deviceID;
extern WiFiClient   netClient;
extern PubSubClient mqtt_client;

extern bool         isRegistered;


// Function declarations
void gateway_callback(char* topic, byte* payload, unsigned int length);
void sendRegistration();
void connectGateway();
void connectGatewayTask(void *pvParameters);








