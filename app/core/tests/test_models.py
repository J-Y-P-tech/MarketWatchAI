from django.test import TestCase, Client
from core.models import Stock, UserProfile
from django.utils import timezone
from django.contrib.auth.models import User
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


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
