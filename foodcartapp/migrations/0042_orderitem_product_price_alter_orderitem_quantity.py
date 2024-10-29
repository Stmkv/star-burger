# Generated by Django 5.1.2 on 2024-10-29 09:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_rename_first_name_order_firstname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Цена'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='количество'),
        ),
    ]