# Generated by Django 4.2.5 on 2023-10-11 14:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0014_company_domain"),
    ]

    operations = [
        migrations.RenameField(
            model_name="company",
            old_name="admin",
            new_name="manager",
        ),
    ]
