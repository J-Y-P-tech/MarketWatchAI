from django.urls import reverse
from django.test import TestCase, Client
from core.models import Stock
from decimal import Decimal
from bs4 import BeautifulSoup


class TestPublic(TestCase):
    """
    Test that page Detail is accessible to registered users only
    """

    def test_detail_unregistered_users(self):
        """
        Confirm that page Detail is accessible to registered users only.
        Unregistered users should be redirected to login page.
        """
        url = reverse('detail', args=[1])
        response = self.client.get(url, follow=True)

        # User redirected to login page
        self.assertContains(response, 'accounts/login')


class TestPageDetail(TestCase):
    """
    Test that page detail covers all requirements.
    Page detail is for registered users only.
    """

    def setUp(self):
        """
        Register user for the tests
        Create test data in model Stock
        """
        self.client = Client()
        # Register user
        self.client.post(reverse('register'),
                         {
                             'first_name': '1',
                             'last_name': '1',
                             'email': '1@example.com',
                             'password': '11111',
                             'confirm_password': '11111'
                         })

        # Login registered user
        self.client.login(username='1@example.com', password='1111')

        self.stock = Stock.objects.create(
            stock_code='ABC',
            sector='Technology',
            industry='Software',
            country='USA',
            exchange_short_name='NYSE',
            company_name='ABC Inc.',
            rsi=37,
            fa_score=30,
            avg_gain_loss=5.00,
            five_year_avg_dividend_yield=3,
            description="Company description",
            ipo_years=3,
        )
        response = self.client.get(reverse('detail', args=[self.stock.id]))
        self.soup = BeautifulSoup(response.content, 'html.parser')

    def test_company_name(self):
        """
        Test that company name is displayed correct on page Detail
        """

        # Get company name form html
        company_name_in_html = self.soup.find(id='company_name').text

        # Confirm that company name in html is the same as the one in model Stock
        self.assertEqual(company_name_in_html, self.stock.company_name)

    def test_stock_code(self):
        """
        Test that stock_code is displayed correct on page Detail
        and that it points to url in Yahoo Finance containing stock-code.
        """
        # Get stock_code from html
        stock_code_in_html = self.soup.find('a', {'id': 'stock_code'}).text
        self.assertEqual(stock_code_in_html, self.stock.stock_code)

        # Get Yahoo Finance url
        stock_code_href = self.soup.find(id='stock_code').get('href')
        self.assertEqual(stock_code_href, "https://finance.yahoo.com/quote/" + self.stock.stock_code)

    def test_exchange_short_name(self):
        """
        Test that exchange_short_name is displayed correct on page Detail
        """
        # Get exchange_short_name form html
        exchange_short_name_in_html = self.soup.find(id='exchange_short_name').text
        self.assertEqual(exchange_short_name_in_html.strip(), "exchange: " +
                         self.stock.exchange_short_name)

    def test_sector(self):
        """
        Test that sector is displayed correct on page Detail
        """
        # Get sector from html
        sector_in_html = self.soup.find(id="sector").text
        self.assertEqual(sector_in_html, self.stock.sector)

    def test_industry(self):
        """
        Test that industry is displayed correct on page Detail
        """
        industry_in_html = self.soup.find(id="industry").text
        self.assertEqual(industry_in_html, self.stock.industry)

    def test_country(self):
        """
        Test that country is displayed correct on page Detail
        """
        country_in_html = self.soup.find(id="country").text
        self.assertEqual(country_in_html, self.stock.country)

    def test_description(self):
        """
        Test that description is displayed correct on page Detail
        """
        # Remove ipo_years because they share div with company description
        ipo_years_element = self.soup.find('code', {'id': 'ipo_years'})
        if ipo_years_element:
            ipo_years_element.extract()
        description_in_hmtl = self.soup.find('p', {'id': "description"}).text
        self.assertEqual(description_in_hmtl.strip(), self.stock.description)

    def test_ipo_years_display(self):
        """
        Test that if ipo_years = 1 ==> {{ stock.company_name }} is on the stock market more than 1 year
        will be displayed, if ipo_years > 1 ==> {{ stock.company_name }} is on the stock market more
        than {{ stock.ipo_years }} years will be displayed
        """
        ipo_years_in_html = self.soup.find(id="ipo_years").text

        one = self.stock.company_name + " is on the stock market more than 1 year."
        more_than_one = self.stock.company_name + " is on the stock market more than " + str(
            self.stock.ipo_years) + " years."
        if int(self.stock.ipo_years) == 1:
            self.assertEqual(ipo_years_in_html.strip(), one)
        elif int(self.stock.ipo_years) > 1:
            self.assertEqual(ipo_years_in_html.strip(), more_than_one)

    def test_fa_score(self):
        """
        Test that fa_score is displayed as expected.
        """
        fa_score_html = self.soup.find(id='fa_score').text
        self.assertEqual(fa_score_html.strip(), "FA score: " + str(self.stock.fa_score))

    def test_rsi(self):
        """
        Test that RSI is displayed correct on page Detail
        """
        rsi_in_html = self.soup.find(id="rsi").text
        self.assertEqual(rsi_in_html.strip(), "RSI: " + str(self.stock.rsi))

    def test_avg_gain_loss(self):
        """
        Test that avg_gain_loss is displayed correct on page Detail
        """
        avg_gain_loss_in_html = self.soup.find(id='avg_gain_loss').text
        self.assertEqual(avg_gain_loss_in_html.strip(), "Average gain/loss: +5.00")

    def test_five_year_avg_dividend_yield(self):
        """
        Test that field five_year_avg_dividend_yield is displayed correct on page Dashboard
        """
        five_year_avg_dividend_yield_in_html = self.soup.find(id="five_year_avg_dividend_yield").text
        self.assertEqual(five_year_avg_dividend_yield_in_html.strip(),
                         "5-Year Avg Dividend Yield: 3.00")
