# Generated by Django 4.1.10 on 2023-07-24 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notificationsetting",
            old_name="load_to_canceled",
            new_name="load_status_changed",
        ),
        migrations.RemoveField(
            model_name="notificationsetting",
            name="load_to_delivered",
        ),
        migrations.RemoveField(
            model_name="notificationsetting",
            name="load_to_in_transit",
        ),
        migrations.RemoveField(
            model_name="notificationsetting",
            name="load_to_ready_to_pickup",
        ),
        migrations.AlterField(
            model_name="notificationsetting",
            name="methods",
            field=models.CharField(
                choices=[
                    ("email", "email"),
                    ("sms", "sms"),
                    ("both", "both"),
                    ("none", "none"),
                ],
                default="email",
                max_length=5,
            ),
        ),
    ]
