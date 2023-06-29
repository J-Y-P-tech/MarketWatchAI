import os
from django.core.management.base import BaseCommand

# core.config will not be uploaded to GitHub for security purposes
# This should not affect the tests
try:
    from core.config import *
except:
    pass

from yahoofinancials import YahooFinancials
from ...models import Stock
from datetime import datetime, timedelta, date
from django.utils import timezone
import pandas as pd
import requests
import ta


class Command(BaseCommand):
    """
    Django command to populate model Stock, using Yahoo Finance APi
    and financialmodelingprep.
    Whenever we call our Command class it will call handle method.
    """

    def handle(self, *args, **options):
        gsc = GetStockCodes(txt_file='all_stock_codes.txt')
        gsc.get_stock_codes_from_txt()
        for stock_code in gsc.list_codes:
            pus = PopulateUpdateStock(stock_code=stock_code)
            pus.populate_company_info(update=False)
            pus.populate_fundamental_analysis_score(update=False)
            pus.populate_rsi(update=False)
            pus.populate_avg_gain_loss(update=False)
            pus.populate_five_year_avg_dividend_yield(update=False)


class GetStockCodes:

    def __init__(self, txt_file):
        self.txt_file = txt_file
        self.list_codes = []

    def get_stock_codes_from_txt(self):
        # Get the path to the file
        file_path = os.path.join(os.getcwd(), self.txt_file)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{self.txt_file}' does not exist.")

        # Open the file and read its contents
        with open(file_path, 'r') as f:
            # Check if the file is empty
            if os.stat(file_path).st_size == 0:
                raise ValueError(f"File '{self.txt_file}' is empty.")

            for line in f:
                # Remove leading and trailing spaces, tabs, and new lines
                code = line.strip()
                self.list_codes.append(code)

        return self.list_codes


class FundTechAnalysis:
    """"
    By give stock code(ticker), using fundamentalanalysis and yahoofinancials APIs
    get real time data for company fundamental and technical analysis
    fundamentalanalysis API requires KEY
    https://site.financialmodelingprep.com/developer/docs/
    """

    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.api_key = FUNDAMENTAL_ANALYSIS_API_KEY

        self.ipo_years = None
        self.company_name = None
        self.exchange_short_name = None
        self.description = None
        self.country = None
        self.industry = None
        self.sector = None

        self.fundamental_analysis_score = None
        self.rsi = None

        self.five_year_avg_dividend_yield = None
        self.avg_gain_loss = None

    def get_company_info(self):
        """
        Using financialmodelingprep provides information about company:
        sector, industry, country, description, exchange_short_name, company_name,
        ipo_date, ipo_years
        ::: Get this indicator once every year
        """

        # Generate the URL using string formatting
        url = f"https://financialmodelingprep.com/api/v3/profile/{self.stock_code}?" \
              f"apikey={self.api_key}"

        # Send a GET request to the URL and get the JSON response
        response = requests.get(url).json()

        # Check if the response is empty
        if not response:
            raise ValueError("API response is empty")

        if "Error Message" in response:
            raise ValueError(f"Error Message in API response: {response}")

        # Check if the required parameters are present in the response
        required_params = ["sector", "industry", "country", "description", "exchangeShortName",
                           "companyName",
                           "ipoDate"]
        if not all(param in response[0] for param in required_params):
            raise KeyError("Missing parameter in API response")

        # Extract the information from the response
        self.sector = response[0]["sector"]
        self.industry = response[0]["industry"]
        self.country = response[0]["country"]
        self.description = response[0]["description"]
        self.exchange_short_name = response[0]["exchangeShortName"]
        self.company_name = response[0]["companyName"]

        # Convert the IPO date to a datetime object
        ipo_date = datetime.strptime(response[0]["ipoDate"], "%Y-%m-%d")

        # Get the current date as a datetime object
        current_date = datetime.now()

        # Calculate the difference between the current date and the IPO date in years
        self.ipo_years = int((current_date - ipo_date).days / 365)

        return self

    def get_fundamental_analysis_score(self):
        """
        Using financialmodelingprep get Fundamental analysis rating
        Documentation url:
        https://site.financialmodelingprep.com/developer/docs/#Company-Rating
        API url:
        https://financialmodelingprep.com/api/v3/rating/AAPL?apikey=YOUR_API_KEY
        ::: Get this indicator once every day
        """

        # Generate the URL using string formatting
        url = f"https://financialmodelingprep.com/api/v3/rating/{self.stock_code}" \
              f"?apikey={self.api_key}"

        # Send a GET request to the URL and get the JSON response
        response = requests.get(url).json()

        # Check if the response is empty
        if not response:
            raise ValueError("API response is empty")

        if "Error Message" in response:
            raise ValueError("Error Message in API response")

        self.fundamental_analysis_score = 0
        for key in response[0]:
            if 'Score' in key:
                try:
                    self.fundamental_analysis_score += response[0][key]
                except ValueError as exc:
                    raise ValueError(f"Unable to calculate fundamental_analysis_rating: {exc}")

        return self

    def calc_rsi(self):
        """
        Calculates the RSI for given stock code on weekly base
        using Yahoo Finance API
        ::: Get this indicator once every day
        """

        # Get the most recent weekly close date
        last_week_close = pd.Timestamp.today().normalize() - \
                          pd.Timedelta(days=pd.Timestamp.today().dayofweek)

        # Set the start and end dates for the data download
        end_date = last_week_close - pd.Timedelta(days=1)
        start_date = end_date - pd.Timedelta(days=365)

        # Create a YahooFinancials object with the stock code
        yahoo_financials = YahooFinancials(self.stock_code)

        # Retrieve the stock data from Yahoo Finance API
        data = yahoo_financials.get_historical_price_data(start_date.strftime('%Y-%m-%d'),
                                                          end_date.strftime('%Y-%m-%d'), 'weekly')

        # Convert the data to a pandas dataframe
        try:
            stock_data = pd.DataFrame(data[self.stock_code]['prices'])
        except Exception as exc:
            raise ValueError(f"No response from YahooFinancials: {exc}")

        # Set the index to be the date column
        stock_data = stock_data.set_index(pd.DatetimeIndex(stock_data['formatted_date'].values))

        # Keep only the 'close' column
        stock_data = stock_data.loc[:, ['close']]

        # Calculate the RSI based on the weekly dataframe
        rsi_indicator = ta.momentum.RSIIndicator(stock_data['close'])

        self.rsi = int(rsi_indicator.rsi()[-1])

        return self

    def calc_avg_gain_loss(self):
        """
        Using historical data for given stock the function
        calculates SMA (Simple Moving Average)
        Then calculates how much the price increased or decreased
        on annual base for the past 5 years.
        The result is average gain or loss
        ::: Get this indicator once every year
        """

        # Create a YahooFinancials object with the stock code
        yf = YahooFinancials(self.stock_code)

        # Get the current date and the date 5 years ago
        today = date.today()
        five_years_ago = today - timedelta(days=5 * 365)

        # Format the dates as strings
        today_str = today.strftime("%Y-%m-%d")
        five_years_ago_str = five_years_ago.strftime("%Y-%m-%d")

        # Get the historical price data as a dictionary
        price_data = yf.get_historical_price_data(five_years_ago_str, today_str, "daily")

        # Convert the price data to a pandas dataframe
        try:
            df = pd.DataFrame(price_data[self.stock_code]["prices"])
        except Exception as exc:
            raise ValueError(f'Empty response from Yahoo Financials {exc}')

        df["formatted_date"] = pd.to_datetime(df["formatted_date"])
        df.set_index("formatted_date", inplace=True)

        # Calculate the simple moving average for each year
        sma = df["close"].resample("Y").mean()

        # Calculate the percentage change of the sma for each year
        pct_change = sma.pct_change()

        # Convert the percentage change to a series of gains or losses as numbers
        gains_or_losses = pct_change.apply(lambda x: x * 100)

        # Create a new dataframe that contains year and gain or loss
        result = pd.DataFrame({"year": gains_or_losses.index.year, "gain_or_loss": gains_or_losses.values})

        self.avg_gain_loss = round(result["gain_or_loss"].tail(5).mean())
        return self

    def get_five_year_avg_dividend_yield(self):
        """
        Using Yahoo Financials API get average 5 year dividend yield
        What dividend on average company paid for owning equity with value 100.
        ::: Get indicator once per year
        """

        # Create a YahooFinancials object
        yahoo_financials = YahooFinancials(self.stock_code)

        # Get the 5 Year Average Dividend Yield
        try:
            self.five_year_avg_dividend_yield = yahoo_financials.get_five_yr_avg_div_yield()
        except Exception as exc:
            raise ValueError(f"Empty response from Yahoo Financials {exc}")

        return self


class PopulateUpdateStock:
    """
    Read all objects in model Stock
    Read all lines form 'all_stock_codes.txt'
    For every ticker from txt file check if record exists.
    If it does not exist, create it.
    For every ticker:
    get_company_info() if it does not exist
    get_fundamental_analysis_score() every day
    calc_rsi() every week
    calc_avg_gain_loss() every year
    get_five_year_avg_dividend_yield() every year
    This class will be inside infinite loop
    """

    def __init__(self, stock_code):
        self.stock_code = stock_code

    def _get_or_create_object_stock(self):
        """
        Check of provided stock_code exists in model Stock
        If exists assign it to self.stock
        else create new object and assign it to self.stock
        """
        all_stocks_model = Stock.objects.all()
        stock = all_stocks_model.filter(stock_code=self.stock_code).first()
        # Company does not exist in model Stock create new object.
        if not stock:
            stock = Stock.objects.create(
                stock_code=self.stock_code
            )
        return stock

    def populate_company_info(self, update=False):
        """
        Get company data and populate it in model Stock
        """
        fta = FundTechAnalysis(stock_code=self.stock_code)
        stock = self._get_or_create_object_stock()

        # Check if company data is populated
        if not stock.sector \
                or not stock.industry \
                or not stock.country \
                or not stock.description \
                or not stock.exchange_short_name \
                or not stock.company_name \
                or not stock.ipo_years \
                or update is True:

            # Get Company data and populate it
            try:
                fta.get_company_info()

                if fta.sector is not None:
                    stock.sector = fta.sector
                if fta.industry is not None:
                    stock.industry = fta.industry
                if fta.country is not None:
                    stock.country = fta.country
                if fta.description is not None:
                    stock.description = fta.description
                if fta.exchange_short_name is not None:
                    stock.exchange_short_name = fta.exchange_short_name
                if fta.company_name is not None:
                    stock.company_name = fta.company_name
                if fta.ipo_years is not None:
                    stock.ipo_years = fta.ipo_years

                stock.save()
            except Exception as exc:
                print(f'populate_company_info Exception: {exc}')

        return self

    def populate_fundamental_analysis_score(self, update=False):
        """
        Get fa score data and populate it in model Stock
        """
        fta = FundTechAnalysis(stock_code=self.stock_code)
        stock = self._get_or_create_object_stock()

        if not stock.fa_score or update is True:

            try:
                fta.get_fundamental_analysis_score()
                if fta.fundamental_analysis_score is not None:
                    stock.fa_score = fta.fundamental_analysis_score
                    stock.fa_score_date = timezone.now()
                    stock.save()
            except Exception as exc:
                print(f'populate_fundamental_analysis_score Exception: {exc}')

        return self

    def populate_rsi(self, update=False):
        """
        Calculate weekly RSI and populate it in model Stock
        """
        fta = FundTechAnalysis(stock_code=self.stock_code)
        stock = self._get_or_create_object_stock()

        if not stock.rsi or update is True:
            try:
                fta.calc_rsi()
                if fta.rsi is not None:
                    stock.rsi = fta.rsi
                    stock.rsi_date = timezone.now()
                    stock.save()
            except Exception as exc:
                print(f'populate_rsi Exception: {exc}')

        return self

    def populate_avg_gain_loss(self, update=False):
        """
        Calculate avg_gain_loss and populate it in model Stock
        """
        fta = FundTechAnalysis(stock_code=self.stock_code)
        stock = self._get_or_create_object_stock()

        if not stock.avg_gain_loss or update is True:
            try:
                fta.calc_avg_gain_loss()
                if fta.avg_gain_loss is not None:
                    stock.avg_gain_loss = fta.avg_gain_loss
                    stock.save()
            except Exception as exc:
                print(f'populate_avg_gain_loss Exception: {exc}')

        return self

    def populate_five_year_avg_dividend_yield(self, update=False):
        """
        Get five_year_avg_dividend_yield and populate it in model Stock
        """
        fta = FundTechAnalysis(stock_code=self.stock_code)
        stock = self._get_or_create_object_stock()

        if not stock.five_year_avg_dividend_yield or update is True:
            try:
                fta.get_five_year_avg_dividend_yield()
                if fta.five_year_avg_dividend_yield is not None:
                    stock.five_year_avg_dividend_yield = fta.five_year_avg_dividend_yield
                    stock.save()
            except Exception as exc:
                print(f'populate_five_year_avg_dividend_yield Exception: {exc}')

        return self
