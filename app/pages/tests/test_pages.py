from django.urls import reverse
from django.test import SimpleTestCase


class PublicTests(SimpleTestCase):
    """ Test unauthenticated requests """

    def test_home_page_load_correct(self):
        """ Test that home page loads correctly """

        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Optionally, you can also assert the content of the response
        # to check for expected HTML
        self.assertContains(response, 'Welcome to MarketWatchAI!')

    def test_home_page_contains_navbar_footer(self):
        """
        Test that home page contains
        <!-- Navbar Section -->
        <!-- Footer Section -->
        """
        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Optionally, you can also assert the content of the response
        # to check for expected HTML
        self.assertContains(response, '<!-- Hero Section -->')
        self.assertContains(response, '<!-- Footer Section -->')

