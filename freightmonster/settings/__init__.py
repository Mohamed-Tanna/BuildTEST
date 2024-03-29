import os

from django.core.exceptions import ImproperlyConfigured

ENVS = ["LOCAL" ,"DEV", "PROD", "STAGING"]

env = os.getenv("ENV")

if env not in ENVS:
    error_message = f"The currnet 'ENV' is {env} but must be one of {ENVS}"
    raise ImproperlyConfigured(error_message)

match env:
    case "DEV":
        from .dev import *
    case "PROD":
        from .prod import *
    case "STAGING":
        from .staging import *
    case "LOCAL":
        from .local import *