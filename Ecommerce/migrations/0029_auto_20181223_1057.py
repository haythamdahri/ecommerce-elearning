# Generated by Django 2.1.4 on 2018-12-23 10:57

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0028_auto_20181223_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='title',
            field=ckeditor.fields.RichTextField(max_length=650),
        ),
    ]