# Generated by Django 4.2.5 on 2023-10-23 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0016_alter_address_created_by"),
        ("manager", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="insurance",
            name="company",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="authentication.company"
            ),
        ),
    ]
