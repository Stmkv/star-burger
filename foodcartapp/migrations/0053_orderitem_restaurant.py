# Generated by Django 5.1.2 on 2024-10-29 15:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant'),
        ),
    ]
