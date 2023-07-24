from django.contrib import admin
from notifications.models import Notification, NotificationSetting


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id" ,"user", "message", "seen", "created_at")


class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "is_allowed",
        "methods",
        "add_as_contact",
        "add_to_load",
        "got_offer",
        "offer_updated",
        "add_as_shipment_admin",
        "load_to_ready_to_pickup",
        "load_to_in_transit",
        "load_to_delivered",
        "load_to_canceled",
        "RC_approved",
        "updated_at",
    )


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationSetting, NotificationSettingAdmin)
