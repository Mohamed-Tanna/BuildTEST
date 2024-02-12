import os

from document.utilities import get_storage_client
from freightmonster.utils import get_secret_manager_client, get_project_id


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class StorageClient(metaclass=SingletonMeta):
    def __init__(self):
        self.storage_client = get_storage_client()


class SecretManagerClient(metaclass=SingletonMeta):
    def __init__(self):
        self.secrete_manager_client = get_secret_manager_client()

    def get_secret_value(self, secret_name):
        return self.secrete_manager_client.access_secret_version(
            request={
                "name": f"projects/{get_project_id()}/secrets/{secret_name}/versions/latest"
            }
        ).payload.data.decode("UTF-8")
