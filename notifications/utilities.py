from django.utils.html import strip_tags
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

def trigger_send_email_notification(subject, template, to, message, url):
    """Trigger sending email notification to user"""
    username = to.split("@")[0].capitalize()
    html_content = get_template(template).render(
        {
            "username": username,
            "message": message,
            "url": url,
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
    message.attach_alternative(html_content, "text/html")
    message.content_subtype = "html"
    message.mixed_subtype = "related"
    res = message.send()
    print(res)

def trigger_send_sms_notification(user):
    """Trigger sending sms notification to user"""
    pass

def handle_notification(user, message):
    """Handle the notification to user's prefrences"""
    pass