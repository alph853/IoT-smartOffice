# config.py
import json
import os
import psutil
import socket
from functools import lru_cache
from typing import Any, Dict, Union


class Config:
    def __init__(self, source: Union[str, Dict[str, Any] | Any]):
        if isinstance(source, str):
            source = os.path.join(os.path.dirname(__file__), source)
            with open(source, 'r') as f:
                data = json.load(f)
        elif isinstance(source, dict):
            data = source
        else:
            raise TypeError(
                f"Config() expects a dict or path to a JSON file, got {type(source)}"
            )

        for key, value in data.items():
            if isinstance(value, dict):
                value = Config(value)
            setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __repr__(self):
        return f"<Config {self.__dict__!r}>"

    @staticmethod
    def get_wireless_lan_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # the address doesn't need to be reachable, we just need the OS to pick a usable interface
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
