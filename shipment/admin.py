from django.contrib import admin
from .models import Facility, Trailer


class FacilityAdmin(admin.ModelAdmin):

    list_display = ["owner", "building_number", "building_name", "street", "city", "state", "zip_code", "country"]

class TrailerAdmin(admin.ModelAdmin):

    list_display = ["model", "max_height", "max_length", "max_width"]

    



admin.site.register(Facility, admin_class=FacilityAdmin)
admin.site.register(Trailer, admin_class=TrailerAdmin)
