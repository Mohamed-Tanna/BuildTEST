# Generated by Django 4.2.5 on 2024-02-02 21:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        (
            "shipment",
            "0032_remove_loadnote_message_or_attachments_not_default_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="facility",
            options={"ordering": ["-updated_at"]},
        ),
        migrations.AddField(
            model_name="facility",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="facility",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]