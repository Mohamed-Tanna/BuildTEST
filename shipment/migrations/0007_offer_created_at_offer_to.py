# Generated by Django 4.1.7 on 2023-05-23 19:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("shipment", "0006_load_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="offer",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="offer",
            name="to",
            field=models.CharField(
                choices=[("customer", "customer"), ("carrier", "carrier")],
                default="customer",
                max_length=8,
            ),
        ),
    ]
