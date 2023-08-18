from django.contrib import admin
from .models import Stock, UserProfile, File
from .management.commands.populate_model_stock import Command
import os


class StockAdmin(admin.ModelAdmin):
    """
    This class defines what fields to be displayed in admin panel,
    which of them to be displayed as links and filters
    """
    actions = ['populate_model_stock']
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
    readonly_fields = ('rsi_date', 'fa_score_date')
    fields = (
        'stock_code', 'company_name', 'sector', 'industry', 'country', 'exchange_short_name',
        'ipo_years', 'rsi', 'rsi_date', 'fa_score', 'fa_score_date',
        'avg_gain_loss', 'five_year_avg_dividend_yield', 'description'
    )

    def populate_model_stock(self, request, queryset):
        # Call the command logic here
        Command().handle(queryset=queryset)

    populate_model_stock.short_description = "Update Model Stock Data from API"


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile


class FileAdmin(admin.ModelAdmin):
    model = File

    def delete_queryset(self, request, queryset):
        for file_obj in queryset:
            # Delete the associated file from the Docker volume
            file_path = file_obj.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete the model record
            file_obj.delete()


admin.site.register(Stock, StockAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(File, FileAdmin)
