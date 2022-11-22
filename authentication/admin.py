from django.contrib import admin
from .models import *

class AppUserAdmin(admin.ModelAdmin):

    list_display = ["id", "user", "user_type", "is_deleted"]

class CarrierAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "DOT_number", "MC_number", "allowed_to_operate"]

class BrokerAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "MC_number", "allowed_to_operate"]

class ShipmentPartyAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user"]


admin.site.register(AppUser, admin_class=AppUserAdmin)
admin.site.register(Carrier, admin_class=CarrierAdmin)
admin.site.register(Broker, admin_class=BrokerAdmin)
admin.site.register(ShipmentParty, admin_class=ShipmentPartyAdmin)

