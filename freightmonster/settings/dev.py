from .base import *
import os
import environ

DIR = os.path.join(BASE_DIR, 'freightmonster/envs/.dev.env')

dev_env = environ.Env()
dev_env.read_env(os.path.join(DIR))

DEBUG = False

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

ALLOWED_HOSTS = ["10.138.0.5", "app-dev.freightslayer.com"]
CSRF_TRUSTED_ORIGINS = ["https://app-dev.freightslayer.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "INSTANCE": dev_env("CONNECTION_NAME"),
        "NAME": dev_env("DATABASE_NAME"),
        "USER": dev_env("DATABASE_USER"),
        "PASSWORD": dev_env("DATABASE_PASS"),
        "HOST": dev_env("DATABASE_PRIVATE_IP"),
        "PORT": "5432",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(env("LOCAL_REDIS"), 6379)]},
    }
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFENDER_REDIS_URL = f"redis://{env('LOCAL_REDIS')}:6379/0"