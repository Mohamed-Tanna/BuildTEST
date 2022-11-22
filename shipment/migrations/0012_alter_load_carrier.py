# Generated by Django 4.1 on 2022-11-18 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0005_carrier_allowed_to_operate"),
        ("shipment", "0011_alter_load_broker"),
    ]

    operations = [
        migrations.AlterField(
            model_name="load",
            name="carrier",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="authentication.carrier",
            ),
        ),
    ]
