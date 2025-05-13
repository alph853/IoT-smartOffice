#!/usr/bin/env python3
import asyncio
import json
import time
import socket
import psutil
import subprocess
import signal
from aiomqtt import Client, MqttError



BROKER_HOST = "192.168.1.164"
BROKER_PORT = 1883

TELEMETRY_TOPIC = "telemetry/+"
COMMAND_FMT = "commands/{device_id}"

TOPICS = [
    ("test/topic", 0, 0),
    ("gateway/register/request", 0, 0),
    ("telemetry/+", 0, 0),
    ("gateway/register/response/+", 0, 0),
    ("gateway/control/commands/+", 0, 0),
]

def is_broker_running(host, port):
    """Check if a broker is running at the specified host and port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except:
        sock.close()
        return False


def start_broker():
    """Start the mosquitto broker if not already running."""
    if is_broker_running(BROKER_HOST, BROKER_PORT):
        print("[Gateway] Broker already running")
        return None

    proc = subprocess.Popen(
        ["mosquitto", "-c", "mosquitto.conf"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    print(f"[Gateway] Broker started (pid={proc.pid})")
    time.sleep(1)  # Give broker time to initialize
    return proc

async def main():
    # Start broker if not running
    broker_proc = start_broker()
    async def handle_messages(client: Client):
        subscription_tasks = [
            client.subscribe((topic[0], topic[1]), topic[2])
            for topic in TOPICS
        ]
        await asyncio.gather(*subscription_tasks)

        async for msg in client.messages:
            topic = msg.topic
            payload = msg.payload.decode()
            print(f"[MQTT] ⟵ {topic} : {payload}")

            # Test topic?
            # if topic.matches(TOPICS[0][0]):
            #     await client.publish(TOPICS[0][0], "OK", qos=1)
            #     print(f"[TestSvc] ➜ {TOPICS[0][0]} : OK")
            #     continue

            # Registration request?
            if topic.matches(TOPICS[1][0]):
                data = payload
                dev_id = data.get("id")
                resp_topic = TOPICS[1][0].format(device_id=dev_id)
                await client.publish(resp_topic, "OK", qos=1)
                print(f"[RegSvc] ➜ {resp_topic} : OK")
                continue

            # Telemetry?
            if topic.matches(TOPICS[2][0]):
                dev_id = topic.split("/")[1]
                cmd_topic = COMMAND_FMT.format(device_id=dev_id)
                cmd = json.dumps({"command": "toggle", "ts": int(time.time())})
                await client.publish(cmd_topic, cmd, qos=1)
                print(f"[CmdSvc] ➜ {cmd_topic} : {cmd}")

    try:
        async with Client(BROKER_HOST, BROKER_PORT) as client:
            print("[Gateway] Running... press Ctrl+C to stop")
            await client.publish("gateway/register/request", "OK", qos=1)
            await handle_messages(client)
    except MqttError as error:
        print(f"[MQTT] Error: {error}")
    finally:
        # Cleanup broker if we started it
        if broker_proc:
            print("[Gateway] Terminating broker...")
            broker_proc.send_signal(signal.SIGINT)
            try:
                broker_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                broker_proc.kill()
            print("[Gateway] Broker stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
