"""
Tests for the user API.
"""
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from core.models import UserProfile
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class PublicUserApiTests(APITestCase):
    """
    Test the public features of the user API.
    Public tests do not require authentication
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'username': 'testuser@example.com',
            'email': 'testuser@example.com',
            'password': 'register_password',
        }
        # Post data to API
        res = self.client.post(reverse('api-register'), payload)

        # Confirm status code 201 = Created
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Confirm user exists in model User
        user_exists = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)

        # Assures that the password is not part of the data response
        # so that we do not transfer sensitive information
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')
        user_exists = User.objects.filter(
            email='test_existing@example.com'
        ).exists()
        self.assertTrue(user_exists)

        payload = {
            'username': 'test_existing@example.com',
            'email': 'test_existing@example.com',
            'password': 'test_password',
        }
        res = self.client.post(reverse('api-register'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 6 chars."""
        payload = {
            'username': 'testuser@example.com',
            'email': 'testuser@example.com',
            'password': 'short',
        }
        res = self.client.post(reverse('api-register'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""

        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')

        payload = {
            'email': 'test_existing@example.com',
            'password': 'test_password',
        }
        res = self.client.post(reverse('api-token'), payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""

        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test@example.com',
                                             username='test@example.com',
                                             password='good_password')

        payload = {
            'email': 'test@example.com',
            'password': 'bad_password'
        }
        res = self.client.post(reverse('api-token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """
        Try to create token for user that do not exist
        """
        # We don’t have user created, so when trying to create token
        # it fails
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(reverse('api-token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(reverse('api-token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(reverse('me'))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(APITestCase):
    """
    Test API requests that require authentication.
    We create this separate class because it uses separate setUp method
    """

    def setUp(self):
        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')
        self.client = APIClient()
        # Any requests that we will use for this client will be
        # made using this user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(reverse('me'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['first_name'], self.user.first_name)
        self.assertEqual(res.data['email'], self.user.email)

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint.
        http:.../accounts/me/ should not be able to post
        {} is an empty dictionary
        """
        res = self.client.post(reverse('me'), {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'first_name': 'Updated first name', 'password': 'newpassword123'}

        res = self.client.patch(reverse('me'), payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class PrivateUserProfileApiTests(APITestCase):
    """
    Test User Profile API. Confirm that only authenticated user's data is returned
    and in case of unauthorized user and exception is thrown.
    """

    def setUp(self):
        """
        SetUp method will create User and force API client to log in.
        Tests will be performed with authenticated user.
        """
        # Create user in User model
        self.user = User.objects.create_user(first_name="Test First Name",
                                             last_name="Test Last Name",
                                             email='test_existing@example.com',
                                             username='test_existing@example.com',
                                             password='test_password')
        # Get created UserProfile
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.bio = 'Test Bio'
        self.user_profile.birth_date = '1980-03-14'
        self.user_profile.location = 'Sofia'
        # Save the changes to the database
        self.user_profile.save()

        self.client = APIClient()
        # Any requests that we will use for this client will be
        # made using this user
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        """
        Test that API can retrieve data for currently logged user.
        """
        response = self.client.get(reverse('api-user-profile'))

        # Confirm that response is 200 = success
        self.assertEqual(response.status_code, 200)

        # Assert UserProfile data
        self.assertEqual(response.data['bio'], 'Test Bio')
        self.assertEqual(response.data['birth_date'], '1980-03-14')
        self.assertEqual(response.data['location'], 'Sofia')

        # Assert User data
        self.assertEqual(response.data['first_name'], 'Test First Name')
        self.assertEqual(response.data['last_name'], 'Test Last Name')
        self.assertEqual(response.data['email'], 'test_existing@example.com')
        self.assertEqual(response.data['username'], 'test_existing@example.com')

    def test_update_user_profile_successfully(self):
        """
        Test that API updated user data successfully.
        """
        updated_data = {
            'bio': 'Updated Bio',
            'birth_date': '1990-05-25',
            'location': 'New York',
        }
        response = self.client.patch(reverse('api-user-profile'), data=updated_data)

        # Confirm that response is 200 = success
        self.assertEqual(response.status_code, 200)

        # Refresh the user profile from the database
        self.user_profile.refresh_from_db()

        # Assert updated UserProfile data
        self.assertEqual(self.user_profile.bio, 'Updated Bio')
        self.assertEqual(str(self.user_profile.birth_date), '1990-05-25')
        self.assertEqual(self.user_profile.location, 'New York')

    def test_upload_image_user_profile_successfully(self):
        """
        Generate image 200x200 px that use API to upload it.
        """

        # Create a 200x200px image file
        image_file = BytesIO()
        image = Image.new('RGB', size=(200, 200), color=(155, 0, 0))
        image.save(image_file, 'JPEG')
        image_file.name = 'upload_image.jpg'
        image_file.seek(0)

        # Upload the image via the API
        image_data = {
            'image': SimpleUploadedFile(image_file.name, image_file.read(), content_type='image/jpeg')
        }
        response = self.client.patch(reverse('api-user-profile'), data=image_data, format='multipart')

        # Confirm that response is 200 = success
        self.assertEqual(response.status_code, 200)

        # Refresh the user profile from the database
        self.user_profile.refresh_from_db()

        # Assert that the path to the uploaded image exists in UserProfile
        self.assertIn('upload_image.jpg', str(self.user_profile.image))

        # Delete the uploaded image from the user profile
        self.user_profile.image.delete()

        # Clean up
        image_file.close()

    def test_upload_image_profile_error(self):
        """
        Test unsuccessful image upload. Generate image less than 200px wide and
        confirm that exception is raised: Image should be at least 200x200 px.
        """

        # Create a 1x1px image file
        image_file = BytesIO()
        image = Image.new('RGB', size=(1, 1), color=(155, 0, 0))
        image.save(image_file, 'JPEG')
        image_file.name = 'error_image.jpg'
        image_file.seek(0)

        # Upload the small image via the API and expect a ValidationError
        with self.assertRaises(Exception) as context:
            self.client.patch(reverse('api-user-profile'),
                              {'image': image_file},
                              format='multipart')

        # Confirm that the exception is raised and contains the expected error message
        self.assertEqual(str(context.exception), 'Image should be at least 200x200 px.')

        # Refresh the user profile from the database
        self.user_profile.refresh_from_db()

        # Assert that there is no path to uploaded image in UserProfile
        self.assertNotIn('error_image.jpg', str(self.user_profile.image))

        # Clean up
        image_file.close()
