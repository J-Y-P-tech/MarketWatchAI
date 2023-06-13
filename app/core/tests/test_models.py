from django.test import TestCase
from core.models import Stock
from django.utils import timezone


class StockModelTest(TestCase):

    def setUp(self):
        # Create a sample stock object
        Stock.objects.create(
            stock_code="AAPL",
            sector="Technology",
            industry="Consumer Electronics",
            country="USA",
            description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, "
                        "tablets, wearables, and accessories worldwide.",
            exchange_short_name="NASDAQ",
            company_name="Apple Inc.",
            ipo_years=1980,
            rsi=65,
            rsi_date=timezone.make_aware(timezone.datetime(2021, 12, 15)),
            fa_score=8,
            fa_score_date=timezone.make_aware(timezone.datetime(2021, 12, 15)),
            avg_gain_loss=0.25,
            five_year_avg_dividend_yield=0.25
        )

    def test_stock_str(self):
        # Test the __str__ method of the stock model
        stock = Stock.objects.get(stock_code="AAPL")
        self.assertEqual(str(stock), "AAPL")

    def test_stock_fields(self):
        # Test the fields of the stock model
        stock = Stock.objects.get(stock_code="AAPL")
        self.assertEqual(stock.sector, "Technology")
        self.assertEqual(stock.industry, "Consumer Electronics")
        self.assertEqual(stock.country, "USA")
        self.assertEqual(stock.description,
                         "Apple Inc. designs, manufactures, and markets smartphones, personal computers, "
                         "tablets, wearables, and accessories worldwide.")
        self.assertEqual(stock.exchange_short_name, "NASDAQ")
        self.assertEqual(stock.company_name, "Apple Inc.")
        self.assertEqual(stock.ipo_years, 1980)
        self.assertEqual(stock.rsi, 65)
        self.assertEqual(stock.rsi_date.strftime("%Y-%m-%d"), "2021-12-15")
        self.assertEqual(stock.fa_score, 8)
        self.assertEqual(stock.fa_score_date.strftime("%Y-%m-%d"), "2021-12-15")
        self.assertEqual(stock.avg_gain_loss, 0.25)
        self.assertEqual(stock.five_year_avg_dividend_yield, 0.25)
