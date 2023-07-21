from rest_framework import serializers
from core.models import Stock


class StockSerializer(serializers.ModelSerializer):
    """
    This class takes input from API, validates it to make sure
    that it is secure and correct as part of validation rules.
    Then it converts it to a model in our actual database.
    """
    class Meta:
        """
        Helper class that defines what Model should be used
        and what fields to be passed
        """
        model = Stock
        # All fields will be passed except the ones we define in exclude
        # exclude = ['rsi_date', 'fa_score_date']
        fields = '__all__'
