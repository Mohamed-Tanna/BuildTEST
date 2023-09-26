from django.contrib import admin

class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "personal_phone_number",
        "company_name",
        "company_domain",
        "company_size",
        "EIN",
        "company_fax_number",
        "company_phone_number",
        "sid_photo",
        "personal_photo",
        "address",
        "city",
        "state",
        "country",
        "zip_code",
    )
    list_filter = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo", "address", "city", "state", "country", "zip_code")
    search_fields = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo", "address", "city", "state", "country", "zip_code")
    readonly_fields = ("id", "email", "first_name", "last_name", "company_name", "company_domain", "company_size", "EIN", "company_fax_number", "company_phone_number", "sid_photo", "personal_photo", "address", "city", "state", "country", "zip_code")
