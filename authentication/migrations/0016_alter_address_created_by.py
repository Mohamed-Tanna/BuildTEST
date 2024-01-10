# Generated by Django 4.2.5 on 2023-10-20 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0015_rename_admin_company_manager"),
    ]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="created_by",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.CASCADE,
                to="authentication.appuser",
            ),
            preserve_default=False,
        ),
    ]
