# Generated by Django 3.2.20 on 2023-07-26 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='five_year_avg_dividend_yield',
            field=models.DecimalField(decimal_places=2, default=-1, max_digits=4),
        ),
    ]
