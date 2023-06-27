from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestAccountPages(TestCase):
    """
    Test that pages open with code 200
    """

    def test_login_page(self):
        """ Test that login page loads correctly """

        url = reverse('login')

        # Issue a GET request to the generated URL
        response = self.client.get(url)

        # Assert that the response status code is 200 indicating a successful response
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        """ Test that register page loads correctly """

        url = reverse('register')

        # Issue a GET request to the generated URL
        response = self.client.get(url)

        # Assert that the response status code is 200 indicating a successful response
        self.assertEqual(response.status_code, 200)

    def test_logout_page(self):
        """ Test that login page loads correctly """

        url = reverse('logout')

        # Issue a GET request to the generated URL
        response = self.client.get(url)

        # Assert that the response status code is
        # 302 indicating a successful redirect
        self.assertEqual(response.status_code, 302)


class TestLogin(TestCase):
    """
    Test that login page works as expected
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser@example.com',
                                             password='testpassword')

    def test_login_page(self):
        """ Test that login page loads correctly """

        url = reverse('login')

        # Issue a GET request to the generated URL
        response = self.client.get(url)

        # Assert that the response status code is 200 indicating a successful response
        self.assertEqual(response.status_code, 200)

    def test_login_successful(self):
        """ Test that user logged in successfully and
        is redirected to home page """

        response = self.client.post(reverse('login'),
                                    {'email': self.user.username,
                                     'password': 'testpassword'})

        # 302 is the status code for redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_unsuccessful(self):
        """ Test user with wrong credentials to be redirected to login page
        """
        response = self.client.post(reverse('login'),
                                    {'email': self.user.username,
                                     'password': 'wrongpassword'})

        # 302 is the status code for redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_email_normalized(self):
        """ Test that email has been normalized upon login """

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            # Create email with normalized email
            self.user = User.objects.create_user(username=expected,
                                                 password='testpassword')

            # Try login with email that has not been normalized
            response = self.client.post(reverse('login'),
                                        {'email': email,
                                         'password': 'testpassword'})

            # 302 is the status code for redirect
            self.assertEqual(response.status_code, 302)
            # Confirm that user has been redirected to home which means
            # a successful login
            self.assertRedirects(response, reverse('home'))


class TestRegister(TestCase):
    """
    Test that page register works as expected
    """

    def test_register_page_load(self):
        """
        Test that page register loads correctly
        """

        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_successful_registration(self):
        """
        Test that user is registered successful and redirected to home page
        """

        # Make post request for user registration
        response = self.client.post(reverse('register'),
                                    {
                                        'first_name': 'Test first name',
                                        'last_name': 'Test last name',
                                        'email': 'test_register@example.com',
                                        'password': 'register_password',
                                        'confirm_password': 'register_password'
                                    })

        # Confirm status code for redirection
        self.assertEqual(response.status_code, 302)

        # Confirm redirection to page home
        self.assertRedirects(response, reverse('home'))

        # Confirm that no new user with the same email has been created
        number_users = User.objects.filter(username='test_register@example.com').count()
        self.assertEqual(number_users, 1)

    def test_existing_email(self):
        """
        Test when trying to register with existing email
        User should be redirected to register page
        Confirm that only 1 user exists with given email
        """
        self.client = Client()
        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')

        # Make post request for user registration
        response = self.client.post(reverse('register'),
                                    {
                                        'first_name': 'Test first name',
                                        'last_name': 'Test last name',
                                        'email': 'test_existing@example.com',
                                        'password': 'register_password',
                                        'confirm_password': 'register_password'
                                    })

        # Confirm status code for redirection
        self.assertEqual(response.status_code, 302)

        # Confirm redirection to page home
        self.assertRedirects(response, reverse('register'))

        # Confirm that no new user with the same email has been created
        number_users = User.objects.filter(username='test_existing@example.com').count()
        self.assertEqual(number_users, 1)

    def test_password_missmatch(self):
        """
        Test registration with password missmatch
        User should be redirected to registration page
        """
        # Make post request for user registration
        response = self.client.post(reverse('register'),
                                    {
                                        'first_name': 'Test first name',
                                        'last_name': 'Test last name',
                                        'email': 'testuser@example.com',
                                        'password': 'register_password',
                                        'confirm_password': 'wrong_password'
                                    })

        # Confirm status code for redirection
        self.assertEqual(response.status_code, 302)

        # Confirm redirection to page home
        self.assertRedirects(response, reverse('register'))

        # Confirm that no new user has been created
        user_exists = User.objects.filter(username='testuser@example.com').exists()
        self.assertFalse(user_exists)


class TestLogout(TestCase):
    """
    Test logout functionality
    """

    def setUp(self):
        """
        SetUp method will create user and log in with its credentials
        """
        self.client = Client()
        self.user = User.objects.create_user(username='testuser@example.com',
                                             password='testpassword')
        self.client.post(reverse('login'),
                         {'email': self.user.username,
                          'password': 'testpassword'})

    def test_logout(self):
        """
        Test that user is logged out after calling logout function
        """

        # POST logout
        response = self.client.post(reverse('logout'), follow=True)

        # Assert that no user is authenticated
        self.assertFalse(response.context['user'].is_authenticated)
