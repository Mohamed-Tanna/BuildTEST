# Generated by Django 4.1.5 on 2023-01-25 15:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AppUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("phone_number", models.CharField(max_length=18, unique=True)),
                (
                    "user_type",
                    models.CharField(
                        choices=[
                            ("carrier", "carrier"),
                            ("broker", "broker"),
                            ("shipment party", "shipment party"),
                        ],
                        max_length=14,
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShipmentParty",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "app_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Carrier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("DOT_number", models.CharField(max_length=8)),
                ("MC_number", models.CharField(max_length=8, null=True)),
                ("allowed_to_operate", models.BooleanField(default=False)),
                (
                    "app_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Broker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("MC_number", models.CharField(max_length=8)),
                ("allowed_to_operate", models.BooleanField(default=False)),
                (
                    "app_user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
            ],
        ),
    ]
