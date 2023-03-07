from google.cloud import storage

def upload_file_to_bucket(file):

    storage_client = storage.Client()

    bucket = storage_client.get_bucket('taxonomy_app_files')
    blob = bucket.blob("Test/"+file.name)
    blob.upload_from_file(file,rewind=True)