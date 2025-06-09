#include <gateway_client.h>
#include <unordered_map>
#include <update.h>


/* -------------------------------------
 * ------------ Variables --------------
 * ------------------------------------- */

WiFiClient   netClient;
PubSubClient mqtt_client(netClient);

const char*  topicRegReq = "gateway/register/request";

String       topicRegRes = "gateway/register/response/";
String       topicCmdReq = "gateway/control/command/";
String       topicCmdRes = "gateway/control/response/";
String       topicTelem  = "gateway/telemetry/";

String       deviceID       = "";
bool         isRegistered   = false;

std::unordered_map<int, String> sensor_id_map;
std::unordered_map<int, String> actuator_id_map;
std::unordered_map<int, int> neo_pixel_ids;


/* -------------------------------------
 * ------------ Functions --------------
 * ------------------------------------- */

void gateway_callback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (unsigned int i = 0; i < length; i++) {
        msg += (char)payload[i];
    }
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, msg);
    if (error) {
        Serial.print("[ERROR] Deserialization error on topic: ");
        Serial.println(topic);
        Serial.print("Message: ");
        Serial.println(msg);
        Serial.print("Error: ");
        Serial.println(error.f_str());
        return;
    }

    Serial.println("\n[MQTT] ---- Callback Triggered ----");
    Serial.print("[MQTT] Topic: '");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(msg);

    if (String(topic) == topicRegRes) {
        // format: OK,id=123457890
        deviceID = doc["device_id"].as<String>();
        JsonArray sensors = doc["sensors"];
        JsonArray actuators = doc["actuators"];

        for (const JsonObject& sensor : sensors) {
            String name = sensor["name"].as<String>();
            int id = sensor["id"].as<int>();
            sensor_id_map[id] = name;
        }

        for (const JsonObject& actuator : actuators) {
            String name = actuator["name"].as<String>();
            int id = actuator["id"].as<int>();
            actuator_id_map[id] = name;
        }
        isRegistered = true;
        topicTelem += deviceID;
        topicCmdReq += deviceID;
        topicCmdRes += deviceID;
        mqtt_client.subscribe(topicCmdReq.c_str());
        Serial.println("[INFO] Registration successful! Subscribed to:");
        Serial.println(topicCmdReq);
        Serial.println(topicCmdRes);
        Serial.println(topicTelem);

    } else if (String(topic) == topicCmdReq) {
        StaticJsonDocument<256> response;
        String request_id = doc["params"]["request_id"];

        String method = doc["method"];
        if (method == "test") {
            Serial.println("[INFO] Test command received");
            response["status"] = "success";
        } else if (method == "setLighting") {
            Serial.println("[INFO] Set lighting command received");
            int color_array[4][3];

            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 3; j++) {
                    color_array[i][j] = doc["params"]["color"][i][j];
                }
            }
            int actuator_id = doc["params"]["actuator_id"];
            int pixel_id = neo_pixel_ids[actuator_id];
            setNeoPixel(pixel_id, color_array);
            response["status"] = "success";
        } else if (method == "setFanState") {
            bool state = doc["params"]["state"];
            setFanState(doc["params"]["actuator_id"], state);
            response["status"] = "success";
        } else {
            Serial.println("[ERROR] Unknown method");
            response["status"] = "error";
        }
        response["request_id"] = request_id;
        size_t json_len = measureJson(response);
        mqtt_client.beginPublish(topicCmdRes.c_str(), json_len, false);
        serializeJson(response, mqtt_client);
        mqtt_client.endPublish();
    } else {
        Serial.println("[INFO] Unknown topic");
    }
}


void sendRegistration() {
    static const size_t JSON_CAPACITY =
        JSON_OBJECT_SIZE(7)      // mac_addr, fw_version, model, name, description, office_id, sensors, actuators
    + JSON_ARRAY_SIZE(4)       // sensors array has 4 entries
    + 4*JSON_OBJECT_SIZE(3)    // each sensor object has 3 fields
    + JSON_ARRAY_SIZE(2)       // actuators array has 2 entries
    + 2*JSON_OBJECT_SIZE(2)    // each actuator object has 2 fields
    + 256;                     // extra for strings

    StaticJsonDocument<JSON_CAPACITY> doc;

    String macAddr = WiFi.macAddress();
    doc["mac_addr"]    = macAddr;
    doc["fw_version"]  = FW_VERSION;
    doc["model"]       = MODEL;
    doc["name"]        = NAME;
    doc["description"] = DESCRIPTION;
    doc["office_id"]   = OFFICE_ID;

    JsonArray sensors = doc.createNestedArray("sensors");
    sensors.add(JsonObject());
    sensors[0]["name"] = "DHT20";
    sensors[0]["unit"] = "°C, %";
    sensors[0]["type"] = "dht20";

    sensors.add(JsonObject());
    sensors[1]["name"] = "LDR-5528";
    sensors[1]["unit"] = "%";
    sensors[1]["type"] = "ldr";

    // sensors.add(JsonObject());
    // sensors[2]["name"] = "User Button A";
    // sensors[2]["unit"] = "boolean";
    // sensors[2]["type"] = "Digital Input";

    // sensors.add(JsonObject());
    // sensors[3]["name"] = "User Button B";
    // sensors[3]["unit"] = "boolean";
    // sensors[3]["type"] = "Digital Input";

    JsonArray actuators = doc.createNestedArray("actuators");
    actuators.add(JsonObject());
    actuators[0]["name"] = "Build-in Status LED";
    actuators[0]["type"] = "indicator";

    actuators.add(JsonObject());
    actuators[1]["name"] = "NeoPixel 4 LED strip";
    actuators[1]["type"] = "led4RGB";

    actuators.add(JsonObject());
    actuators[2]["name"] = "Mini Fan";
    actuators[2]["type"] = "fan";

    size_t json_len = measureJson(doc);
    mqtt_client.beginPublish(topicRegReq, json_len, false);
    serializeJson(doc, mqtt_client);
    mqtt_client.endPublish();
}


void connectGateway() {
    String macAddr = WiFi.macAddress();
    macAddr.replace(":", "");
    topicRegRes += macAddr;

    if (!WiFi.isConnected()) {
        Serial.println("[INFO] WiFi is not connected. Cannot connect to ThingsBoard.");
        return;
    }

    Serial.print("[MQTT] Connecting to gateway as ");
    Serial.println(NAME);

    bool connected = false;
    if (strlen(mqttUser) > 0) {
        connected = mqtt_client.connect(deviceID.c_str(), mqttUser, mqttPass);
    } else {
        connected = mqtt_client.connect(mqttUser);
    }
    if (connected) {
        Serial.println("[INFO] Gateway connected. Subscribing to topics...");
        Serial.println(topicRegRes);
        bool subSuccess = mqtt_client.subscribe(topicRegRes.c_str(), 1);
        Serial.print("[INFO] Subscription to registration response topic: ");
        Serial.println(subSuccess ? "SUCCESS" : "FAILED");

        sendRegistration();
    } else {
        int state = mqtt_client.state();
        Serial.print("Gateway connection failed, rc=");
        Serial.print(state);
        Serial.print(" (");

        switch(state) {
            case -4: Serial.print("MQTT_CONNECTION_TIMEOUT"); break;
            case -3: Serial.print("MQTT_CONNECTION_LOST"); break;
            case -2: Serial.print("MQTT_CONNECT_FAILED"); break;
            case -1: Serial.print("MQTT_DISCONNECTED"); break;
            case 1:  Serial.print("MQTT_CONNECT_BAD_PROTOCOL"); break;
            case 2:  Serial.print("MQTT_CONNECT_BAD_CLIENT_ID"); break;
            case 3:  Serial.print("MQTT_CONNECT_UNAVAILABLE"); break;
            case 4:  Serial.print("MQTT_CONNECT_BAD_CREDENTIALS"); break;
            case 5:  Serial.print("MQTT_CONNECT_UNAUTHORIZED"); break;
            default: Serial.print("UNKNOWN"); break;
        }
        Serial.println(") - retry in 2s");
    }
}


void connectGatewayTask(void *pvParameters) {
    vTaskDelay(pdMS_TO_TICKS(5000));

    mqtt_client.setBufferSize(1024);
    mqtt_client.setServer(mqttServer, mqttPort);
    mqtt_client.setKeepAlive(15);
    mqtt_client.setCallback(gateway_callback);
    Serial.println("[INFO] MQTT callback registered");

    while (!WiFi.isConnected()) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    connectGateway();

    while (true) {
        if (!mqtt_client.connected()) {
            Serial.println("[INFO] Not connected to gateway. Attempting connection...");
            vTaskDelay(pdMS_TO_TICKS(2000));
            connectGateway();
        } else {
            mqtt_client.loop();
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
