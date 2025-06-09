import csv
import time
from datetime import datetime
import serial
import serial.tools.list_ports
import threading

# 1) Configuration
BAUDRATE     = 115200
OUTPUT_FILE  = 'log_dry_.csv'
PORT_FILTER  = 'USB'   # substring to identify your device ports, e.g. 'USB' or 'ACM' on Linux, 'COM' on Windows
READ_TIMEOUT = 1.0     # seconds

# 2) Helper to detect ports matching your devices
def list_device_ports(filter_str=PORT_FILTER):
    return [
        p.device
        for p in serial.tools.list_ports.comports()
        if filter_str in p.description
    ]

# 3) Worker thread: read lines from one port and log them
def serial_worker(port_name):
    try:
        ser = serial.Serial(port_name, BAUDRATE, timeout=READ_TIMEOUT)
        print(f"[+] Listening on {port_name}")
    except Exception as e:
        print(f"[!] Could not open {port_name}: {e}")
        return

    with open(OUTPUT_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # write header if file is empty
        if csvfile.tell() == 0:
            writer.writerow(['timestamp', 'data'])
        while True:
            try:
                raw = ser.readline().decode('utf-8', errors='replace').strip()
                if not raw:
                    continue
                ts = datetime.now().isoformat(sep=' ')
                writer.writerow([ts, raw])
                csvfile.flush()
                print(f"{ts} | {raw}")
            except Exception as e:
                print(f"[!] Read error on {port_name}: {e}")
                break
    ser.close()

# 4) Main: spawn one thread per device port
def main():
    ports = list_device_ports()
    if not ports:
        print("No matching serial ports found.")
        return

    threads = []
    for port in ports:
        t = threading.Thread(target=serial_worker, args=(port,), daemon=True)
        t.start()
        threads.append(t)

    # keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping logging.")

if __name__ == '__main__':
    main()
