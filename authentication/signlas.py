from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import AppUser
from notifications.models import  NotificationSetting

@receiver(post_save, sender=AppUser)
def create_notification_setting(sender, instance, created, **kwargs):
    if created:
        NotificationSetting.objects.create(user=instance)