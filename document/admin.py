from django.contrib import admin
import document.models as models

class FileAdmin(admin.ModelAdmin):
    list_display = ["name", "load", "uploaded_by"]

class FinalAgreementAdmin(admin.ModelAdmin):
    list_display = ["id", "shipper_username", "carrier_username", "customer_username", "broker_username"]

admin.site.register(models.UploadedFile, admin_class=FileAdmin)
admin.site.register(models.FinalAgreement, admin_class=FinalAgreementAdmin)