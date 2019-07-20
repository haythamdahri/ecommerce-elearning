# Generated by Django 2.1.4 on 2019-01-29 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0053_auto_20190129_2205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specification',
            name='description',
        ),
        migrations.AddField(
            model_name='specification',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Product'),
        ),
    ]
