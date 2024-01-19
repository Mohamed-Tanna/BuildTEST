# Generated by Django 4.2.5 on 2024-01-19 15:46

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0020_alter_company_scac"),
        ("shipment", "0025_alter_claimnote_supporting_docs"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoadNote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField(default="")),
                (
                    "attachments",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.TextField(), default=list, size=None
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
                (
                    "load",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shipment.load"
                    ),
                ),
                (
                    "visible_to",
                    models.ManyToManyField(
                        related_name="visible_to", to="authentication.appuser"
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="loadnote",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("message", ""), _negated=True),
                    models.Q(("attachments__exact", []), _negated=True),
                    _connector="OR",
                ),
                name="message_or_attachments_not_default",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="loadnote",
            unique_together={("load", "creator")},
        ),
    ]