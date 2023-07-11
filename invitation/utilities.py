from django.utils.html import strip_tags
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives



def send_invite(subject, template, to, inviter_email, url):
    """Send invitation to user on the request of another user(to)"""
    username = to.split("@")[0].capitalize()
    html_content = get_template(template).render(
        {
            "username": username,
            "inviter": inviter_email,
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