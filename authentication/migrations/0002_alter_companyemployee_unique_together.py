# Generated by Django 4.1.7 on 2023-03-01 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="companyemployee",
            unique_together={("app_user", "company")},
        ),
    ]
