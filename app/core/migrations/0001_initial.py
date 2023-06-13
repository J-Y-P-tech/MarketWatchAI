# Generated by Django 3.2.19 on 2023-06-06 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_code', models.CharField(default='', max_length=6)),
                ('sector', models.CharField(blank=True, max_length=255, null=True)),
                ('industry', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('exchange_short_name', models.CharField(blank=True, max_length=255, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('ipo_years', models.IntegerField(blank=True, null=True)),
                ('rsi', models.IntegerField(blank=True, null=True)),
                ('rsi_date', models.DateTimeField(blank=True, null=True)),
                ('fa_score', models.IntegerField(blank=True, null=True)),
                ('fa_score_date', models.DateTimeField(blank=True, null=True)),
                ('avg_gain_loss', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('five_year_avg_dividend_yield', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
            ],
        ),
    ]