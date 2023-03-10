from django.contrib import admin
import document.models as models

class FileAdmin(admin.ModelAdmin):
    list_display = ["name", "load", "uploaded_by"]

admin.site.register(models.UploadedFile, admin_class=FileAdmin)