# Generated by Django 4.1.2 on 2022-12-05 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipment", "0020_alter_facility_extra_info_alter_load_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="load",
            name="name",
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]