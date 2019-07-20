# Generated by Django 2.1.4 on 2018-12-19 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0005_brand_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.CharField(blank=True, max_length=450, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, to='Ecommerce.Product'),
        ),
    ]
