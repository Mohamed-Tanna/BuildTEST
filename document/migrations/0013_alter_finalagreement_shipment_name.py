# Generated by Django 4.1.7 on 2023-05-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0012_finalagreement_equipment_finalagreement_load_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="finalagreement",
            name="shipment_name",
            field=models.CharField(editable=False, max_length=255),
        ),
    ]