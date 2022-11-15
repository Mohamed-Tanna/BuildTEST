from django.db import models
from authentication.models import *


class Facility(models.Model):

    owner = models.ForeignKey(
        to=ShipmentParty, null=False, blank=False, on_delete=models.DO_NOTHING
    )
    building_number = models.CharField(max_length=100)
    building_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    extra_info = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.owner.app_user.user.username} => {self.building_name}"


class Trailer(models.Model):

    model = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    max_height = models.FloatField()
    max_length = models.FloatField()
    max_width = models.FloatField()


class Load(models.Model):

    owner = models.ForeignKey(to=AppUser, null=False)
    shipper = models.ForeignKey(to=ShipmentParty, on_delete=models.DO_NOTHING)
    consignee = models.ForeignKey(to=ShipmentParty, on_delete=models.DO_NOTHING)
    broker = models.ForeignKey(to=Broker, on_delete=models.DO_NOTHING)
    carrier = models.ForeignKey(to=Carrier, on_delete=models.DO_NOTHING)
    pick_up_date = models.DateField(null=False)
    delivery_date = models.DateField(null=False)
    pick_up_location = models.ForeignKey(to=Facility, on_delete=models.DO_NOTHING)
    destination = models.ForeignKey(to=Facility, on_delete=models.DO_NOTHING)
    status = models.CharField(
        choices=[
            ("Created", "Created"),
            ("Information Recieved", "Information Recieved"),
            ("Confirmed", "Confirmed"),
            ("Ready For Pick Up", "Ready For Pick Up"),
            ("Picked Up", "Picked Up"),
            ("In Transit", "In Transit"),
            ("Delivered", "Delivered"),
            ("Canceled", "Canceled")
        ],
        max_length=20,
        null=False,
    )
