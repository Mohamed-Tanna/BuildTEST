from django.db import models
from shipment.models import Load
import authentication.models as auth_models
import shipment.models as ship_models


class UploadedFile(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(
        to=auth_models.AppUser, null=False, blank=False, on_delete=models.CASCADE
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.DecimalField(max_digits=4, decimal_places=2, null=False)


class FinalAgreement(models.Model):
    shipper = models.ForeignKey(
        to=auth_models.ShipmentParty, null=False, blank=False, on_delete=models.CASCADE, related_name="final_shipper"
    )
    consignee = models.ForeignKey(
        to=auth_models.ShipmentParty, null=False, blank=False, on_delete=models.CASCADE, related_name="final_consignee"
    )
    broker = models.ForeignKey(
        to=auth_models.Broker, null=False, blank=False, on_delete=models.CASCADE
    )
    carrier = models.ForeignKey(
        to=auth_models.Carrier, null=False, blank=False, on_delete=models.CASCADE
    )
    customer = models.ForeignKey(
        to=auth_models.ShipmentParty, null=False, blank=False, on_delete=models.CASCADE, related_name="final_customer"
    )
    pick_up_location = models.ForeignKey(
        to=ship_models.Facility, null=False, blank=False, on_delete=models.CASCADE, related_name="final_pick_up"
    )
    drop_off_location = models.ForeignKey(
        to=ship_models.Facility, null=False, blank=False, on_delete=models.CASCADE, related_name="final_drop_off"
    )
    broker_company = models.ForeignKey(
        to=auth_models.Company, null=False, blank=False, on_delete=models.CASCADE, related_name="broker_company"
    )
    carrier_company = models.ForeignKey(
        to=auth_models.Company, null=False, blank=False, on_delete=models.CASCADE, related_name="carrier_company"
    )
    customer_company = models.ForeignKey(
        to=auth_models.Company, null=False, blank=False, on_delete=models.CASCADE, related_name="customer_company"
    )
    customer_offer = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    carrier_offer = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    length = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    width = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    height = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    weight = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    quantity = models.IntegerField(default=1, blank=False, null=False)
    commodity = models.CharField(max_length=255, null=False, blank=False)
    trailer_type = models.CharField(max_length=100, null=False, blank=False)
    pick_up_date = models.DateField(null=False)
    drop_off_date = models.DateField(null=False)
    issuing_date = models.DateTimeField(auto_now_add=True)
    goods_info = models.CharField(
        choices=[("Yes", "Yes"), ("No", "No")], max_length=3, null=False, default="No"
    )
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
    )
    shipment = models.ForeignKey(
        to=ship_models.Shipment, null=False, on_delete=models.CASCADE
    )
