from django.db import models
from shipment.models import Load
import authentication.models as auth_models
import shipment.models as ship_models


class UploadedFile(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE, on_update=models.PROTECT)
    uploaded_by = models.ForeignKey(
        to=auth_models.AppUser, null=False, blank=False, on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.DecimalField(max_digits=4, decimal_places=2, null=False)


class FinalAgreement(models.Model):
    shipper_username = models.CharField(max_length=255, null=False, blank=False)
    consignee_username = models.CharField(max_length=255, null=False, blank=False)
    broker_username = models.CharField(max_length=255, null=False, blank=False)
    customer_username = models.CharField(max_length=255, null=False, blank=False)
    carrier_username = models.CharField(max_length=255, null=False, blank=False)
    broker_company_name = models.CharField(max_length=255, null=False, blank=False)
    broker_company_address = models.CharField(max_length=255, null=False, blank=False)
    carrier_company_name = models.CharField(max_length=255, null=False, blank=False)
    carrier_company_address = models.CharField(max_length=255, null=False, blank=False)
    customer_company_name = models.CharField(max_length=255, null=False, blank=False)
    customer_company_address = models.CharField(max_length=255, null=False, blank=False)
    shipper_facility_name = models.CharField(max_length=255, null=False, blank=False)
    consignee_facility_name = models.CharField(max_length=255, null=False, blank=False)
    pickup_date = models.DateField(null=False, blank=False)
    dropoff_date = models.DateField(null=False, blank=False)
    pickup_address = models.CharField(max_length=255, null=False, blank=False)
    dropoff_address = models.CharField(max_length=255, null=False, blank=False)
    commodity = models.CharField(max_length=255, null=False, blank=False)
    load_type = load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
    )
