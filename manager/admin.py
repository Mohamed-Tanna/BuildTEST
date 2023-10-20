from django.contrib import admin
from manager import models


class InsuranceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "provider",
        "type",
        "policy_number",
        "expiration_date",
        "premium_amount",
    )
    list_filter = (
        "id",
        "company",
        "provider",
    )
    search_fields = (
        "id",
        "company",
        "provider",
    )

admin.site.register(models.Insurance, InsuranceAdmin)
