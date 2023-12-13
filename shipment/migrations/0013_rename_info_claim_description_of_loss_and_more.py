# Generated by Django 4.2.5 on 2023-12-13 16:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("shipment", "0012_claim_claimmessage"),
    ]

    operations = [
        migrations.RenameField(
            model_name="claim",
            old_name="info",
            new_name="description_of_loss",
        ),
        migrations.AddField(
            model_name="claim",
            name="Date_of_loss",
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="claim",
            name="commodity_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="claim",
            name="commodity_type",
            field=models.CharField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="claim",
            name="type_of_loss",
            field=models.CharField(
                choices=[
                    ("damaged", "damaged"),
                    ("lost", "lost"),
                    ("delayed", "delayed"),
                ],
                default="lost",
                max_length=7,
            ),
            preserve_default=False,
        ),
    ]
