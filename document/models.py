from django.db import models
from shipment.models import Load
from authentication.models import AppUser

class UploadedFile(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    file = models.FileField(upload_to="pdfs/", null=False, blank=False)
    load = models.ForeignKey(to=Load, null=False, blank=False, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(to=AppUser, null=False, blank=False, on_delete=models.CASCADE)
