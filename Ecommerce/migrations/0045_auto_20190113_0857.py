# Generated by Django 2.1.4 on 2019-01-13 08:57

import Ecommerce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0044_auto_20190112_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField(blank=True, max_length=20000, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=Ecommerce.models.PathAndRename('images/2019/01/13')),
        ),
    ]
