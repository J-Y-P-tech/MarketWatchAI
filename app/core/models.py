from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils import timezone
import os


class Stock(models.Model):
    """
    Model to collect data about given entity(stock)
    """
    stock_code = models.CharField(max_length=8, default='')
    sector = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    exchange_short_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    ipo_years = models.IntegerField(null=True, blank=True)
    rsi = models.IntegerField(null=True, blank=True)
    rsi_date = models.DateTimeField(null=True, blank=True)
    fa_score = models.IntegerField(null=True, blank=True)
    fa_score_date = models.DateTimeField(null=True, blank=True)
    avg_gain_loss = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    five_year_avg_dividend_yield = models.DecimalField(max_digits=4, decimal_places=2, default=-1)

    def __str__(self):
        return self.stock_code


class UserProfile(models.Model):
    """
    UserProfile is an extension of User model that is connected to User OneByOne
    adds image field.
    """
    # related_name='profile' --> means that UserProfile will be saved
    # on model User at the name of 'profile' and can be found by it
    user = models.OneToOneField(User, primary_key=True, verbose_name='user',
                                related_name='profile', on_delete=models.CASCADE)
    # blank=True --> means that the field is not required
    # null=True --> it is allowed to be empty in the database
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/user_images', blank=True)

    def __str__(self):
        return self.user.username

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """
        Every time user is created a new record will be
        added to UserProfile.
        """
        if created:
            UserProfile.objects.get_or_create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        # sender is the User model
        # instance is the actual User object that was just created
        instance.profile.save()


def is_staff_check(user):
    return user.is_staff


class File(models.Model):
    """
    FileModel contain file data in form of txt.
    This file contains all stock codes used in the project.
    """
    file = models.FileField(upload_to='txt-files/')

    def save(self, *args, **kwargs):
        if self.file.name.endswith('.txt'):
            timestamp = timezone.now().strftime('%Y_%m_%d')
            original_name, extension = os.path.splitext(self.file.name)
            new_filename = f"{original_name}_{timestamp}.txt"
            self.file.name = new_filename
            super().save(*args, **kwargs)

            with self.file.open('r') as f:
                lines = f.readlines()
                for line in lines:
                    stock_code = line.strip()
                    if 2 < len(stock_code) < 5 and not Stock.objects.filter(stock_code=stock_code).exists():
                        Stock.objects.create(stock_code=stock_code)
        else:
            raise ValidationError("Only .txt files are allowed.")

        super().save(*args, **kwargs)

    class Meta:
        permissions = [
            ("view_model_file", "Permission to view data from model File"),
            ("write_model_file", "Permission to write data to model File"),
            ("delete_model_file", "Permission to delete data from model File"),
        ]

    def __str__(self):
        return str(self.file)


# Override the has_perm method of the User model
def user_has_perm(self, perm, obj=None):
    if self.is_staff:
        return True
    return self.has_perm(f"app.{perm}")


User.add_to_class("has_perm", user_has_perm)
