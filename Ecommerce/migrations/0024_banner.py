# Generated by Django 2.1.4 on 2018-12-23 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0023_auto_20181223_0722'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=650)),
                ('description', models.CharField(max_length=100000)),
                ('price_from', models.DecimalField(decimal_places=4, max_digits=6)),
                ('external_url', models.CharField(blank=True, max_length=500, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Product')),
            ],
        ),
    ]
