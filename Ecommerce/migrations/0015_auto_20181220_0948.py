# Generated by Django 2.1.4 on 2018-12-20 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ecommerce', '0014_auto_20181220_0948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Ecommerce.Color'),
        ),
    ]
