# Python imports
import os
import ipaddress
import subprocess

# Module imports
from .base import *

# Third party imports
from google.cloud import secretmanager
from google.cloud import storage


DEBUG = False

client = secretmanager.SecretManagerServiceClient()

secret_key = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('SECRET_KEY')}/versions/latest"
    }
)

SECRET_KEY = secret_key.payload.data.decode("UTF-8")

BASE_URL="https://staging.freightslayer.com"
ALLOWED_HOSTS = ["app-staging.freightslayer.com"]
CSRF_TRUSTED_ORIGINS = ["https://app-staging.freightslayer.com/"]

for ip in ipaddress.IPv4Network("10.0.1.0/24"):
    ALLOWED_HOSTS.append(str(ip))

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

email_host_password = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('EMAIL_HOST_PASS')}/versions/latest"
    }
)

EMAIL_HOST_PASSWORD = email_host_password.payload.data.decode("UTF-8")

# Database
# https://docs.djangoproject.com/en/4.latest/ref/settings/#databases
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

GS_BUCKET_NAME = "staging_freight_uploaded_files"

storage_client = storage.Client()
bucket = storage_client.bucket("freightslayer-staging-ssl-cert")
for blob in bucket.list_blobs():
    blob_name = blob.name
    blob.download_to_filename(os.path.join(BASE_DIR, blob_name))

# run bash script to change pem file permission to 600 to allow django to read it
subprocess.run(["bash", os.path.join(BASE_DIR, "change_pem_file_permission.sh")])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "INSTANCE": connection_name.payload.data.decode("UTF-8"),
        "NAME": database_name.payload.data.decode("UTF-8"),
        "USER": database_user.payload.data.decode("UTF-8"),
        "PASSWORD": database_password.payload.data.decode("UTF-8"),
        "HOST": database_ip.payload.data.decode("UTF-8"),
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
            "sslrootcert": os.path.join(BASE_DIR, "server-ca.pem"),
            "sslcert": os.path.join(BASE_DIR, "client-cert.pem"),
            "sslkey": os.path.join(BASE_DIR, "client-key.pem"),
        },
    },
}

MEMORYSTOREIP = client.access_secret_version(
    request={
        "name": f"projects/{os.getenv('PROJ_ID')}/secrets/{os.getenv('RED_IP')}/versions/latest"
    }
).payload.data.decode("UTF-8")

REDIS_HOST = f"{MEMORYSTOREIP}:6379"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(f"{MEMORYSTOREIP}", 6379)]},
    }
}

DEFENDER_REDIS_URL = f"redis://{MEMORYSTOREIP}:6379/0"
