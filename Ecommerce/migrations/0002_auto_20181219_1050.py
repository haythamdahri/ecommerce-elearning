# Generated by Django 2.1.4 on 2018-12-19 10:50

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, max_length=15000, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='shop',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='software',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, max_length=60000),
        ),
    ]
