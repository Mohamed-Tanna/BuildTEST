# python imports
import os
import environ
from datetime import datetime, timedelta
# third party imports
from google.cloud import storage
from google.auth import compute_engine
from google.oauth2 import service_account
from google.auth.transport import requests
# module imports
from freightmonster.settings.base import BASE_DIR
if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import GS_BUCKET_NAME
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import GS_BUCKET_NAME
else:
    from freightmonster.settings.dev import GS_BUCKET_NAME


def generate_signed_url(object_name, bucket_name=GS_BUCKET_NAME, expiration=3600):
    """Generates a signed URL for downloading an object from a bucket."""
    try:
        storage_client = get_storage_client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob("pdfs/" + object_name)
        if not blob.exists():
            raise NameError
        
        signing_creds = get_signing_creds(storage_client._credentials)
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(seconds=expiration),
            method="GET",
            credentials=signing_creds
        )

        return url

    except NameError:
        print(f"Error: Object {object_name} not found in bucket {bucket_name}")
        return None

    except (BaseException) as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return None


def upload_to_gcs(uploaded_file, bucket_name=GS_BUCKET_NAME):
    """Uploads a file to the bucket.""" 
    storage_client = get_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("pdfs/" + uploaded_file.name)
    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)


def get_storage_client():
    if os.getenv("ENV") == "LOCAL":
        env = environ.Env()
        env.read_env(os.path.join(BASE_DIR, ".local.env"))
        service_account_file_path = env("SA_CREDS")
        credentials = service_account.Credentials.from_service_account_file(
            os.path.join(BASE_DIR, service_account_file_path)
        )
        storage_client = storage.Client(credentials=credentials)
        return storage_client
    else:
        storage_client = storage.Client()
        return storage_client
    

def get_signing_creds(credentials):
    """Returns a signing credentials object."""
    auth_request = requests.Request()
    signing_credentials = compute_engine.IDTokenCredentials(auth_request, "", service_account_email=credentials.service_account_email)
    return signing_credentials