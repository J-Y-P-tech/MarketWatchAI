from django.urls import reverse
from django.test import SimpleTestCase, TestCase, Client
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from core.models import UserProfile


class PublicTestsPages(SimpleTestCase):
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

    def test_base_template_navbar(self):
        """
        Test that Navbar contains LogIn and Register links for
        unauthenticated users.
        """
        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Confirm that response contains urls to login and register
        self.assertContains(response, '/accounts/login')
        self.assertContains(response, '/accounts/register')


class PrivateTestsPages(TestCase):
    """
    This class tests registered and authenticated users.
    """

    def setUp(self):
        """
        Create User and force to log in.
        """
        # Create User
        self.client = Client()
        self.user = User.objects.create_user(username='user_profile@example.com',
                                             password='123456')

        # Login registered user
        self.client.login(username='user_profile@example.com', password='123456')

    def test_registered_user_no_photo(self):
        """
        Test registered user without photo.
        The response should contain default avatar icon
        <i class="bi bi-person-bounding-box fs-2"></i>
        """
        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Check if response contains default icon
        self.assertContains(response, '<i class="bi bi-person-bounding-box fs-2"></i>')

    def test_registered_user_with_photo(self):
        """
        Test registered user with photo.
        Image should be provided in the response.
        """
        # Create a 1x1px image file
        image_file = BytesIO()
        image = Image.new('RGBA', size=(1, 1), color=(155, 0, 0))
        image.save(image_file, 'png')
        image_file.name = 'test.png'
        image_file.seek(0)

        # Upload the image to the user profile
        user_profile = UserProfile.objects.get(pk=self.user.pk)
        user_profile.image.save(image_file.name, ContentFile(image_file.read()), save=True)
        user_profile.save()

        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Check if response contains image file
        self.assertContains(response, '/static/media/user_images/')
