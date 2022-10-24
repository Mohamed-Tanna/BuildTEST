from django.contrib import admin
from .models import *

class AppUserAdmin(admin.ModelAdmin):

    list_display = ["user", "user_type", "is_deleted"]


admin.site.register(AppUser, admin_class=AppUserAdmin)
admin.site.register(Carrier)
admin.site.register(Broker)
admin.site.register(ShipmentParty)

