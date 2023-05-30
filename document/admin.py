from django.contrib import admin
import document.models as models

class FileAdmin(admin.ModelAdmin):
    list_display = ["name", "load", "uploaded_by"]

class FinalAgreementAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in models.FinalAgreement._meta.get_fields() if not f.editable]

admin.site.register(models.UploadedFile, admin_class=FileAdmin)
admin.site.register(models.FinalAgreement, admin_class=FinalAgreementAdmin)