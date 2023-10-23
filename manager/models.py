from django.db import models
from authentication.models import Company
from django.core.validators import MinLengthValidator

class Insurance(models.Model):
    company = models.OneToOneField(
        to=Company,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    provider = models.CharField(max_length=100, null=False, blank=False)
    policy_number = models.CharField(
        max_length=20, null=False, blank=False, validators=[MinLengthValidator(8)]
    )
    type = models.CharField(max_length=100, null=False, blank=False)
    expiration_date = models.DateField(null=False, blank=False)
    premium_amount = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.provider} => {self.company.name}"
