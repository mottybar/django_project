# Generated by Django 2.1 on 2020-04-28 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200425_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='birth_date',
            field=models.CharField(max_length=100),
        ),
    ]