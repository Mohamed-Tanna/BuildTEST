# Generated by Django 4.1.7 on 2023-06-07 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("authentication", "0008_alter_appuser_user_type"),
        ("shipment", "0009_rename_broker_load_dispatcher_alter_load_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinalAgreement",
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
                ("shipper_username", models.CharField(editable=False, max_length=255)),
                ("shipper_full_name", models.CharField(editable=False, max_length=255)),
                (
                    "shipper_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                (
                    "consignee_username",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "consignee_full_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "consignee_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                (
                    "dispatcher_username",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "dispatcher_full_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "dispatcher_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                ("dispatcher_email", models.EmailField(editable=False, max_length=255)),
                ("customer_username", models.CharField(editable=False, max_length=255)),
                (
                    "customer_full_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "customer_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                ("customer_email", models.EmailField(editable=False, max_length=255)),
                ("carrier_username", models.CharField(editable=False, max_length=255)),
                ("carrier_full_name", models.CharField(editable=False, max_length=255)),
                (
                    "carrier_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                ("carrier_email", models.EmailField(editable=False, max_length=255)),
                (
                    "dispatcher_billing_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "dispatcher_billing_address",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "dispatcher_billing_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                (
                    "carrier_billing_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "carrier_billing_address",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "carrier_billing_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                (
                    "customer_billing_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "customer_billing_address",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "customer_billing_phone_number",
                    models.CharField(editable=False, max_length=18),
                ),
                (
                    "shipper_facility_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "shipper_facility_address",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "consignee_facility_name",
                    models.CharField(editable=False, max_length=255),
                ),
                (
                    "consignee_facility_address",
                    models.CharField(editable=False, max_length=255),
                ),
                ("pickup_date", models.DateField(editable=False)),
                ("dropoff_date", models.DateField(editable=False)),
                (
                    "length",
                    models.DecimalField(
                        decimal_places=2, editable=False, max_digits=12
                    ),
                ),
                (
                    "width",
                    models.DecimalField(
                        decimal_places=2, editable=False, max_digits=12
                    ),
                ),
                (
                    "height",
                    models.DecimalField(
                        decimal_places=2, editable=False, max_digits=12
                    ),
                ),
                (
                    "weight",
                    models.DecimalField(
                        decimal_places=2, editable=False, max_digits=12
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2, default=1, editable=False, max_digits=12
                    ),
                ),
                ("commodity", models.CharField(editable=False, max_length=255)),
                (
                    "goods_info",
                    models.CharField(
                        choices=[("Yes", "Yes"), ("No", "No")],
                        default="No",
                        editable=False,
                        max_length=3,
                    ),
                ),
                (
                    "load_type",
                    models.CharField(
                        choices=[("LTL", "LTL"), ("FTL", "FTL")],
                        default="FTL",
                        editable=False,
                        max_length=3,
                    ),
                ),
                ("equipment", models.CharField(editable=False, max_length=255)),
                (
                    "load_id",
                    models.CharField(editable=False, max_length=255, unique=True),
                ),
                (
                    "load_name",
                    models.CharField(editable=False, max_length=255, unique=True),
                ),
                ("shipment_name", models.CharField(editable=False, max_length=255)),
                (
                    "customer_offer",
                    models.DecimalField(decimal_places=2, editable=False, max_digits=8),
                ),
                (
                    "carrier_offer",
                    models.DecimalField(decimal_places=2, editable=False, max_digits=8),
                ),
                ("did_customer_agree", models.BooleanField(default=False)),
                (
                    "customer_uuid",
                    models.UUIDField(
                        blank=True, editable=False, null=True, unique=True
                    ),
                ),
                ("did_carrier_agree", models.BooleanField(default=False)),
                (
                    "carrier_uuid",
                    models.UUIDField(
                        blank=True, editable=False, null=True, unique=True
                    ),
                ),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="UploadedFile",
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
                ("name", models.CharField(max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("size", models.DecimalField(decimal_places=2, max_digits=4)),
                (
                    "load",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shipment.load"
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
            ],
        ),
    ]
