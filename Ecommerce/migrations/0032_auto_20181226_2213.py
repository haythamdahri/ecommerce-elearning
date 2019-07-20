# Generated by Django 2.1.4 on 2018-12-26 22:13

import Ecommerce.models
import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0031_auto_20181223_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsLetter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255)),
                ('subscribe_date', models.DateTimeField(default=datetime.datetime(2018, 12, 26, 22, 13, 20, 944537, tzinfo=utc))),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/26')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_cover',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/26')),
        ),
        migrations.AlterField(
            model_name='shop',
            name='image_profile',
            field=models.ImageField(upload_to=Ecommerce.models.PathAndRename('images/2018/12/26')),
        ),
    ]