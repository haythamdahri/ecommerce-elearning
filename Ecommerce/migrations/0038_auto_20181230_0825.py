# Generated by Django 2.1.4 on 2018-12-30 08:25

import Ecommerce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0037_auto_20181227_1031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='end_date',
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/30')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_cover',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/30')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_profile',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/30')),
        ),
    ]
