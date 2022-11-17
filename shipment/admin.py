from django.contrib import admin
from .models import *


class FacilityAdmin(admin.ModelAdmin):

    list_display = ["owner", "building_number", "building_name", "street", "city", "state", "zip_code", "country"]

class TrailerAdmin(admin.ModelAdmin):

    list_display = ["model", "max_height", "max_length", "max_width"]

class LoadAdmin(admin.ModelAdmin):
    
    list_display = ["created_by", "pick_up_date", "delivery_date", "status"]    



admin.site.register(Facility, admin_class=FacilityAdmin)
admin.site.register(Trailer, admin_class=TrailerAdmin)
admin.site.register(Load, admin_class=LoadAdmin)
