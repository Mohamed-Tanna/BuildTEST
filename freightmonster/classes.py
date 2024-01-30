from document.utilities import get_storage_client


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
