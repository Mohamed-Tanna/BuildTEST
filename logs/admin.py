from django.contrib import admin
import logs.models as models

# Register your models here.


class LogAdmin(admin.ModelAdmin):
    list_display = ["id", "app_user", "action", "timestamp"]


admin.site.register(models.Log, admin_class=LogAdmin)
