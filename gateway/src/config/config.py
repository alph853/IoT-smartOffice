import psutil
import socket
import os
from typing import List, Dict

from src.domain.models import MqttTopic


class ConfigUtils:
    @staticmethod
    def get_wireless_lan_ip():
        addrs = [addr for _, addr_lst in psutil.net_if_addrs().items() for addr in addr_lst]
        addr = next(filter(lambda x: x.family in (socket.AF_INET,) and not x.address.startswith('127'), addrs), None)
        return addr.address if addr else None

    @staticmethod
    def get_mqtt_topics(topics: List[Dict]):
        return [
            MqttTopic(**topic)
            for topic in topics
        ]

    @staticmethod
    def get_config_path(config_path: str):
        path = os.path.join(os.path.dirname(__file__), config_path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        return path
