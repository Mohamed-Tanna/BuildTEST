# Generated by Django 4.2.5 on 2023-09-25 20:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0012_company_admin_alter_appuser_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.appuser",
            ),
        ),
        migrations.AlterField(
            model_name="appuser",
            name="selected_role",
            field=models.CharField(
                choices=[
                    ("carrier", "carrier"),
                    ("dispatcher", "dispatcher"),
                    ("shipment party", "shipment party"),
                    ("manager", "manager"),
                    ("support", "support"),
                ],
                max_length=14,
            ),
        ),
        migrations.AlterField(
            model_name="appuser",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("carrier", "carrier"),
                    ("dispatcher", "dispatcher"),
                    ("shipment party", "shipment party"),
                    ("carrier-dispatcher", "carrier-dispatcher"),
                    ("dispatcher-shipment party", "dispatcher-shipment party"),
                    ("carrier-shipment party", "carrier-shipment party"),
                    (
                        "carrier-dispatcher-shipment party",
                        "carrier-dispatcher-shipment party",
                    ),
                    ("manager", "manager"),
                    ("support", "support"),
                ],
                max_length=33,
            ),
        ),
    ]
