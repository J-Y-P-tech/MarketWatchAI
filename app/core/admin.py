from django.contrib import admin
from .models import Stock


class StockAdmin(admin.ModelAdmin):
    """
    This class defines what fields to be displayed in admin panel,
    which of them to be displayed as links and filters
    """
    search_fields = list_display = (
        'stock_code',
        'sector',
        'industry',
        'country',
        'exchange_short_name',
        'company_name',
        'ipo_years',
        'rsi',
        'rsi_date',
        'fa_score',
        'fa_score_date',
        'avg_gain_loss',
        'five_year_avg_dividend_yield'
    )
    list_display_links = (
        'stock_code',
    )

    list_filter = (
        'sector',
        'industry',
        'country',
        'exchange_short_name',
        'ipo_years',
        'rsi',
        'fa_score',
        'avg_gain_loss'
    )
    readonly_fields = ('rsi_date', 'fa_score_date', 'avg_gain_loss', 'five_year_avg_dividend_yield')
    fields = (
        'stock_code', 'company_name', 'sector', 'industry', 'country', 'exchange_short_name',
        'ipo_years', 'rsi', 'rsi_date', 'fa_score', 'fa_score_date',
        'avg_gain_loss', 'five_year_avg_dividend_yield', 'description'
    )


admin.site.register(Stock, StockAdmin)
