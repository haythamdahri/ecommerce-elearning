# Generated by Django 2.1.4 on 2018-12-22 06:04

import Ecommerce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0018_auto_20181220_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/22')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_cover',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/22')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_profile',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/22')),
        ),
    ]
