# Generated by Django 2.1.4 on 2018-12-27 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0036_auto_20181227_0851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='price_sup',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=15, null=True),
        ),
    ]