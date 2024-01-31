import os
import environ
from freightmonster.settings.base import BASE_DIR
from google.oauth2 import service_account
from google.cloud import secretmanager


def get_secret_manager_client():
    if os.getenv("ENV") == "LOCAL":
        env = environ.Env()
        env.read_env(os.path.join(BASE_DIR, "local.env"))
        service_account_file_path = env("SA_CREDS")
        credentials = service_account.Credentials.from_service_account_file(
            os.path.join(BASE_DIR, service_account_file_path)
        )
        secret_manager_client = secretmanager.SecretManagerServiceClient(
            credentials=credentials
        )
        return secret_manager_client
    else:
        secret_manager_client = secretmanager.SecretManagerServiceClient()
        return secret_manager_client


def get_project_id():
    if os.getenv("ENV") == "LOCAL":
        env = environ.Env()
        env.read_env(os.path.join(BASE_DIR, "local.env"))
        return env("PROJECT_ID")
    else:
        return os.getenv('PROJ_ID')
