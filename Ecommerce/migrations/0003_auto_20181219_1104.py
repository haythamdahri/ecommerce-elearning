# Generated by Django 2.1.4 on 2018-12-19 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0002_auto_20181219_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=4, max_digits=6),
        ),
    ]
