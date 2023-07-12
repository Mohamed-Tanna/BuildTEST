from django.utils.html import strip_tags
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from authentication.models import User
from shipment.models import Load, Shipment


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


def get_notification_msg(
    action,
    load: Load = None,
    shipment: Shipment = None,
    user: User = None,
):
    if action == "added as a contact":
        return f"{user.username} has added you as a contact"
    elif action == "added to a load":
        roles = find_user_roles_in_a_load(load, user)
        return f"You have been added to this load {load.name} as a {', '.join(roles)}"
    elif action == "got an offer":
        return f"{load.dispatcher} has sent you an offer on this load {load.name}"
    elif action == "got a counter":
        return f"{user.username} has countered your offer on load {load.name}"
    elif action == "added as a shipment admin":
        return f"{user.username} has added you as a shipment admin on shipment {shipment.name}"
    elif action == "load is ready for pick up":
        return f"load {load.name} is now ready for pickup" 
    elif action == "load is in transit":
        return f"load {load.name} has been picked up and is now in transit" 
    elif action == "load is delivered":
        return f"load {load.name} has been delivered succefully"
    elif action == "RC is approved":
        return f"{user.username} has approved the rate confirmation on load {load.name}"
    elif action == "load is canceled":
        return f"load {load.name} has been cancelled"


def find_user_roles_in_a_load(load:Load, user:User):
    username = user.username
    load_parties = {
        "customer": f"{load.customer.app_user.user.username}",
        "shipper": f"{load.shipper.app_user.user.username}",
        "consignee": f"{load.consignee.app_user.user.username}",
        "dispatcher": f"{load.dispatcher.app_user.user.username}",
        "carrier": f"{load.carrier.app_user.user.username}"
    }
    roles = []
    for key, value in load_parties.items():
        if value == username:
            roles.append(key)
    
    return roles