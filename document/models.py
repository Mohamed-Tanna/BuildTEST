from django.db import models
from shipment.models import Load
import authentication.models as auth_models


class UploadedFile(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(
        to=auth_models.AppUser, null=False, blank=False, on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.DecimalField(max_digits=4, decimal_places=2, null=False)


class FinalAgreement(models.Model):
    shipper_username = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    shipper_full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    shipper_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    consignee_username = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    consignee_full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    consignee_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    broker_username = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    broker_full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    broker_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    broker_email = models.EmailField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_username = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    customer_email = models.EmailField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_username = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_email = models.EmailField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    broker_billing_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    broker_billing_address = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    broker_billing_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_billing_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_billing_address = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    carrier_billing_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    customer_billing_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_billing_address = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_billing_phone_number = models.CharField(
        max_length=18,
        null=False,
        blank=False,
        editable=False,
    )
    shipper_facility_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    shipper_facility_address = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    consignee_facility_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    consignee_facility_address = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    pickup_date = models.DateField(null=False, blank=False, editable=False)
    dropoff_date = models.DateField(null=False, blank=False, editable=False)
    length = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        editable=False,
    )
    width = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        editable=False,
    )
    height = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        editable=False,
    )
    weight = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=False,
        editable=False,
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1,
        editable=False,
    )
    commodity = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    goods_info = models.CharField(
        choices=[("Yes", "Yes"), ("No", "No")],
        max_length=3,
        null=False,
        default="No",
        editable=False,
    )
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
        editable=False,
    )
    equipment = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    load_id = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        editable=False,
    )
    load_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
        editable=False,
    )
    shipment_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        editable=False,
    )
    customer_offer = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=False,
        editable=False,
    )
    carrier_offer = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=False,
        editable=False,
    )
    did_customer_agree = models.BooleanField(default=False)
    customer_uuid = models.UUIDField(
        blank=True,
        null=True,
        unique=True,
        editable=False,
    )
    did_carrier_agree = models.BooleanField(default=False)
    carrier_uuid = models.UUIDField(
        blank=True,
        null=True,
        unique=True,
        editable=False,
    )
    generated_at = models.DateTimeField(auto_now_add=True, editable=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
