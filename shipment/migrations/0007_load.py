# Generated by Django 4.1 on 2022-11-17 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shipment", "0006_trailer"),
    ]

    operations = [
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
                ("pick_up_date", models.DateField()),
                ("delivery_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Created", "Created"),
                            ("Information Recieved", "Information Recieved"),
                            ("Confirmed", "Confirmed"),
                            ("Ready For Pick Up", "Ready For Pick Up"),
                            ("Picked Up", "Picked Up"),
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
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="authentication.broker",
                    ),
                ),
                (
                    "carrier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="authentication.carrier",
                    ),
                ),
                (
                    "consignee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="consignee",
                        to="authentication.shipmentparty",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="authentication.appuser",
                    ),
                ),
                (
                    "destination",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="destination",
                        to="shipment.facility",
                    ),
                ),
                (
                    "pick_up_location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="pick_up",
                        to="shipment.facility",
                    ),
                ),
                (
                    "shipper",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="shipper",
                        to="authentication.shipmentparty",
                    ),
                ),
            ],
        ),
    ]
