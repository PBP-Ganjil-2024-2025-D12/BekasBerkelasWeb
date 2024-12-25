# Generated by Django 5.1.1 on 2024-10-25 10:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_catalog', '0005_alter_car_seller'),
        ('user_dashboard', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='seller_buat_dashboard',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='user_dashboard.sellerprofile'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='car',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]