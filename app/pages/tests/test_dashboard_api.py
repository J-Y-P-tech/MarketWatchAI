from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models import Stock
from decimal import Decimal


class PrivateDashboardApiTests(APITestCase):
    """
    Test Dashboard API. It requires authentication.
    """

    def setUp(self):
        """
        Create User and force its authentication
        """
        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')
        self.client = APIClient()
        # Any requests that we will use for this client will be
        # made using this user
        self.client.force_authenticate(user=self.user)

        # Create sample Stock objects for testing
        Stock.objects.create(stock_code='ABC', sector='Technology', industry='Software',
                             country='USA', exchange_short_name='NASDAQ', company_name='ABC Inc.',
                             rsi=30, fa_score=31, avg_gain_loss=Decimal('10.5'),
                             five_year_avg_dividend_yield=Decimal('22.3'))
        Stock.objects.create(stock_code='DEF', sector='Finance', industry='Banking',
                             country='UK', exchange_short_name='LSE', company_name='DEF Bank',
                             rsi=20, fa_score=20, avg_gain_loss=Decimal('11.2'),
                             five_year_avg_dividend_yield=Decimal('1.8'))

    def test_dashboard_api_correct_query(self):
        """
        Test APi query that contains all the required indicators:
        fa_score, rsi, avg_gain_loss, five_year_avg_dividend_yield
        """

        response = self.client.get(
            '/dashboard-api/?fa_score=30&rsi=40&avg_gain_loss=10&five_year_avg_dividend_yield=1')

        # Verify that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that only the 'ABC' stock is returned by the filtering requirements
        self.assertEqual(response.data[0]['stock_code'], 'ABC')
        self.assertEqual(response.data[0]['sector'], 'Technology')
        self.assertEqual(response.data[0]['industry'], 'Software')
        self.assertEqual(response.data[0]['country'], 'USA')
        self.assertEqual(response.data[0]['exchange_short_name'], 'NASDAQ')
        self.assertEqual(response.data[0]['company_name'], 'ABC Inc.')
        self.assertEqual(response.data[0]['rsi'], 30)
        self.assertEqual(response.data[0]['fa_score'], 31)
        self.assertEqual(response.data[0]['avg_gain_loss'], '10.50')
        self.assertEqual(response.data[0]['five_year_avg_dividend_yield'], '22.30')

    def test_dashboard_api_incorrect_query(self):
        """
        Test APi query that Does NOT contain all the required indicators:
        fa_score, rsi, avg_gain_loss, five_year_avg_dividend_yield
        """
        response = self.client.get(
            '/dashboard-api/?fa_score=30&rsi=40&avg_gain_loss=10')

        # Verify that the response status code is 400
        self.assertEqual(response.status_code, 400)
        # Confirm that ParseError message is raised
        self.assertEqual(response.data['detail'], "All required indicators (fa_score, rsi, avg_gain_loss, "
                                                  "five_year_avg_dividend_yield) must be provided.")
