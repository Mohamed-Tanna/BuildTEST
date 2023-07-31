import os
from django.utils.html import strip_tags
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from shipment.models import Load, Shipment
from twilio.rest import Client
from authentication.models import AppUser
import notifications.models as models
from freightmonster.settings.base import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
)


# file deepcode ignore AttributeLoadOnNone: because these fields are not nullable 
# everytime the function is called some of the fields are supposed to be null

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


def trigger_send_sms_notification(app_user: AppUser, sid, token, phone_number, message):
    """Trigger sending sms notification to user"""
    client = Client(sid, token)
    try:
        client.messages.create(
            to=app_user.phone_number, from_=phone_number, body=message
        )
        return True
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return False


# main
def handle_notification(app_user: AppUser, action, load=None, shipment=None):
    """Handle the notification to user's prefrences"""
    try:
        notification_setting = models.NotificationSetting.objects.get(user=app_user)
    except models.NotificationSetting.DoesNotExist:
        return False
    if notification_setting.is_allowed:
        action_to_attr_mapping = {
            "add_as_contact": "add_as_contact",
            "add_to_load": "add_to_load",
            "got_offer": "got_offer",
            "offer_updated": "offer_updated",
            "add_as_shipment_admin": "add_as_shipment_admin",
            "load_status_changed": "load_status_changed",
            "RC_approved": "RC_approved",
        }

        if action in action_to_attr_mapping and getattr(
            notification_setting, action_to_attr_mapping[action]
        ):
            message, url = get_notification_msg_and_url(
                action, load, shipment, app_user
            )
            if isinstance(message, bool):
                return False

            notification = models.Notification.objects.create(
                user=app_user, message=message
            )
            notification.save()
            send_notification(app_user, message, url)
            return True
        else:
            return False
    else:
        return False


def send_notification(app_user: AppUser, message, url=None):
    """Send the notification to user's preferred method(s)"""
    notification_setting = models.NotificationSetting.objects.get(user=app_user)

    if notification_setting.methods == "email":
        trigger_send_email_notification(
            message=message,
            to=app_user.user.email,
            subject="FreightSlayer Notification",
            template="send_notification.html",
            url=url,
        )
    elif notification_setting.methods == "sms":
        trigger_send_sms_notification(
            app_user=app_user,
            sid=TWILIO_ACCOUNT_SID,
            token=TWILIO_AUTH_TOKEN,
            phone_number=TWILIO_PHONE_NUMBER,
            message=f"Hey {app_user.user.username}, " + message,
        )
    elif notification_setting.methods == "both":
        trigger_send_email_notification(
            message=message,
            to=app_user.user.email,
            subject="FreightSlayer Notification",
            template="send_notification.html",
            url=url,
        )
        trigger_send_sms_notification(
            app_user=app_user,
            sid=TWILIO_ACCOUNT_SID,
            token=TWILIO_AUTH_TOKEN,
            phone_number=TWILIO_PHONE_NUMBER,
            message=f"Hey {app_user.user.username}, " + message,
        )


def get_notification_msg_and_url(
    action,
    load: Load = None,
    shipment: Shipment = None,
    app_user: AppUser = None,
):
    """Get the notification message based on the action"""
    environment = os.getenv("ENV").lower()
    if action == "add_as_contact":
        return (
            f"You have been added as a contact by {app_user.user.username}.",
            f"https://{environment}.freightslayer.com/contact",
        )
    elif action == "add_to_load":
        roles = find_user_roles_in_a_load(load, app_user)
        return (
            f"You have been added to the load {load.name} as a {', '.join(roles)}",
            f"https://{environment}.freightslayer.com/load-details/{load.id}",
        )
    elif action == "got_offer":
        return (
            f"{load.dispatcher} has sent you an offer for the load '{load.name}'.",
            f"https://{environment}.freightslayer.com/load-details/{load.id}",
        )
    elif action == "offer_updated":
        return (
            f"{app_user.user.username} has countered your offer on the load '{load.name}'.",
            f"https://{environment}.freightslayer.com/load-details/{load.id}",
        )
    elif action == "add_as_shipment_admin":
        return (
            f"You have been added as a shipment admin by {app_user.user.username} for shipment '{shipment.name}'.",
            f"https://{environment}.freightslayer.com/shipment-details/{shipment.id}",
        )
    elif action == "load_status_changed":
        return (
            f"Kindly be informed that there has been a recent update regarding the load '{load.name}' status,  and it is now {load.status}.",
            f"https://{environment}.freightslayer.com/load-details/{load.id}",
        )
    elif action == "RC_approved":
        return (
            f"{app_user.user.username} has approved the rate confirmation for the load '{load.name}'.",
            f"https://{environment}.freightslayer.com/load-details/{load.id}",
        )


def find_user_roles_in_a_load(load: Load, app_user: AppUser):
    username = app_user.user.username
    load_parties = {
        "customer": f"{load.customer.app_user.user.username}",
        "shipper": f"{load.shipper.app_user.user.username}",
        "consignee": f"{load.consignee.app_user.user.username}",
        "dispatcher": f"{load.dispatcher.app_user.user.username}",
        "carrier": f"{load.carrier.app_user.user.username}",
    }
    roles = []
    for key, value in load_parties.items():
        if value == username:
            roles.append(key)

    return roles
