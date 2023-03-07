from django.db import models
from shipment.models import Load
from authentication.models import AppUser

class File(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE)
    owner = models.ForeignKey(to=AppUser, null=False, blank=False, on_delete=models.CASCADE)
