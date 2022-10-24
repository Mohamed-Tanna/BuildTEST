from enum import unique
from django.db import models
from authentication.models import ShipmentParty


class Facility(models.Model):

    owner = models.ForeignKey(to=ShipmentParty,  null=False, blank=False, on_delete=models.DO_NOTHING)
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

