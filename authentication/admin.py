from django.contrib import admin
import authentication.models as models

class AppUserAdmin(admin.ModelAdmin):

    list_display = ["id", "user", "user_type"]

class CarrierAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "DOT_number", "allowed_to_operate"]

class BrokerAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "MC_number", "allowed_to_operate"]

class ShipmentPartyAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user"]

class CompanyAdmin(admin.ModelAdmin):

    list_display = ["id", "name", "EIN" ,"address"]

class AddressAdmin(admin.ModelAdmin):

    list_display = ["id", "address", "city", "state", "country", "zip_code"]

class CompanyEmployeeAdmin(admin.ModelAdmin):

    list_display = ["id", "company", "app_user"]

class UserTaxAdmin(admin.ModelAdmin):

    list_display = ["id", "app_user", "TIN"]


admin.site.register(models.AppUser, admin_class=AppUserAdmin)
admin.site.register(models.Carrier, admin_class=CarrierAdmin)
admin.site.register(models.Broker, admin_class=BrokerAdmin)
admin.site.register(models.ShipmentParty, admin_class=ShipmentPartyAdmin)
admin.site.register(models.Company, admin_class=CompanyAdmin)
admin.site.register(models.Address, admin_class=AddressAdmin)
admin.site.register(models.CompanyEmployee, admin_class=CompanyEmployeeAdmin)
admin.site.register(models.UserTax, admin_class=UserTaxAdmin)

