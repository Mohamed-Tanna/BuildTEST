# Generated by Django 4.1 on 2022-11-28 19:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shipment', '0014_load_depth_load_height_load_quantity_load_weight_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='app_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='main', to=settings.AUTH_USER_MODEL),
        ),
    ]