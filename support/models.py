from django.db import models
from django.core.validators import MinLengthValidator
from authentication.models import Address


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
    personal_phone_number = models.CharField(
        max_length=18,
        unique=True,
        null=False,
        blank=False,
        editable=False,
    )
    company_name = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )
    company_domain = models.CharField(
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    company_size = models.CharField(
        choices=[("1-10", "1-10"), ("11-50", "11-50"), ("51-100", "51-100"), (">100", ">100")],
        max_length=6,
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
    company_address = models.ForeignKey(
        to=Address,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    sid_photo = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    personal_photo = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    status = models.CharField(
        max_length=8,
        null=False,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Denied", "Denied"),
        ],
        default="Pending",
    )
    rejection_reason = models.TextField(
        default="",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    handled_at = models.DateTimeField(
        auto_now=True,
    )