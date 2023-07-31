import os.path
from django.urls import reverse
from django.test import SimpleTestCase, TestCase, Client
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from core.models import UserProfile
import datetime


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
        # user_profile.refresh_from_db()

        # Issue a GET request to the generated URL
        response = self.client.get('/')

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Check if response contains image file
        self.assertContains(response, 'uploads/user_images/')

        # Delete image after test
        img_path = user_profile.image.path
        if os.path.exists(img_path):
            os.remove(img_path)


class TestProfile(TestCase):
    """
    Test that page profile displays the correct data
    """

    def setUp(self):
        """
        Create User and force it to log in.
        """
        # Create User
        self.client = Client()
        self.user = User.objects.create_user(username='user_profile@example.com',
                                             password='123456',
                                             email='user_profile@example.com',
                                             first_name='Test First Name',
                                             last_name='Test Last Name')

        self.user_profile = UserProfile.objects.get(pk=self.user.pk)
        self.user_profile.location = 'Test Location'
        self.user_profile.bio = 'Test Bio'

        # Create a 1x1px image file
        image_file = BytesIO()
        image = Image.new('RGBA', size=(1, 1), color=(155, 0, 0))
        image.save(image_file, 'png')
        image_file.name = 'test.png'
        image_file.seek(0)

        # Upload the image to the user profile
        self.user_profile.image.save(image_file.name, ContentFile(image_file.read()), save=True)
        self.user_profile.save()

        # Login registered user
        self.client.login(username='user_profile@example.com', password='123456')

    def tearDown(self):
        """
        Delete uploaded image for the tests
        """
        if os.path.exists(self.user_profile.image.path):
            os.remove(self.user_profile.image.path)

    def test_profile_correct_data(self):
        """
        Test that page profile contains all required fields
        """
        # Issue a GET request to the generated URL
        response = self.client.get(reverse('profile'))

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Check if response contains all required data
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user_profile.location)
        self.assertContains(response, self.user_profile.bio)
        self.assertContains(response, self.user_profile.image.url)
        self.assertContains(response, '/profile-update')

    def test_profile_unauthorized_user(self):
        """
        Confirm that only registered users have access to profile page
        and are redirected to log in
        """
        self.client.logout()

        # Issue a GET request to the generated URL
        response = self.client.get(reverse('profile'))

        # Assert that the response status code is 302
        # redirect to page login
        self.assertEqual(response.status_code, 302)


class TestUpdateProfile(TestCase):
    """
    Test that page update-profile behaves as expected.
    """

    def setUp(self):
        """
        Create User and force it to log in.
        """
        # Create User
        self.client = Client()
        self.user = User.objects.create_user(username='user_profile@example.com',
                                             password='123456',
                                             email='user_profile@example.com',
                                             first_name='Test First Name',
                                             last_name='Test Last Name')

        self.user_profile = UserProfile.objects.get(pk=self.user.pk)
        self.user_profile.location = 'Test Location'
        self.user_profile.bio = 'Test Bio'

        # Create a 1x1px image file
        image_file = BytesIO()
        image = Image.new('RGBA', size=(1, 1), color=(155, 0, 0))
        image.save(image_file, 'png')
        image_file.name = 'test.png'
        image_file.seek(0)

        # Upload the image to the user profile
        self.user_profile.image.save(image_file.name, ContentFile(image_file.read()), save=True)
        self.user_profile.save()

        # Login registered user
        self.client.login(username='user_profile@example.com', password='123456')

    def tearDown(self):
        """
        Delete uploaded image for the tests
        """
        self.user_profile.refresh_from_db()
        if os.path.exists(self.user_profile.image.path):
            os.remove(self.user_profile.image.path)

    def test_profile_update_correct_placeholders(self):
        """
        Test page profile-update contains correct placeholders data
        """
        # Open 'profile-update'
        response = self.client.get(reverse('profile-update'))

        # Assert that the response status code is 200,
        # indicating a successful response
        self.assertEqual(response.status_code, 200)

        # Check if response contains all required data
        self.assertContains(response, 'placeholder="' + self.user.first_name)
        self.assertContains(response, 'placeholder="' + self.user.last_name)
        self.assertContains(response, 'placeholder="' + self.user_profile.bio)
        self.assertContains(response, 'placeholder="' + self.user_profile.location)

    def test_profile_update_submit_correct_data(self):
        """
        Test if a POST request will save the data into models:
        User and UserProfile
        """
        profile_image_before_update = self.user_profile.image.path

        # Create a 250x250px image file
        image_file = BytesIO()
        image = Image.new('RGB', size=(250, 250), color=(155, 0, 0))
        image.save(image_file, 'JPEG')
        image_file.name = 'updated_image.jpg'
        image_file.seek(0)

        # POST request to 'profile-update'
        data = {
            'first_name': 'Updated First Name',
            'last_name': 'Updated Last Name',
            'bio': 'Updated Bio',
            'location': 'Updated Location',
            'birth_date': '2023-07-28',
            'image': image_file
        }

        response = self.client.post(reverse('profile-update'), data)

        # Confirm success
        self.assertEqual(response.status_code, 200)

        # Confirm redirection to page 'profile'
        self.assertContains(response, '| Profile')

        # Confirm that updated data is displayed
        self.assertContains(response, data['first_name'])
        self.assertContains(response, data['last_name'])
        self.assertContains(response, data['bio'])
        self.assertContains(response, data['location'])
        self.assertContains(response, data['birth_date'])

        # Confirm that update image is displayed
        self.assertContains(response, 'updated_image')

        # Confirm that previous image no longer exists
        self.assertFalse(os.path.exists(profile_image_before_update))

    def test_profile_update_smaller_image(self):
        """
        Tests if uploaded image is less than 200x200 px an
        error message should be displayed. No new image should be uploaded.
        """
        profile_image_before_update = self.user_profile.image.path

        # Create a 150x150px image file
        image_file = BytesIO()
        image = Image.new('RGB', size=(150, 150), color=(155, 0, 0))
        image.save(image_file, 'JPEG')
        image_file.name = 'updated_image.jpg'
        image_file.seek(0)

        # POST request to 'profile-update'
        data = {
            'first_name': 'Updated First Name',
            'last_name': 'Updated Last Name',
            'bio': 'Updated Bio',
            'location': 'Updated Location',
            'birth_date': '2023-07-28',
            'image': image_file
        }

        response = self.client.post(reverse('profile-update'), data, follow=True)

        # After follow=True status code is 200
        self.assertEqual(response.status_code, 200)

        # Confirm we are still on page 'profile-update'
        self.assertContains(response, '| Profile Update')

        # Confirm that image is not updated
        self.assertNotContains(response, 'updated_image')

        # Confirm that previous image still exists
        self.assertTrue(os.path.exists(profile_image_before_update))
