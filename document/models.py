from django.db import models
from shipment.models import Load
import authentication.models as auth_models
from django.core.validators import MinLengthValidator


class UploadedFile(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(
        to=auth_models.AppUser, null=False, blank=False, on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.DecimalField(max_digits=4, decimal_places=2, null=False)


class FinalAgreement(models.Model):
    shipper_username = models.CharField(max_length=255, null=False, blank=False)
    shipper_full_name = models.CharField(max_length=255, null=False, blank=False)
    shipper_phone_number = models.CharField(max_length=18, null=False, blank=False)
    consignee_username = models.CharField(max_length=255, null=False, blank=False)
    consignee_full_name = models.CharField(max_length=255, null=False, blank=False)
    consignee_phone_number = models.CharField(max_length=18, null=False, blank=False)
    broker_username = models.CharField(max_length=255, null=False, blank=False)
    broker_full_name = models.CharField(max_length=255, null=False, blank=False)
    broker_phone_number = models.CharField(max_length=18, null=False, blank=False)
    broker_email = models.EmailField(max_length=255, null=False, blank=False)
    customer_username = models.CharField(max_length=255, null=False, blank=False)
    customer_full_name = models.CharField(max_length=255, null=False, blank=False)
    customer_phone_number = models.CharField(max_length=18, null=False, blank=False)
    customer_email = models.EmailField(max_length=255, null=False, blank=False)
    carrier_username = models.CharField(max_length=255, null=False, blank=False)
    carrier_full_name = models.CharField(max_length=255, null=False, blank=False)
    carrier_phone_number = models.CharField(max_length=18, null=False, blank=False)
    carrier_email = models.EmailField(max_length=255, null=False, blank=False)
    broker_company_name = models.CharField(max_length=255, null=False, blank=False)
    broker_company_address = models.CharField(max_length=255, null=False, blank=False)
    broker_company_fax_number = models.CharField(max_length=18, null=True, blank=True)
    carrier_company_name = models.CharField(max_length=255, null=False, blank=False)
    carrier_company_address = models.CharField(max_length=255, null=False, blank=False)
    carrier_company_fax_number = models.CharField(max_length=18, null=True, blank=True)
    customer_company_name = models.CharField(max_length=255, null=False, blank=False)
    customer_company_address = models.CharField(max_length=255, null=False, blank=False)
    customer_company_fax_number = models.CharField(max_length=18, null=True, blank=True)
    shipper_facility_name = models.CharField(max_length=255, null=False, blank=False)
    shipper_facility_address = models.CharField(max_length=255, null=False, blank=False)
    consignee_facility_name = models.CharField(max_length=255, null=False, blank=False)
    consignee_facility_address = models.CharField(max_length=255, null=False, blank=False)
    pickup_date = models.DateField(null=False, blank=False)
    dropoff_date = models.DateField(null=False, blank=False)
    length = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    width = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    height = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    weight = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    commodity = models.CharField(max_length=255, null=False, blank=False)
    goods_info = models.CharField(
        choices=[("Yes", "Yes"), ("No", "No")], max_length=3, null=False, default="No"
    )
    customer_offer = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    carrier_offer = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    did_customer_agree = models.BooleanField(default=False)
    customer_uuid = models.CharField(max_length=36, null=True, blank=True, validators=[MinLengthValidator(36)])
    did_carrier_agree = models.BooleanField(default=False)
    carrier_uuid = models.CharField(max_length=36, null=True, blank=True, validators=[MinLengthValidator(36)])
    generated_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    commodity = models.CharField(max_length=255, null=False, blank=False)
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
    )
    load_id = models.CharField(max_length=255, null=False, blank=False, unique=True)
