# Generated by Django 2.1.4 on 2019-01-26 21:10

import Ecommerce.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0047_auto_20190116_2053'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(default='Created', max_length=200)),
                ('comment', models.TextField(blank=True, default='')),
                ('track_number', models.CharField(blank=True, max_length=300, null=True)),
                ('date_payment', models.DateField(blank=True, null=True)),
                ('date_complete', models.DateField(blank=True, null=True)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Profile')),
            ],
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='orderservice',
            name='profile',
        ),
        migrations.RemoveField(
            model_name='orderservice',
            name='service',
        ),
        migrations.RemoveField(
            model_name='service',
            name='brands',
        ),
        migrations.RemoveField(
            model_name='service',
            name='images',
        ),
        migrations.RemoveField(
            model_name='service',
            name='products',
        ),
        migrations.RemoveField(
            model_name='service',
            name='software',
        ),
        migrations.RemoveField(
            model_name='software',
            name='images',
        ),
        migrations.AlterField(
            model_name='banner',
            name='price_from',
            field=models.DecimalField(decimal_places=2, max_digits=16),
        ),
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.FileField(upload_to=Ecommerce.models.PathAndRename('images/2019/01/26')),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='color',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Color'),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Order'),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=15),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_from',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=16, null=True),
        ),
        migrations.DeleteModel(
            name='OrderProduct',
        ),
        migrations.DeleteModel(
            name='OrderService',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.DeleteModel(
            name='Software',
        ),
    ]