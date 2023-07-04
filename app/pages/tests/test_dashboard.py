from django.urls import reverse
from django.test import SimpleTestCase, TestCase, Client
from django.contrib.auth.models import User


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
