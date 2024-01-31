# Generated by Django 4.2.5 on 2024-01-30 21:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "shipment",
            "0033_remove_loadnote_message_or_attachments_not_default_and_more",
        ),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="loadnote",
            name="message_or_attachments_not_default",
        ),
        migrations.AddConstraint(
            model_name="loadnote",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        models.Q(("message", ""), _negated=True), ("is_created", True)
                    ),
                    models.Q(("attachments__len", 0), ("is_created", False)),
                    _connector="OR",
                ),
                name="message_or_attachments_not_default",
            ),
        ),
    ]