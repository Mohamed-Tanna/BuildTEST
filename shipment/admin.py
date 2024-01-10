from django.contrib import admin
import shipment.models as models


class FacilityAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner",
        "building_name",
        "address",
    ]


class TrailerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "model",
        "max_height",
        "max_length",
        "max_width",
    ]


class LoadAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "created_at",
        "created_by",
        "shipper",
        "consignee",
        "dispatcher",
        "pick_up_date",
        "delivery_date",
        "status",
        "shipment",
    ]


class ContactAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "origin",
        "contact",
    ]


class OfferAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "party_1",
        "party_2",
        "initial",
        "current",
        "load",
        "to",
        "status",
    ]


class ShipmentAdminSite(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "created_by",
    ]


class ClaimAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "load",
        "claimant",
    ]


class ShipmentAdminAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "shipment",
        "admin",
    ]


admin.site.register(models.Facility, admin_class=FacilityAdmin)
admin.site.register(models.Trailer, admin_class=TrailerAdmin)
admin.site.register(models.Load, admin_class=LoadAdmin)
admin.site.register(models.Contact, admin_class=ContactAdmin)
admin.site.register(models.Offer, admin_class=OfferAdmin)
admin.site.register(models.Shipment, admin_class=ShipmentAdminSite)
admin.site.register(models.Claim, admin_class=ClaimAdmin)
admin.site.register(models.ShipmentAdmin, admin_class=ShipmentAdminAdmin)
