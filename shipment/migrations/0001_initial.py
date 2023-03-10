# Generated by Django 4.1.7 on 2023-03-09 21:38

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("authentication", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Facility",
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
                ("building_name", models.CharField(max_length=100)),
                ("extra_info", models.CharField(blank=True, max_length=255)),
                (
                    "address",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.address",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Shipment",
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
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer",
                        to="authentication.appuser",
                    ),
                ),
            ],
            options={
                "unique_together": {("created_by", "name")},
            },
        ),
        migrations.CreateModel(
            name="Trailer",
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
                ("model", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=50)),
                ("max_height", models.FloatField()),
                ("max_length", models.FloatField()),
                ("max_width", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="Load",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("pick_up_date", models.DateField()),
                ("delivery_date", models.DateField()),
                ("length", models.DecimalField(decimal_places=2, max_digits=12)),
                ("width", models.DecimalField(decimal_places=2, max_digits=12)),
                ("height", models.DecimalField(decimal_places=2, max_digits=12)),
                ("weight", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "quantity",
                    models.DecimalField(decimal_places=2, default=1, max_digits=12),
                ),
                ("commodity", models.CharField(max_length=255)),
                (
                    "goods_info",
                    models.CharField(
                        choices=[("Yes", "Yes"), ("No", "No")],
                        default="No",
                        max_length=3,
                    ),
                ),
                (
                    "load_type",
                    models.CharField(
                        choices=[("LTL", "LTL"), ("FTL", "FTL")],
                        default="FTL",
                        max_length=3,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Created", "Created"),
                            ("Awaiting Customer", "Awaiting Customer"),
                            ("Assigning Carrier", "Assigning Carrier"),
                            ("Awaiting Carrier", "Awaiting Carrier"),
                            ("Awaiting Broker", "Awaiting Broker"),
                            ("Ready For Pick Up", "Ready For Pick Up"),
                            ("In Transit", "In Transit"),
                            ("Delivered", "Delivered"),
                            ("Canceled", "Canceled"),
                        ],
                        default="Created",
                        max_length=20,
                    ),
                ),
                (
                    "broker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.broker",
                    ),
                ),
                (
                    "carrier",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.carrier",
                    ),
                ),
                (
                    "consignee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consignee",
                        to="authentication.shipmentparty",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customer",
                        to="authentication.shipmentparty",
                    ),
                ),
                (
                    "destination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="destination",
                        to="shipment.facility",
                    ),
                ),
                (
                    "pick_up_location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pick_up",
                        to="shipment.facility",
                    ),
                ),
                (
                    "shipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipment.shipment",
                    ),
                ),
                (
                    "shipper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipper",
                        to="authentication.shipmentparty",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Contact",
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
                    "contact",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contact",
                        to="authentication.appuser",
                    ),
                ),
                (
                    "origin",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="main",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ShipmentAdmin",
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
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
                (
                    "shipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shipment.shipment",
                    ),
                ),
            ],
            options={
                "unique_together": {("shipment", "admin")},
            },
        ),
        migrations.CreateModel(
            name="Offer",
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
                ("initial", models.DecimalField(decimal_places=2, max_digits=8)),
                ("current", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Accepted", "Accepted"),
                            ("Rejected", "Rejected"),
                            ("Pending", "Pending"),
                        ],
                        default="Pending",
                        max_length=8,
                    ),
                ),
                (
                    "load",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shipment.load"
                    ),
                ),
                (
                    "party_1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bidder",
                        to="authentication.broker",
                    ),
                ),
                (
                    "party_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receiver",
                        to="authentication.appuser",
                    ),
                ),
            ],
            options={
                "unique_together": {("party_1", "party_2", "load")},
            },
        ),
        migrations.AddConstraint(
            model_name="load",
            constraint=models.CheckConstraint(
                check=models.Q(("delivery_date__gt", models.F("pick_up_date"))),
                name="delivery_date_check",
            ),
        ),
        migrations.AddConstraint(
            model_name="load",
            constraint=models.CheckConstraint(
                check=models.Q(("pick_up_date__gte", datetime.date(2023, 3, 9))),
                name="pick_up_date should be greater than or equal today's date",
            ),
        ),
        migrations.AddConstraint(
            model_name="load",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("pick_up_location", models.F("destination")), _negated=True
                ),
                name="pick up location and drop off location cannot be equal",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="contact",
            unique_together={("origin", "contact")},
        ),
    ]
