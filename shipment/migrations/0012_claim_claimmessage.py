# Generated by Django 4.2.5 on 2023-12-12 17:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0020_alter_company_scac"),
        ("shipment", "0011_load_actual_delivery_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="Claim",
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
                (
                    "claimant_role",
                    models.CharField(
                        choices=[
                            ("customer", "customer"),
                            ("carrier", "carrier"),
                            ("shipper", "shipper"),
                            ("consignee", "consignee"),
                            ("dispatcher", "dispatcher"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "claimed_on_role",
                    models.CharField(
                        choices=[
                            ("customer", "customer"),
                            ("carrier", "carrier"),
                            ("shipper", "shipper"),
                            ("consignee", "consignee"),
                            ("dispatcher", "dispatcher"),
                        ],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("negotiation", "negotiation"),
                            ("resolved", "resolved"),
                            ("unresolved", "unresolved"),
                        ],
                        max_length=11,
                    ),
                ),
                ("info", models.TextField()),
                ("evidences", models.TextField(blank=True)),
                (
                    "claimant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="claim_claimant",
                        to="authentication.appuser",
                    ),
                ),
                (
                    "claimed_on",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="claim_claimed_on",
                        to="authentication.appuser",
                    ),
                ),
                (
                    "load_id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="shipment.load"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ClaimMessage",
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
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("customer", "customer"),
                            ("carrier", "carrier"),
                            ("shipper", "shipper"),
                            ("consignee", "consignee"),
                            ("dispatcher", "dispatcher"),
                        ],
                        max_length=10,
                    ),
                ),
                ("message", models.TextField()),
                ("evidences", models.TextField(blank=True)),
                (
                    "claim_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shipment.claim"
                    ),
                ),
                (
                    "claimer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="authentication.appuser",
                    ),
                ),
            ],
            options={
                "unique_together": {("claim_id", "claimer", "role")},
            },
        ),
    ]
