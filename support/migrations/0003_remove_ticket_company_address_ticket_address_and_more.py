# Generated by Django 4.2.5 on 2023-10-20 17:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0002_rename_personal_phone_ticket_personal_phone_number_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ticket",
            name="company_address",
        ),
        migrations.AddField(
            model_name="ticket",
            name="address",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="city",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="country",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="insurance_expiration_date",
            field=models.DateField(default="1999-07-05"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="insurance_policy_number",
            field=models.CharField(
                default="",
                max_length=20,
                validators=[django.core.validators.MinLengthValidator(8)],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="insurance_premium_amount",
            field=models.FloatField(default=2000.0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="insurance_provider",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="insurance_type",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="state",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticket",
            name="zip_code",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="ticket",
            name="email",
            field=models.EmailField(max_length=100, unique=True),
        ),
    ]
