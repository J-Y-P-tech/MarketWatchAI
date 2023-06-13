from django.db import models


class Stock(models.Model):
    """
    Model to collect data about given entity(stock)
    """
    stock_code = models.CharField(max_length=8, default='')
    sector = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    exchange_short_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    ipo_years = models.IntegerField(null=True, blank=True)
    rsi = models.IntegerField(null=True, blank=True)
    rsi_date = models.DateTimeField(null=True, blank=True)
    fa_score = models.IntegerField(null=True, blank=True)
    fa_score_date = models.DateTimeField(null=True, blank=True)
    avg_gain_loss = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    five_year_avg_dividend_yield = models.DecimalField(max_digits=4, decimal_places=2,
                                                     null=True, blank=True)

    def __str__(self):
        return self.stock_code
