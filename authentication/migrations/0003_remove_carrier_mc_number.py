# Generated by Django 4.1.7 on 2023-03-21 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_company_fax_number_company_phone_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="carrier",
            name="MC_number",
        ),
    ]