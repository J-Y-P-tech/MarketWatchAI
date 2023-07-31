import os
from django.test import TestCase, SimpleTestCase, tag
from core.management.commands.populate_model_stock import *
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta, date
from core.tests.data_for_testing_populate_model_stock import *
from core.models import Stock
from django.contrib.auth.models import User
from io import StringIO
import sys


@tag('github')
class GetStockCodesTestCase(SimpleTestCase):
    """
    Test Class GetStockCodes.
    Create temporaty txt file and fill it with ticker.
    Then run get_stock_codes_from_txt() and confirm
    that the function gets the data as expected
    """

    def setUp(self):
        # Create a new text file with the specified stock codes
        with open('test_codes.txt', 'w') as f:
            f.write('TXG\n')
            f.write('MMM\n')
            f.write('ABT\n')
            f.write('ABBV\n')
            f.write('ACHC\n')
            f.write('ACN\n')
            f.write('ATVI\n')
            f.write('AYI\n')

    def tearDown(self):
        # Remove the test file after the test is complete
        os.remove('test_codes.txt')

    def test_get_stock_codes_from_txt(self):
        # Test the GetStockCodes class with the new file
        gsc = GetStockCodes(txt_file='test_codes.txt')
        gsc.get_stock_codes_from_txt()

        # Check if the list contains the specified stock codes
        self.assertIn('TXG', gsc.list_codes)
        self.assertIn('MMM', gsc.list_codes)
        self.assertIn('ABT', gsc.list_codes)
        self.assertIn('ABBV', gsc.list_codes)
        self.assertIn('ACHC', gsc.list_codes)
        self.assertIn('ACN', gsc.list_codes)
        self.assertIn('ATVI', gsc.list_codes)
        self.assertIn('AYI', gsc.list_codes)

    def test_missing_text_file(self):
        # Test the GetStockCodes class with a missing file
        with self.assertRaises(FileNotFoundError):
            gsc = GetStockCodes(txt_file='missing_file.txt')
            gsc.get_stock_codes_from_txt()

    def test_empty_text_file(self):
        # Test the GetStockCodes class with an empty file
        with open('empty_file.txt', 'w') as f:
            pass

        with self.assertRaises(ValueError):
            gsc = GetStockCodes(txt_file='empty_file.txt')
            gsc.get_stock_codes_from_txt()

        os.remove('empty_file.txt')


@tag('github')
class TestFundTechAnalysis(SimpleTestCase):
    """
    Test Class for module FundTechAnalysis.
    Tests one by one all its functions.
    """

    def setUp(self):
        self.fta = FundTechAnalysis(stock_code='TXG')

    @patch("requests.get")
    def test_get_company_info_correct(self, mock_get):
        """
        This test will mock financialmodelingprep.com/api/
        and make it return the expected data
        """
        # Mock the response from the API
        mock_response = Mock()
        mock_response.json.return_value = [{
            "sector": "Technology",
            "industry": "Software",
            "country": "USA",
            "description": "A software company",
            "exchangeShortName": "NASDAQ",
            "companyName": "ABC Inc.",
            "ipoDate": "2020-01-01"
        }]
        mock_get.return_value = mock_response

        # Create an instance of MyClass and call the function        
        self.fta.get_company_info()

        # Check that the required parameters are present in the response
        self.assertEqual(self.fta.sector, "Technology")
        self.assertEqual(self.fta.industry, "Software")
        self.assertEqual(self.fta.country, "USA")
        self.assertEqual(self.fta.description, "A software company")
        self.assertEqual(self.fta.exchange_short_name, "NASDAQ")
        self.assertEqual(self.fta.company_name, "ABC Inc.")

        # Check that the IPO date is converted to a datetime object and the IPO years are calculated correctly
        self.assertEqual(self.fta.ipo_years, datetime.now().year - 2020)

    @patch("requests.get")
    def test_get_company_info_empty_response(self, mock_get):
        """
        This test will simulate empty response from API
        get_company_info should raise ValueError exception
        """
        # Mock empty response from the API
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_get.return_value = mock_response

        # Confirm that correct Exception has been raised
        with self.assertRaises(ValueError):
            self.fta.get_company_info()

    @patch("requests.get")
    def test_get_company_info_error_in_response(self, mock_get):
        """
        Test will simulate Error message from API and confirm that
        get_company_info() will print 'get_company_info Error'
        """
        # Mock Error message in response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "Error Message"
        }
        mock_get.return_value = mock_response
        # Confirm that correct Exception has been raised
        with self.assertRaises(ValueError):
            self.fta.get_company_info()

    @patch("requests.get")
    def test_get_fundamental_analysis_score_correct(self, mock_get):
        """
        This will simulate correct return from API
        that contains Score in keys response
        Then assert that this Score value sis saved in
        fundamental_analysis_score
        """
        mock_response = Mock()
        mock_response.json.return_value = [{
            "Score": 31
        }]
        mock_get.return_value = mock_response

        self.fta.get_fundamental_analysis_score()

        # Check that the required parameters are present in the response
        self.assertEqual(self.fta.fundamental_analysis_score, 31)

    @patch("requests.get")
    def test_get_fundamental_analysis_score_empty_response(self, mock_get):
        """
        This test simulates empty response from API.
        get_fundamental_analysis_score() should raise ValueError
        """
        # Mock empty response from the API
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_get.return_value = mock_response

        # Confirm that correct Exception has been raised
        with self.assertRaises(ValueError):
            self.fta.get_fundamental_analysis_score()

    @patch("requests.get")
    def test_get_fundamental_analysis_score_error_in_response(self, mock_get):
        """
        This test simulates Error in response from API
        get_fundamental_analysis_score() should raise ValueError
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "Error Message"
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            self.fta.get_fundamental_analysis_score()

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_calc_rsi_correct(self, mock_yahoo_financials):
        """
        Simulate response from YahooFinancials historical price data
        Calculated RSI should be 58
        """

        mock_data = MOCK_DATA_RSI

        mock_yahoo_financials.return_value = mock_data

        self.fta.calc_rsi()
        self.assertEqual(self.fta.rsi, 58)

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_calc_rsi_empty_response(self, mock_yahoo_financials):
        """
        Simulates empty response from YahooFinancials
        and confirm the Exception is raised
        """
        mock_data = {'TXGFDHTCR': {'eventsData': {}}}
        mock_yahoo_financials.return_value = mock_data

        with self.assertRaises(ValueError):
            self.fta.calc_rsi()

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_calc_avg_gain_loss_correct(self, mock_yahoo_financials):
        """
        Simulates response from Yahoo Financials
        and confirms that the calculation is correct
        """
        mock_data = FIVE_YEARS_MOCK_DATA
        mock_yahoo_financials.return_value = mock_data

        self.fta.calc_avg_gain_loss()
        self.assertEqual(self.fta.avg_gain_loss, 16)

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_calc_avg_gain_loss_empty_response(self, mock_yahoo_financials):
        """
        Simulates empty response from YahooFinancials
        and confirm the Exception is raised
        """
        mock_data = {'TXGFDHTCR': {'eventsData': {}}}
        mock_yahoo_financials.return_value = mock_data

        with self.assertRaises(ValueError):
            self.fta.calc_avg_gain_loss()

    @patch("yahoofinancials.YahooFinancials.get_five_yr_avg_div_yield")
    def test_get_five_year_avg_dividend_yield_correct(self, mock_yahoo_financials):
        """
        Simulates empty response from YahooFinancials
        for five_year_avg_dividend_yield
        The return could be None (If there is no data)
        or float.
        """
        mock_data = 0.9
        mock_yahoo_financials.return_value = mock_data

        self.fta.get_five_year_avg_dividend_yield()
        self.assertEqual(self.fta.five_year_avg_dividend_yield, 0.9)


@tag('github')
class TestPopulateUpdateStock(TestCase):
    """
    Tests for class PopulateUpdateStock.
    All its functions will be tested.
    """

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_company_info_correct(self, mock_fta):
        # create a mock instance of FundTechAnalysis
        mock_fta = mock_fta.return_value

        # set some values for its attributes
        mock_fta.sector = 'Technology'
        mock_fta.industry = 'Software'
        mock_fta.country = 'USA'
        mock_fta.description = 'A leading software company'
        mock_fta.exchange_short_name = 'NASDAQ'
        mock_fta.company_name = 'Microsoft'
        mock_fta.ipo_years = 1986

        # create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')

        # call the populate_company_info method
        pus.populate_company_info()

        # get the record from the model stock
        stock = Stock.objects.get(stock_code='MSFT')

        # assert that the data from the record match the values from the mock
        self.assertEqual(stock.sector, 'Technology')
        self.assertEqual(stock.industry, 'Software')
        self.assertEqual(stock.country, 'USA')
        self.assertEqual(stock.description, 'A leading software company')
        self.assertEqual(stock.exchange_short_name, 'NASDAQ')
        self.assertEqual(stock.company_name, 'Microsoft')
        self.assertEqual(stock.ipo_years, 1986)

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_company_info_missing_parameter(self, mock_fta):
        """
        Simulate missing parameter in API response
        ipo_years
        """
        # Create a mock instance of FundTechAnalysis
        mock_fta = mock_fta.return_value

        # Add values to all attributes but ipo_years
        mock_fta.sector = 'Technology'
        mock_fta.industry = 'Software'
        mock_fta.country = 'USA'
        mock_fta.description = 'A leading software company'
        mock_fta.exchange_short_name = 'NASDAQ'
        mock_fta.company_name = 'Microsoft'

        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        # create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')

        # call the populate_company_info method
        pus.populate_company_info()

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_company_info Exception:", output)

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_company_info_error_api_response(self, mock_fta):
        """
        Simulate error in API response. This happens when maximum
        requests per day have been reached.
        The expected behaviour is print of an Exception
        """
        # Mock Error message in response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "Error Message"
        }
        mock_fta.return_value = mock_response

        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        # create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')

        # call the populate_company_info method
        pus.populate_company_info()

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_company_info Exception:", output)

    @patch('requests.get')
    def test_populate_fundamental_analysis_score_correct(self, mock_requests_get):
        """
        Test function populate_fundamental_analysis_score
        Simulate correct return from FundTechAnalysis
        Confirm that object in model Stock contains expected data
        """
        mock_response = Mock()
        mock_response.json.return_value = [{
            "Score": 31
        }]
        mock_requests_get.return_value = mock_response

        # create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')

        # call the populate_company_info method
        pus.populate_fundamental_analysis_score()

        # get the record from the model stock
        stock = Stock.objects.get(stock_code='MSFT')

        # assert that the data from the record match the values from the mock
        self.assertEqual(stock.fa_score, 31)

    @patch("requests.get")
    def test_populate_fundamental_analysis_score_empty_api_response(self, mock_requests_get):
        """
        Simulate empty APi response when running get_fundamental_analysis_score()
        Confirm that populate_fundamental_analysis_score Exception:
        exists in the print output
        Confirm that no changes have been applied to stock.fa_score
        """

        # Mock Empty response from the API
        mock_response = Mock()
        mock_response.json.return_value = None
        mock_requests_get.return_value = mock_response

        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        # Create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')
        # Create record for given stock to confirm
        # no changes have been applied to stock.fa_score
        pus._get_or_create_object_stock()

        stock = Stock.objects.get(stock_code='MSFT')
        fa_score_before = stock.fa_score

        # call the populate_company_info method
        pus.populate_fundamental_analysis_score()

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_fundamental_analysis_score Exception:", output)

        stock = Stock.objects.get(stock_code='MSFT')
        fa_score_after = stock.fa_score

        # Confirm that fa_score was not changed
        self.assertEqual(fa_score_before, fa_score_after)

    @patch("requests.get")
    def test_populate_fundamental_analysis_score_error_in_api_response(self, mock_requests_get):
        """
        Simulate Error in  APi response when running get_fundamental_analysis_score()
        This happens when API request slimit has been reached.
        Confirm that populate_fundamental_analysis_score Exception:
        exists in the print output
        Confirm that no changes have been applied to stock.fa_score
        """

        # Mock Empty response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "Error Message"
        }
        mock_requests_get.return_value = mock_response

        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        # Create an instance of PopulateUpdateStock with some stock code
        pus = PopulateUpdateStock('MSFT')
        # Create record for given stock to confirm
        # no changes have been applied to stock.fa_score
        pus._get_or_create_object_stock()

        stock = Stock.objects.get(stock_code='MSFT')
        fa_score_before = stock.fa_score

        # call the populate_company_info method
        pus.populate_fundamental_analysis_score()

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_fundamental_analysis_score Exception:", output)

        stock = Stock.objects.get(stock_code='MSFT')
        fa_score_after = stock.fa_score

        # Confirm that fa_score was not changed
        self.assertEqual(fa_score_before, fa_score_after)

    @patch("core.management.commands.populate_model_stock.FundTechAnalysis")
    def test_populate_rsi_correct(self, mock_fta):
        """
        Simulate correct RSI calculation
        Confirm that model Stock has been populated with
        correct RSI for give stock code
        """

        # create a mock instance of FundTechAnalysis
        mock_fta = mock_fta.return_value

        # set some values for its attributes
        mock_fta.rsi = 58

        # Call populate_rsi()
        pus = PopulateUpdateStock('MSFT')
        pus.populate_rsi(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='MSFT')
        # Confirm data is correct
        self.assertEqual(stock.rsi, 58)

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_populate_rsi_no_response_from_api(self, mock_yahoo_financials):
        """
        Simulates empty response from YahooFinancials
        and confirm the Exception is raised
        """
        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        mock_data = {'TXG': {'eventsData': {}}}
        mock_yahoo_financials.return_value = mock_data

        # Call populate_rsi()
        pus = PopulateUpdateStock('TXG')
        pus.populate_rsi(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='TXG')
        # Confirm that RSI is None
        self.assertEqual(stock.rsi, None)

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_rsi Exception: No response from YahooFinancials:", output)

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_avg_gain_loss_correct(self, mock_fta):
        """
        Simulate correct response from Yahoo Finance API
        and confirm that correct data is added to model Stock
        """

        # create a mock instance of FundTechAnalysis
        mock_fta = mock_fta.return_value

        # set some values for its attributes
        mock_fta.avg_gain_loss = 14

        # Call populate_rsi()
        pus = PopulateUpdateStock('TXG')
        pus.populate_avg_gain_loss(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='TXG')
        # Confirm that RSI is None
        self.assertEqual(stock.avg_gain_loss, 14)

    @patch("yahoofinancials.YahooFinancials.get_historical_price_data")
    def test_populate_avg_gain_loss_empty_response(self, mock_yahoo_financials):
        """
        Simulate Empty response form Yahoo Finance API and
        confirm that no changes have been applied to model Stock
        and system printed correct messages
        """
        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        mock_data = {'TXG': {'eventsData': {}}}
        mock_yahoo_financials.return_value = mock_data

        # Call populate_rsi()
        pus = PopulateUpdateStock('TXG')
        pus.populate_avg_gain_loss(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='TXG')
        # Confirm that RSI is None
        self.assertEqual(stock.avg_gain_loss, None)

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_avg_gain_loss Exception:", output)

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_five_year_avg_dividend_yield_correct(self, mock_fta):
        """
        Simulates correct response from Yahoo Finance API
        and confirm that record has been created in model Stock
        """
        # create a mock instance of FundTechAnalysis
        mock_fta = mock_fta.return_value

        # set some values for its attributes
        mock_fta.five_year_avg_dividend_yield = 9

        # Call populate_rsi()
        pus = PopulateUpdateStock('TXG')
        pus.populate_five_year_avg_dividend_yield(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='TXG')
        # Confirm that RSI is None
        self.assertEqual(stock.five_year_avg_dividend_yield, 9)

    @patch("yahoofinancials.YahooFinancials.get_five_yr_avg_div_yield")
    def test_populate_five_year_avg_dividend_yield_empty_response(self, mock_get_five_yr_avg_div_yield):
        """
        Simulate raise ValueError(f"Empty response from Yahoo Financials {exc}")
        and confirm that a message has been printed:
        populate_five_year_avg_dividend_yield Exception:
        """
        # Save the original stdout
        old_stdout = sys.stdout
        # Redirect stdout to a buffer
        new_stdout = StringIO()
        sys.stdout = new_stdout

        mock_get_five_yr_avg_div_yield.side_effect = Exception("Empty response from Yahoo Financials")

        # Call populate_five_year_avg_dividend_yield()
        pus = PopulateUpdateStock('TXG')
        pus.populate_five_year_avg_dividend_yield(update=True)

        # Get data from model Stock
        stock = Stock.objects.get(stock_code='TXG')
        # Confirm that five_year_avg_dividend_yield is None
        self.assertEqual(stock.five_year_avg_dividend_yield, -1)

        # Get the printed output from the buffer
        output = new_stdout.getvalue()

        # Restore the original stdout
        sys.stdout = old_stdout
        # Assert that the output contains the expected string
        self.assertIn("populate_five_year_avg_dividend_yield Exception:", output)


class TestAdminUpdateStocks(TestCase):
    """
    Test Update Stock data on admin interface
    """

    def setUp(self):
        # Create a superuser for admin access
        self.admin_user = User.objects.create_superuser(
            username='testsuperuser@example.com',
            email='testsuperuser@example.com',
            password='admin123'
        )

        # Create some initial stocks in the database
        Stock.objects.create(stock_code='AAPL')
        Stock.objects.create(stock_code='GOOG')
        Stock.objects.create(stock_code='MSFT')

    @patch('core.management.commands.populate_model_stock.FundTechAnalysis')
    def test_populate_existing_stocks(self, mock_fta):
        # Create a mock instance of FundTechAnalysis
        mock_fta_instance = mock_fta.return_value

        # set some values for its attributes
        mock_fta_instance.description = 'company description'
        mock_fta_instance.sector = 'sector'
        mock_fta_instance.industry = 'industry'
        mock_fta_instance.country = 'US'
        mock_fta_instance.exchange_short_name = 'exc'
        mock_fta_instance.company_name = 'company name'
        mock_fta_instance.ipo_years = 10
        mock_fta_instance.rsi = 40
        mock_fta_instance.fundamental_analysis_score = 30
        mock_fta_instance.avg_gain_loss = 10
        mock_fta_instance.five_year_avg_dividend_yield = 1

        # Select existing stocks
        selected_stocks = Stock.objects.filter(stock_code__in=['AAPL', 'GOOG'])

        # Mock admin request and queryset
        request = self.client.request().wsgi_request
        request.user = self.admin_user
        queryset = selected_stocks

        # Call the command through the admin interface
        Command().handle(queryset=queryset)

        # Assert that the selected stocks have been populated
        # with the correct data
        for stock in selected_stocks:
            stock.refresh_from_db()
            self.assertEqual(stock.rsi, 40)
            self.assertEqual(stock.fa_score, 30)
            self.assertEqual(stock.description, 'company description')
            self.assertEqual(stock.sector, 'sector')
            self.assertEqual(stock.industry, 'industry')
            self.assertEqual(stock.country, 'US')
            self.assertEqual(stock.exchange_short_name, 'exc')
            self.assertEqual(stock.company_name, 'company name')
            self.assertEqual(stock.ipo_years, 10)
            self.assertEqual(stock.avg_gain_loss, 10)
            self.assertEqual(stock.five_year_avg_dividend_yield, 1)

        # Confirm that the unselected stocks have no added data
        unselected_stocks = Stock.objects.filter(stock_code__in=['MSFT'])
        for stock in unselected_stocks:
            stock.refresh_from_db()
            self.assertEqual(stock.rsi, None)
            self.assertEqual(stock.fa_score, None)
            self.assertEqual(stock.description, None)
            self.assertEqual(stock.sector, None)
            self.assertEqual(stock.industry, None)
            self.assertEqual(stock.country, None)
            self.assertEqual(stock.exchange_short_name, None)
            self.assertEqual(stock.company_name, None)
            self.assertEqual(stock.ipo_years, None)
            self.assertEqual(stock.avg_gain_loss, None)
            self.assertEqual(stock.five_year_avg_dividend_yield, -1)
