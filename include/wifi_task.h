#include <WiFi.h>
#include <config.h>


constexpr char WIFI_SSID[]     = "HAI";
constexpr char WIFI_PASSWORD[] = "180266127";


bool isWiFiConnected();
void initWiFi();
void wifiTask(void *pvParameters);


extern WiFiClient   netClient;
