from django.urls import reverse
from django.test import TestCase, Client
from core.models import Stock
from decimal import Decimal
from bs4 import BeautifulSoup


class TestDashboardPrivate(TestCase):
    """
    Test that page dashboard is accessible only to
    registered users. If unauthorized requests come
    should be redirected to login page
    """

    def test_unauthorized_access(self):
        """
        Tests that when unregistered user tries to open page dashboard
        will be redirected to login page
        """
        url = reverse('dashboard')
        response = self.client.get(url, follow=True)

        # User redirected to login page
        self.assertContains(response, 'accounts/login')

    def test_registered_user(self):
        """
        Confirm that registered and logged users have access to page dashboard
        """
        # Register user for the test
        self.client = Client()
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

        # Open page dashboard
        response = self.client.get(reverse('dashboard'))

        # Confirm response 200 - Success
        self.assertEqual(response.status_code, 200)


class TestDashboardSearch(TestCase):
    """
    Test for search on page Dashboard
    """

    def setUp(self):
        """
        Register user for the tests
        """
        self.client = Client()
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

    def test_dashboard_search_return_values(self):
        """
        Confirm that POST request returns correct values for search variables
        """
        # Generate Search with default values
        data = {
            'fa_score': 30,
            'rsi': 40,
            'avg_gain_loss': 10,
            'five_year_avg_dividend_yield': 2
        }
        # send a post request to the form view with the data
        response = self.client.post(reverse('dashboard'), data)

        # assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that response values match tha data from POST request
        self.assertEqual(response.context.get('fa_score'), str(data['fa_score']))
        self.assertEqual(response.context.get('rsi'), str(data['rsi']))
        self.assertEqual(response.context.get('avg_gain_loss'), str(data['avg_gain_loss']))
        self.assertEqual(response.context.get('five_year_avg_dividend_yield'),
                         str(data['five_year_avg_dividend_yield']))


class TestDashboardFilter(TestCase):
    """
    Test class for filter option on page Dashboard
    """

    def setUp(self):
        """
        Register user for the tests
        Create test data in model Stock
        """
        self.client = Client()
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
            avg_gain_loss=5,
            five_year_avg_dividend_yield=3
        )
        Stock.objects.create(
            stock_code='XYZ',
            sector='Finance',
            industry='Banking',
            country='UK',
            exchange_short_name='LSE',
            company_name='XYZ Bank',
            rsi=39,
            fa_score=35,
            avg_gain_loss=12,
            five_year_avg_dividend_yield=2
        )

    def test_dashboard_filter_avg_gain_loss(self):
        """
        Test that filtering functionality works for avg_gain_loss
        Test will perform search for specific avg-gain_loss and only
        one company should be returned
        """

        # Send a POST request with filter values
        data = {
            'fa_score': 20,
            'rsi': 40,
            'avg_gain_loss': 10,
            'five_year_avg_dividend_yield': 1
        }
        # send a post request to the form view with the data
        response = self.client.post(reverse('dashboard'), data)

        # Assert that the response has a successful status code
        self.assertEqual(response.status_code, 200)
        # print(response.context)

        # Assert that the filtered stocks are displayed in the table
        self.assertContains(response, 'XYZ')
        self.assertNotContains(response, 'ABC')

    def test_dashboard_filter_fa_score(self):
        """
        Test filter on page Dashboard for fa_score
        """
        # Send a POST request with filter values
        data = {
            'rsi': 40,
            'fa_score': 30,
            'avg_gain_loss': 4,
            'five_year_avg_dividend_yield': 1
        }

        # Send POST request to page Dashboard with data as context
        response = self.client.post(reverse('dashboard'), data)

        # Confirm success code 200
        self.assertEqual(response.status_code, 200)

        # Assert that XYZ is displayed and ABC is not
        self.assertContains(response, 'XYZ')
        self.assertNotContains(response, 'ABC')

    def test_dashboard_filter_rsi(self):
        """
        Test filter on page Dashboard for rsi
        """
        # Send a POST request with filter values
        data = {
            'rsi': 38,
            'fa_score': 25,
            'avg_gain_loss': 4,
            'five_year_avg_dividend_yield': 1
        }

        # Send POST request to page Dashboard with data as context
        response = self.client.post(reverse('dashboard'), data)

        # Confirm success code 200
        self.assertEqual(response.status_code, 200)

        # Assert that company 'ABC' is part of the result and 'XYZ' is not
        self.assertContains(response, 'ABC')
        self.assertNotContains(response, 'XYZ')

    def test_dashboard_filter_five_year_avg_dividend_yield(self):
        """
        Test filter on page Dashboard for filter_five_year_avg_dividend_yield
        """
        # Send a POST request with filter values
        data = {
            'rsi': 40,
            'fa_score': 25,
            'avg_gain_loss': 4,
            'five_year_avg_dividend_yield': 2
        }

        # Send POST request to page Dashboard
        response = self.client.post(reverse('dashboard'), data)

        # Confirm success code 200
        self.assertEqual(response.status_code, 200)

        # Confirm that company 'ABC' is part of the result and 'XYZ' is not
        self.assertContains(response, 'ABC')
        self.assertNotContains(response, 'XYZ')

    def test_dashboard_url(self):
        """
        Test that stock_code from the results is url to detail page
        """
        # Generate Search with default values
        data = {
            'fa_score': 29,
            'rsi': 40,
            'avg_gain_loss': 4,
            'five_year_avg_dividend_yield': 1
        }
        # send a post request to the form view with the data
        response = self.client.post(reverse('dashboard'), data)
        # assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a", style="text-decoration:none;color:black;")

        self.assertEqual(links[0]["href"], '/' + str(self.stock.id))


class TestDashboardSort(TestCase):
    """
    Test sort functionality on page Dashboard
    """

    def setUp(self):
        self.client = Client()
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
        # Create sample Stock objects for testing
        Stock.objects.create(stock_code='ABC', sector='Technology', industry='Software',
                             country='USA', exchange_short_name='NASDAQ', company_name='ABC Inc.',
                             rsi=50, fa_score=80, avg_gain_loss=Decimal('10.5'),
                             five_year_avg_dividend_yield=Decimal('2.3'))
        Stock.objects.create(stock_code='DEF', sector='Finance', industry='Banking',
                             country='UK', exchange_short_name='LSE', company_name='DEF Bank',
                             rsi=60, fa_score=70, avg_gain_loss=Decimal('11.2'),
                             five_year_avg_dividend_yield=Decimal('1.8'))

    @staticmethod
    def get_table_rows_order(response):
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.select('table tbody tr')
        actual_order = [row.find('td').text for row in rows]

        return actual_order

    def test_sort_by_fa_score(self):
        """
        Test sort by fa_score value. The stock with less fa_score should be first
        """
        form_data = {'sort': 'fa_score'}
        response = self.client.post(reverse('dashboard'), data=form_data)
        actual_order = self.get_table_rows_order(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_order, ['DEF', 'ABC'])

    def test_sort_by_rsi(self):
        """
        Test sort by RSI. Simulate POST request like pressing RSI.
        Rows should be ordered by RSI in ascending order.
        """
        form_data = {'sort': 'rsi'}
        response = self.client.post(reverse('dashboard'), data=form_data)
        actual_order = self.get_table_rows_order(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_order, ['ABC', 'DEF'])

    def test_sort_by_avg_gain_loss(self):
        """
        Test sort by avg_gain_loss. Simulate POST request like pressing avg_gain_loss.
        Rows should be ordered by avg_gain_loss in ascending order.
        """
        form_data = {'sort': 'avg_gain_loss'}
        response = self.client.post(reverse('dashboard'), form_data)
        actual_order = self.get_table_rows_order(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_order, ['ABC', 'DEF'])

    def test_by_five_year_avg_dividend_yield(self):
        """
        Test sort by five_year_avg_dividend_yield. Simulate POST request by pressing
        five_year_avg_dividend_yield button.
        Rows should be ordered by five_year_avg_dividend_yield in ascending order
        """
        form_data = {'sort': 'five_year_avg_dividend_yield'}
        response = self.client.post(reverse('dashboard'), form_data)
        actual_order = self.get_table_rows_order(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(actual_order, ['DEF', 'ABC'])
