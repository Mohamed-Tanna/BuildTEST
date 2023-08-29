from django.db import models
from django.core.validators import MinLengthValidator
from authentication.models import Address

# Create your models here.


class Ticket(models.Model):
    email = models.EmailField(
        max_length=100,
        null=False,
        blank=False,
    )
    first_name = models.CharField(
        max_length=100,
        null=False,
        blank=False, 
    )
    last_name = models.CharField(
        max_length=100,
        null=False,
        blank=False, 
    )
    personal_phone = models.CharField(
        max_length=18,
        unique=True,
        null=False,
        blank=False,
        editable=False,
     )
    company_name = models.CharField(
        max_length= 100,
        null = False,
        blank=False,
    )
    company_domain = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )
    company_size = models.IntegerField(
        max_length=100,
        null=False,
        blank=False,
    )
    EIN = models.CharField(
        max_length=9,
        null=False,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(9)],
    )
    company_fax_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    company_phone_number = models.CharField(
        max_length=18,
        unique=True,
        null=False,
        blank=False,
    )
    address = models.ForeignKey(
        to=Address,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    SID_Photo = models.ImageField(
        upload_to='/',
        null=False,
        blank=False,
    )
    personal_photo = models.ImageField(
        upload_to='/',
        null=False,
        blank=False,
    )