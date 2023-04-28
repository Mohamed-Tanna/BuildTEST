import os
import ipaddress
import subprocess
from .base import *
from google.cloud import secretmanager


DEBUG = False

client = secretmanager.SecretManagerServiceClient()

secret_key = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('SECRET_KEY')}/versions/latest"
    }
)

SECRET_KEY = secret_key.payload.data.decode("UTF-8")

ALLOWED_HOSTS = ["app-dev.freightslayer.com"]
CSRF_TRUSTED_ORIGINS = ["https://app-dev.freightslayer.com/"]

for ip in ipaddress.IPv4Network("10.0.1.0/24"):
    ALLOWED_HOSTS.append(str(ip))

# run bash script to change pem file permission to 600 to allow django to read it
subprocess.run(["bash", os.path.join(BASE_DIR, "change_pem_file_permission.sh")])

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

email_host_password = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('EMAIL_HOST_PASS')}/versions/latest"
    }
)

EMAIL_HOST_PASSWORD = email_host_password.payload.data.decode("UTF-8")

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
connection_name = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_CONNECTION_NAME')}/versions/latest"
    }
)

database_name = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_NAME')}/versions/latest"
    }
)

database_user = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_USER')}/versions/latest"
    }
)

database_password = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_PASS')}/versions/latest"
    }
)

database_ip = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('DB_IP')}/versions/latest"
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
).payload.data.decode("UTF-8")

REDIS_HOST = f"{MEMORYSTOREIP}:6379"

MEMORYSTOREIP = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('RED_IP')}/versions/latest"
    }
).payload.data.encode("UTF-8")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(f"{MEMORYSTOREIP}", 6379)]},
    }
}

DEFENDER_REDIS_URL = f"redis://{MEMORYSTOREIP}:6379/0"

GS_BUCKET_NAME = "dev_freight_uploaded_files"