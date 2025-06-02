# Gateway_Simulation

## English

### Purpose

This folder contains Python scripts to simulate IoT devices sending telemetry data via MQTT broker (Mosquitto), for testing the IoT Gateway and ThingsBoard/CoreIoT system.

---

### 1. Requirements

- Python 3.8+
- Docker & Docker Compose installed (if running broker/thingsboard via docker)
- Required Python libraries:
  ```sh
  pip install paho-mqtt
  ```

---

### 2. Start Required Services

**You must start the services with Docker before running the simulation scripts!**

#### Step 1: Start Docker Compose

Run the following command in the folder containing `docker-compose.yml` (usually this folder):

```sh
docker-compose up -d
```

- This will start Mosquitto broker, ThingsBoard Gateway, Redis, etc.
- Check if services are running:
  ```sh
  docker-compose ps
  ```

---

### 3. Run Simulation Scripts

#### A. Send data to MQTT broker (localhost)

```sh
python mqtt_localhost.py
```
- This script connects to Mosquitto broker (`localhost:1883` by default) and sends 3 sample telemetry messages.

#### B. Send data via Gateway (using host.docker.internal)

```sh
python mqtt_via_gateway.py
```
- This script simulates multiple sensors sending data via the broker, suitable when running on Windows and the broker is inside Docker.

#### C. Advanced tests

- The `test/` folder contains advanced test scripts (timeouts, multiple sensors, etc).

---

### 4. Check Data on ThingsBoard/CoreIoT

1. Log in to CoreIoT admin page (app.coreiot.io).
2. Go to **Devices** → select your gateway device (e.g., "IoT Gateway").
3. Check **Latest telemetry** for new sensor data.

---

### 5. Troubleshooting

- If the script cannot connect to the broker:
  - Check if Docker is running (`docker-compose ps`).
  - Check if port 1883 is open and correct.
  - Check the host/port configuration in the script.
- If needed, change the `host` parameter when creating the publisher object in the script.

---

### 6. Folder Structure

```
Gateway_Simulation/
│
├── docker-compose.yml
├── mqtt_config.json
├── mqtt_localhost.py
├── mqtt_pub.py
├── mqtt_via_gateway.py
├── debug/
│   └── debug_mqtt.py
└── test/
    ├── mqtt_test_timeout.py
    ├── quick_test.py
    ├── test_mqtt.py
    └── test_single.py
```

---

### 7. Contact

If you have issues running the simulation, check the steps above or contact the project developer for support.

---

---

## Tiếng Việt

### Mục đích

Thư mục này chứa các script Python để mô phỏng thiết bị IoT gửi dữ liệu (telemetry) qua MQTT broker (Mosquitto), phục vụ kiểm thử hệ thống IoT Gateway và ThingsBoard/CoreIoT.

---

### 1. Yêu cầu hệ thống

- Python 3.8+
- Đã cài đặt Docker & Docker Compose (nếu chạy broker/thingsboard bằng docker)
- Đã cài đặt các thư viện Python cần thiết:
  ```sh
  pip install paho-mqtt
  ```

---

### 2. Khởi động các dịch vụ cần thiết

**Bắt buộc phải bật các service bằng Docker trước khi chạy các script mô phỏng!**

#### Bước 1: Khởi động Docker Compose

Chạy lệnh sau trong thư mục chứa `docker-compose.yml` (thường là chính thư mục này):

```sh
docker-compose up -d
```

- Lệnh này sẽ khởi động Mosquitto broker, ThingsBoard Gateway, Redis, ...
- Kiểm tra các service đã chạy:
  ```sh
  docker-compose ps
  ```

---

### 3. Chạy các script mô phỏng gửi dữ liệu

#### A. Gửi dữ liệu lên MQTT broker (localhost)

```sh
python mqtt_localhost.py
```
- Script này sẽ kết nối tới Mosquitto broker (mặc định `localhost:1883`), gửi 3 bản tin telemetry mẫu.

#### B. Gửi dữ liệu qua Gateway (dùng host.docker.internal)

```sh
python mqtt_via_gateway.py
```
- Script này mô phỏng nhiều sensor gửi dữ liệu qua broker, phù hợp khi chạy trên Windows và broker nằm trong Docker.

#### C. Test nâng cao

- Thư mục `test/` chứa các script kiểm thử nâng cao, ví dụ timeout, nhiều sensor, v.v.

---

### 4. Kiểm tra dữ liệu trên ThingsBoard/CoreIoT

1. Đăng nhập vào trang quản trị CoreIoT (app.coreiot.io).
2. Vào mục **Devices** → chọn device gateway (ví dụ: "IoT Gateway").
3. Xem mục **Latest telemetry** để kiểm tra dữ liệu sensor vừa gửi lên.

---

### 5. Troubleshooting

- Nếu script báo lỗi không kết nối được broker:
  - Kiểm tra Docker đã chạy chưa (`docker-compose ps`).
  - Kiểm tra port 1883 đã mở và đúng chưa.
  - Kiểm tra cấu hình host/port trong script.
- Nếu cần sửa host, hãy thay đổi tham số `host` khi tạo đối tượng publisher trong script.

---

### 6. Cấu trúc thư mục

```
Gateway_Simulation/
│
├── docker-compose.yml
├── mqtt_config.json
├── mqtt_localhost.py
├── mqtt_pub.py
├── mqtt_via_gateway.py
├── debug/
│   └── debug_mqtt.py
└── test/
    ├── mqtt_test_timeout.py
    ├── quick_test.py
    ├── test_mqtt.py
    └── test_single.py
```

---

### 7. Liên hệ

Nếu gặp vấn đề khi chạy mô phỏng, hãy kiểm tra lại các bước trên hoặc liên hệ người phát triển dự án để được hỗ trợ thêm.
