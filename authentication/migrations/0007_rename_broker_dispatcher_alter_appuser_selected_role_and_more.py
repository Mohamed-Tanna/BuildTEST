# Generated by Django 4.1.7 on 2023-05-30 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipment", "0009_rename_broker_load_dispatcher_alter_load_status"),
        ("authentication", "0006_address_created_by"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Broker",
            new_name="Dispatcher",
        ),
        migrations.AlterField(
            model_name="appuser",
            name="selected_role",
            field=models.CharField(
                choices=[
                    ("carrier", "carrier"),
                    ("dispatcher", "dispatcher"),
                    ("shipment party", "shipment party"),
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
                    ("dispatcher-carrier", "dispatcher-carrier"),
                    ("dispatcher-shipment party", "dispatcher-shipment party"),
                    ("carrier-shipment party", "carrier-shipment party"),
                    (
                        "dispatcher-carrier-shipment party",
                        "dispatcher-carrier-shipment party",
                    ),
                ],
                max_length=33,
            ),
        ),
    ]
