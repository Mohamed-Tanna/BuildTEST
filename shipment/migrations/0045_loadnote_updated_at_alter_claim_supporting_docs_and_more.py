# Generated by Django 4.2.5 on 2024-02-13 22:43

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shipment", "0044_load_last_updated"),
    ]

    operations = [
        migrations.AddField(
            model_name="loadnote",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="claim",
            name="supporting_docs",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="claimnote",
            name="supporting_docs",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.TextField(), blank=True, default=list, size=None
            ),
        ),
    ]