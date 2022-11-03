from .base import *
from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
DIR = os.path.join(BASE_DIR, 'envs/.dev.env')

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(DIR))

DEBUG = False

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

ALLOWED_HOSTS = ["10.138.0.5", "app-dev.freightslayer.com"]
CSRF_TRUSTED_ORIGINS = ["https://app-dev.freightslayer.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "INSTANCE": env("CONNECTION_NAME"),
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASS"),
        "HOST": env("DATABASE_PRIVATE_IP"),
        "PORT": "5432",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(env("HOST_REDIS"), 6379)]},
    }
}

DEFENDER_REDIS_URL = f"redis://{env('HOST_REDIS')}:6379/0"