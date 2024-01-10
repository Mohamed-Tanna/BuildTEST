# Generated by Django 4.2.5 on 2023-12-14 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0020_alter_company_scac"),
        ("shipment", "0014_alter_claim_commodity_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="claim",
            name="claimant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="claim_claimant",
                to="authentication.appuser",
            ),
        ),
        migrations.AlterField(
            model_name="claim",
            name="claimed_on",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="claim_claimed_on",
                to="authentication.appuser",
            ),
        ),
    ]
