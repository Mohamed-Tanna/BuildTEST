import os
from document.utilities import get_storage_client

if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import GS_COMPANY_MANAGER_BUCKET_NAME
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import GS_COMPANY_MANAGER_BUCKET_NAME
else:
    from freightmonster.settings.local import GS_COMPANY_MANAGER_BUCKET_NAME


def upload_to_gcs(uploaded_file, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME):
    """Uploads a file to the bucket."""
    storage_client = get_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("pdfs/" + uploaded_file.name)
    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)