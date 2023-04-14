from .base import *
import os
from google.cloud import secretmanager

DEBUG = False

client = secretmanager.SecretManagerServiceClient()

secret_key = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('SECRET_KEY')}/versions/1"
    }
)

SECRET_KEY = secret_key.payload.data.decode("UTF-8")

ALLOWED_HOSTS = ["10.138.0.5", "app-dev.freightslayer.com"]
CSRF_TRUSTED_ORIGINS = ["https://app-dev.freightslayer.com/"]

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

email_host_password = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('EMAIL_HOST_PASS')}/versions/2"
    }
)

EMAIL_HOST_PASSWORD = email_host_password.payload.data.decode("UTF-8")

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
connection_name = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_CONNECTION_NAME')}/versions/1"
    }
)

database_name = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_NAME')}/versions/1"
    }
)

database_user = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_USER')}/versions/1"
    }
)

database_password = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_PASS')}/versions/1"
    }
)

database_ip = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_IP')}/versions/2"
    }
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "INSTANCE": connection_name.payload.data.decode("UTF-8"),
        "NAME": database_name.payload.data.decode("UTF-8"),
        "USER": database_user.payload.data.decode("UTF-8"),
        "PASSWORD": database_password.payload.data.decode("UTF-8"),
        "HOST": database_ip.payload.data.decode("UTF-8"),
        "PORT": "5432",
    }
}

MEMORYSTOREIP = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('RED_IP')}/versions/latest"
    }
).payload.data.encode("UTF-8")

REDIS_HOST = f"{MEMORYSTOREIP}:6379"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{MEMORYSTOREIP}:6379",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(f"{MEMORYSTOREIP}", 6379)]},
    }
}

DEFENDER_REDIS_URL = f"redis://{MEMORYSTOREIP}:6379/0"