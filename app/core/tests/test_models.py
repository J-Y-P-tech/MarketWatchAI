from django.test import TestCase, Client
from core.models import Stock, UserProfile, File
from django.utils import timezone
from django.contrib.auth.models import User
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import os


class StockModelTest(TestCase):

    def setUp(self):
        # Create a sample stock object
        Stock.objects.create(
            stock_code="AAPL",
            sector="Technology",
            industry="Consumer Electronics",
            country="USA",
            description="Apple Inc. designs, manufactures, and markets smartphones, personal computers, "
                        "tablets, wearables, and accessories worldwide.",
            exchange_short_name="NASDAQ",
            company_name="Apple Inc.",
            ipo_years=1980,
            rsi=65,
            rsi_date=timezone.make_aware(timezone.datetime(2021, 12, 15)),
            fa_score=8,
            fa_score_date=timezone.make_aware(timezone.datetime(2021, 12, 15)),
            avg_gain_loss=0.25,
            five_year_avg_dividend_yield=0.25
        )

    def test_stock_str(self):
        # Test the __str__ method of the stock model
        stock = Stock.objects.get(stock_code="AAPL")
        self.assertEqual(str(stock), "AAPL")

    def test_stock_fields(self):
        # Test the fields of the stock model
        stock = Stock.objects.get(stock_code="AAPL")
        self.assertEqual(stock.sector, "Technology")
        self.assertEqual(stock.industry, "Consumer Electronics")
        self.assertEqual(stock.country, "USA")
        self.assertEqual(stock.description,
                         "Apple Inc. designs, manufactures, and markets smartphones, personal computers, "
                         "tablets, wearables, and accessories worldwide.")
        self.assertEqual(stock.exchange_short_name, "NASDAQ")
        self.assertEqual(stock.company_name, "Apple Inc.")
        self.assertEqual(stock.ipo_years, 1980)
        self.assertEqual(stock.rsi, 65)
        self.assertEqual(stock.rsi_date.strftime("%Y-%m-%d"), "2021-12-15")
        self.assertEqual(stock.fa_score, 8)
        self.assertEqual(stock.fa_score_date.strftime("%Y-%m-%d"), "2021-12-15")
        self.assertEqual(stock.avg_gain_loss, 0.25)
        self.assertEqual(stock.five_year_avg_dividend_yield, 0.25)


class UserProfileModelTest(TestCase):
    """
    Test that UserProfile model behaves as expected.
    When a user is created a new record in UserProfile should be created that
    contains reference to user data
    """

    def setUp(self):
        """
        SetUp method creates instance of Client()
        Creates user in User Model
        """
        self.client = Client()
        self.user = User.objects.create_user(username='user_profile@example.com',
                                             password='123456')

    def test_user_profile_exists(self):
        """
        Confirm that a record in UserProfile exists and is a reference
        to user.
        """
        user_profile = UserProfile.objects.get(pk=self.user.pk)
        self.assertEqual(user_profile.user, self.user)

    def test_user_profile_image(self):
        """
        Confirm that a user can upload an image to their profile and
        that the image is deleted on teardown.
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

        # Test that the image exists
        self.assertTrue(user_profile.image)

        # Delete the image file on teardown
        user_profile.image.delete(save=True)


class FileModelTests(TestCase):
    """
    Tests for FileModel
    """

    def setUp(self):
        """
        SetUp method creates instance of Client()
        Creates superuser in User Model and force to log in
        """
        self.client = Client()
        self.admin_username = 'super_user_profile@example.com'
        self.admin_password = 'adminpassword'

        self.user = User.objects.create_superuser(username=self.admin_username,
                                                  password=self.admin_password,
                                                  email=self.admin_username)
        self.client.login(username=self.admin_username, password=self.admin_password)


class FileAdminTestCase(TestCase):
    """
    Test class for model File
    """

    def setUp(self):
        """
        Create admin and regular user for tests and login as admin.
        """
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpassword',
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username='regular_user',
            password='regularpassword',
            is_staff=False,
        )
        self.client.login(username='admin', password='adminpassword')
        self.upload_url = reverse('admin:core_file_add')
        file_data = b"AAPL\nMSFT\nADBE"
        self.file_to_upload = SimpleUploadedFile("test_file.txt", file_data)

    def tearDown(self):
        """
        Clean up uploaded files and Stock objects.
        """
        for file_obj in File.objects.all():
            # Delete the associated file from the Docker volume
            file_path = file_obj.file.path
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete the model record
            file_obj.delete()

        Stock.objects.all().delete()

    def test_admin_can_upload_file(self):
        """
        Test that admin can upload txt file successfully.
        Confirm that record in model File is created.
        Confirm that stock codes from file are added to model Stock.
        """

        # Confirm that admin has access to: admin/core/file/add/
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)

        # Upload generated txt file
        response = self.client.post(self.upload_url, {'file': self.file_to_upload})

        # Redirect after successful upload
        self.assertEqual(response.status_code, 302)

        # Confirm that file is added to model File
        self.assertEqual(File.objects.count(), 1)

        # Confirm that file exists on its location
        file_obj = File.objects.first()
        self.assertTrue(os.path.exists(file_obj.file.path))

        # Confirm that model Stock contains: AAPL, MSFT, ADBE
        stock_codes = ['AAPL', 'MSFT', 'ADBE']
        for stock_code in stock_codes:
            self.assertTrue(Stock.objects.filter(stock_code=stock_code).exists())

    def test_existing_stocks_not_added_from_file(self):
        """
        Confirm that stock that already exist in file are not been added twice
        """

        # Upload generated txt file from setUp
        self.client.post(self.upload_url, {'file': self.file_to_upload})

        # generate new file with 1 new stock
        file_data = b"AAPL\nMSFT\nADBE\nERIC"
        file_to_upload = SimpleUploadedFile("test_file.txt", file_data)
        self.client.post(self.upload_url, {'file': file_to_upload})

        # Confirm that number of stocks is = 4
        # Only 1 new stock is added to existing 3
        count_stocks = Stock.objects.all().count()
        self.assertEqual(count_stocks, 4)

    def test_admin_can_delete_file(self):
        """
        Confirm that admin can upload and delete file
        """
        # Upload generated txt file
        self.client.post(self.upload_url, {'file': self.file_to_upload})

        # Delete uploaded file using: admin/core/file/delete/
        file_obj = File.objects.first()
        delete_url = reverse('admin:core_file_delete', args=[file_obj.pk])

        # Confirm deletion
        response = self.client.post(delete_url, {'post': 'yes'})

        # Redirect after successful delete
        self.assertEqual(response.status_code, 302)

        # Confirm that no records exist in model File
        self.assertEqual(File.objects.count(), 0)

    def test_regular_user_cannot_upload_file(self):
        """
        Confirm that regular user can not upload in model File
        due to restrictions.
        """
        # Log in as regular user
        self.client.logout()
        self.client.login(username='regular_user', password='regularpassword')

        response = self.client.get(self.upload_url)

        # 302 - Redirect
        # User is redirected to login page
        self.assertEqual(response.status_code, 302)
