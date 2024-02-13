from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


class Ticket(models.Model):
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    personal_phone_number = models.CharField(
        max_length=18, unique=True
    )
    company_name = models.CharField(
        max_length=100, default=""
    )
    company_domain = models.CharField(
        max_length=150, default=""
    )
    company_size = models.CharField(
        choices=[
            ("1-10", "1-10"),
            ("11-50", "11-50"),
            ("51-100", "51-100"),
            (">100", ">100"),
        ],
        max_length=6,
        default="",
    )
    EIN = models.CharField(
        max_length=10,
        default=""
    )
    scac = models.CharField(
        max_length=4,
        default="",
    )
    company_fax_number = models.CharField(
        max_length=100, default=""
    )
    company_phone_number = models.CharField(
        max_length=18, default=""
    )
    address = models.CharField(max_length=255, default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")
    zip_code = models.CharField(max_length=100, default="")
    country = models.CharField(max_length=100, default="")
    insurance_provider = models.CharField(max_length=100, default="")
    insurance_policy_number = models.CharField(
        max_length=20, default=""
    )
    insurance_type = models.CharField(max_length=100, default="")
    insurance_premium_amount = models.FloatField(null=True)
    sid_photo = models.CharField(max_length=255, default="")
    personal_photo = models.CharField(
        max_length=255, default=""
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
    rejection_reason = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    handled_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['company_name'],
                condition=~Q(company_name=""),
                name='company_name_unique'
            ),
            UniqueConstraint(
                fields=['company_domain'],
                condition=~Q(company_domain=""),
                name='company_domain_unique'
            ),
            UniqueConstraint(
                fields=['EIN'],
                condition=~Q(EIN=""),
                name='EIN_unique'
            ),
            UniqueConstraint(
                fields=['company_phone_number'],
                condition=~Q(company_phone_number=""),
                name='company_phone_number_unique'
            ),
        ]
