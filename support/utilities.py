import os
import re

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from rest_framework import status

from document.utilities import get_storage_client
from support.models import Ticket

if os.getenv("ENV") == "DEV":
    from freightmonster.settings.dev import GS_COMPANY_MANAGER_BUCKET_NAME
elif os.getenv("ENV") == "STAGING":
    from freightmonster.settings.staging import GS_COMPANY_MANAGER_BUCKET_NAME
else:
    from freightmonster.settings.local import GS_COMPANY_MANAGER_BUCKET_NAME

#TODO: refactor upload_to_gcs so you can use it in different apps
def upload_to_gcs(uploaded_file, bucket_name=GS_COMPANY_MANAGER_BUCKET_NAME):
    """Uploads a file to the bucket."""
    storage_client = get_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("pdfs/" + uploaded_file.name)
    blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)


def send_request_result(subject, template, to, password_or_reason, company_name):
    """Send whether the company manager request was approved or denied"""
    username = to.split("@")[0].capitalize()
    html_content = get_template(template).render(
        {
            "username": username,
            "password_or_reason": password_or_reason,
            "company_name": company_name,
        }
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=html_content,
        from_email="notifications@freightslayer.com",
        to=[to],
        reply_to=["notifications@freightslayer.com"],
    )
    message.attach_alternative(html_content, "text/html")
    message.content_subtype = "html"
    message.mixed_subtype = "related"
    res = message.send()
    print(res)


def is_scac_valid(scac):
    pattern = r'^[A-Z]*$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, scac) and 2 <= len(scac) <= 4:
        tickets = Ticket.objects.filter(scac=scac)
        if not tickets.exists():
            result["isValid"] = True
        else:
            result["message"] = "scac already exists"
            result["errorStatus"] = status.HTTP_409_CONFLICT
    else:
        result["message"] = "scac length should be 2-4 characters and contain upper case letters only"
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result


def ein_validation(ein):
    pattern = r'^\d{2}-\d{7}$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, ein):
        result["isValid"] = True
    else:
        result["message"] = "Invalid EIN format. It should be in the form XX-XXXXXXX where X is a digit."
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result


def min_length_validation(value, min_length):
    pattern = fr'^[\w\d-]{{{min_length},}}$'
    result = {
        "isValid": False,
        "message": "",
        "errorStatus": ""
    }
    if re.match(pattern, value):
        result["isValid"] = True
    else:
        result["message"] = (
            f"Invalid format. It should be at least {min_length} characters long and can include letters, digits, and hyphens.")
        result["errorStatus"] = status.HTTP_500_INTERNAL_SERVER_ERROR
    return result
