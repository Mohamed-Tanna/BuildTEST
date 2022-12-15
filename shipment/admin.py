from django.contrib import admin
from .models import *


class FacilityAdmin(admin.ModelAdmin):

    list_display = ["id", "owner", "building_number", "building_name", "street", "city", "state", "zip_code", "country"]

class TrailerAdmin(admin.ModelAdmin):

    list_display = ["id", "model", "max_height", "max_length", "max_width"]

class LoadAdmin(admin.ModelAdmin):
    
    list_display = ["id", "name", "created_by", "shipper", "consignee", "pick_up_date", "delivery_date", "status"]

class ContactAdmin(admin.ModelAdmin):

    list_display = ["id", "origin", "contact"]

class OfferAdmin(admin.ModelAdmin):

    list_display = ["id", "bidder", "receiver", "value"]



admin.site.register(Facility, admin_class=FacilityAdmin)
admin.site.register(Trailer, admin_class=TrailerAdmin)
admin.site.register(Load, admin_class=LoadAdmin)
admin.site.register(Contact, admin_class=ContactAdmin)
admin.site.register(Offer, admin_class=OfferAdmin)
