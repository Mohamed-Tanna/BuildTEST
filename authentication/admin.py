from django.contrib import admin
import authentication.models as models

class AppUserAdmin(admin.ModelAdmin):

    list_display = ["id", "user", "user_type", "is_deleted"]

class CarrierAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "DOT_number", "MC_number", "allowed_to_operate"]

class BrokerAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "MC_number", "allowed_to_operate"]

class ShipmentPartyAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user"]


admin.site.register(models.AppUser, admin_class=AppUserAdmin)
admin.site.register(models.Carrier, admin_class=CarrierAdmin)
admin.site.register(models.Broker, admin_class=BrokerAdmin)
admin.site.register(models.ShipmentParty, admin_class=ShipmentPartyAdmin)

