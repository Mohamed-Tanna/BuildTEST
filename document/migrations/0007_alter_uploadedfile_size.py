# Generated by Django 4.1.7 on 2023-03-15 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("document", "0006_uploadedfile_size_uploadedfile_uploaded_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadedfile",
            name="size",
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
    ]