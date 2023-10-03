from django.contrib import admin
from support import models

class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "status",
        "created_at",
    )
    list_filter = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo")
    search_fields = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo")
    readonly_fields = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo")

admin.site.register(models.Ticket, TicketAdmin)
