# Generated by Django 4.1.7 on 2023-03-09 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadedfile",
            name="file",
            field=models.FileField(upload_to="pdfs/"),
        ),
    ]