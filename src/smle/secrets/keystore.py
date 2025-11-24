import os

from dotenv import dotenv_values

class KeyStore:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._keys = dotenv_values(".env")

    def get_key(self, service:str):
        if service in self._keys.keys():
            return self._keys[service]
        else:
            raise Exception("No valid key found in .env")