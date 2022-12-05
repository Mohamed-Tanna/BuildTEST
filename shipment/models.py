from django.db import models
from authentication.models import *


class Facility(models.Model):

    owner = models.ForeignKey(
        to=User, null=False, blank=False, on_delete=models.CASCADE
    )
    building_number = models.CharField(max_length=100)
    building_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    extra_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.owner.username} => {self.building_name}"


class Trailer(models.Model):

    model = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    max_height = models.FloatField()
    max_length = models.FloatField()
    max_width = models.FloatField()


class Load(models.Model):

    created_by = models.ForeignKey(to=AppUser, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True, null=True, blank=False)
    shipper = models.ForeignKey(
        to=ShipmentParty,
        null=False,
        on_delete=models.CASCADE,
        related_name="shipper",
    )
    consignee = models.ForeignKey(
        to=ShipmentParty,
        null=False,
        on_delete=models.CASCADE,
        related_name="consignee",
    )
    broker = models.ForeignKey(to=Broker, null=True, on_delete=models.CASCADE)
    carrier = models.ForeignKey(to=Carrier, null=True, on_delete=models.CASCADE)
    pick_up_date = models.DateField(null=False)
    delivery_date = models.DateField(null=False)
    pick_up_location = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="pick_up"
    )
    destination = models.ForeignKey(
        to=Facility, on_delete=models.CASCADE, related_name="destination"
    )
    height = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False
    )
    width = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False
    )
    depth = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, null=False
    )
    weight = models.DecimalField(
        max_digits=12, decimal_places=4, default=0.00, null=False
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    goods_info = models.TextField(null=True)
    load_type = models.CharField(
        choices=[("LTL", "LTL"), ("FTL", "FTL")],
        max_length=3,
        null=False,
        default="FTL",
    )
    status = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Information Recieved", "Information Recieved"),
            ("Confirmed", "Confirmed"),
            ("Signed", "Signed"),
            ("Ready For Pick Up", "Ready For Pick Up"),
            ("Picked Up", "Picked Up"),
            ("In Transit", "In Transit"),
            ("Delivered", "Delivered"),
            ("Canceled", "Canceled"),
        ],
        max_length=20,
        null=False,
        default="Created",
    )


class Contact(models.Model):
    class Meta:
        unique_together = (("origin", "contact"),)

    origin = models.ForeignKey(
        to=User, null=True, on_delete=models.CASCADE, related_name="main"
    )
    contact = models.ForeignKey(
        to=AppUser, null=True, on_delete=models.CASCADE, related_name="contact"
    )
