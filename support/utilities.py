import os
from document.utilities import get_storage_client
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

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
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(
        subject=subject,
        body=html_content,
        from_email="notifications@freightslayer.com",
        to=[to],
        reply_to=["notifications@freightslayer.com"],
    )
    message.attach_alternative(text_content, "text/plain")
    message.content_subtype = "html"
    message.mixed_subtype = "related"
    res = message.send()
    print(res)