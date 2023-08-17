from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.models import Stock, UserProfile
from django.contrib.auth.models import User
import decimal
from rest_framework import viewsets, response, status, generics
from .serializers import StockSerializer
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
import PIL.Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from django.contrib import messages
import os.path


def home(request):
    user = request.user
    if user.is_authenticated:
        user_profile = UserProfile.objects.get(user=user.id)
        context = {
            'user': user,
            'user_profile': user_profile
        }
    else:
        context = {

        }
    return render(request, 'pages/home.html', context)


@login_required(login_url='/accounts/login')
def dashboard(request):
    """
    View that handles dashboard page
    """
    if request.method == 'POST':
        fa_score = request.POST.get('fa_score')
        rsi = request.POST.get('rsi')
        avg_gain_loss = request.POST.get('avg_gain_loss')
        five_year_avg_dividend_yield = request.POST.get('five_year_avg_dividend_yield')
        sort_field = request.POST.get('sort')  # Get the sort field from the clicked button

        all_stocks = Stock.objects.all()

        # Filter
        # fa_score greater than
        if fa_score:
            all_stocks = all_stocks.filter(fa_score__gt=int(fa_score))
        # rsi less than
        if rsi:
            all_stocks = all_stocks.filter(rsi__lte=int(rsi))
        # avg_gain_loss greater than
        if avg_gain_loss:
            all_stocks = all_stocks.filter(avg_gain_loss__gt=decimal.Decimal(avg_gain_loss))
        # five_year_dividend_yield greater than
        if five_year_avg_dividend_yield:
            all_stocks = all_stocks.filter(
                five_year_avg_dividend_yield__gt=decimal.Decimal(five_year_avg_dividend_yield))

        # Retrieve the current sort direction from session or set it to ascending by default
        sort_direction = request.session.get('sort_direction', 'ascending')

        # Sort
        if sort_field:
            if sort_field == request.session.get('sort_field'):
                # If the same field is clicked again, reverse the sort direction
                sort_direction = 'ascending' if sort_direction == 'descending' else 'descending'
            else:
                # If a different field is clicked, set the sort direction to ascending
                sort_direction = 'ascending'

            request.session['sort_direction'] = sort_direction
            request.session['sort_field'] = sort_field

            # Determine the prefix '-' for descending order
            sort_prefix = '-' if sort_direction == 'descending' else ''

            # Sort the queryset based on the selected field and direction
            sort_field_with_prefix = f'{sort_prefix}{sort_field}'
            all_stocks = all_stocks.order_by(sort_field_with_prefix)

        # Set default values if none are provided
        data = {
            'fa_score': fa_score,
            'rsi': rsi,
            'avg_gain_loss': avg_gain_loss,
            'five_year_avg_dividend_yield': five_year_avg_dividend_yield,
            'all_stocks': all_stocks,
        }

        return render(request, 'pages/dashboard.html', data)

    if request.method == 'GET':
        fa_score = request.GET.get('fa_score')
        rsi = request.GET.get('rsi')
        avg_gain_loss = request.GET.get('avg_gain_loss')
        five_year_avg_dividend_yield = request.GET.get('five_year_avg_dividend_yield')

        if not fa_score:
            fa_score = 30
        if not rsi:
            rsi = 40
        if not avg_gain_loss:
            avg_gain_loss = 10
        if not five_year_avg_dividend_yield:
            five_year_avg_dividend_yield = 1

        all_stocks = Stock.objects.all()

        # Filter
        # fa_score greater than
        if fa_score:
            all_stocks = all_stocks.filter(fa_score__gt=int(fa_score))
        # rsi less than
        if rsi:
            all_stocks = all_stocks.filter(rsi__lte=int(rsi))
        # avg_gain_loss greater than
        if avg_gain_loss:
            all_stocks = all_stocks.filter(avg_gain_loss__gt=decimal.Decimal(avg_gain_loss))
        # five_year_dividend_yield greater than
        if five_year_avg_dividend_yield:
            all_stocks = all_stocks.filter(
                five_year_avg_dividend_yield__gt=decimal.Decimal(five_year_avg_dividend_yield))

            # Set default values if none are provided
        data = {
            'fa_score': fa_score,
            'rsi': rsi,
            'avg_gain_loss': avg_gain_loss,
            'five_year_avg_dividend_yield': five_year_avg_dividend_yield,
            'all_stocks': all_stocks,
        }

        return render(request, 'pages/dashboard.html', data)


@login_required(login_url='/accounts/login')
def profile(request):
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            user_profile = UserProfile.objects.get(user=user.id)
            context = {
                'user': user,
                'user_profile': user_profile
            }
        else:
            context = {

            }
        return render(request, 'pages/profile.html', context)


@login_required(login_url='/accounts/login')
def profile_update(request):
    """
    View that will manage profile page.
    """
    if request.method == 'GET':
        user = request.user
        if user.is_authenticated:
            user_profile = UserProfile.objects.get(user=user.id)
            context = {
                'user': user,
                'user_profile': user_profile
            }
        else:
            context = {

            }
        return render(request, 'pages/profile_update.html', context)

    if request.method == 'POST':

        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user.id)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')

        if bio:
            user_profile.bio = bio
        birth_date = request.POST.get('birth_date')
        if birth_date:
            user_profile.birth_date = birth_date
        location = request.POST.get('location')
        if location:
            user_profile.location = location

        request_image = request.FILES.get('image')
        if request_image:

            image = PIL.Image.open(request_image)
            if image.width < 200:
                messages.error(request, 'Image should be at least 200x200 px.')
                return redirect('profile-update')
            else:
                if image.height > image.width:
                    """
                    Image is portrait
                    """
                    updated_width = 200
                    updated_height = int((200 * image.height) / image.width)
                    image = image.resize((updated_width, updated_height), PIL.Image.ANTIALIAS)

                    crop_left = 0
                    crop_top = int((updated_height - updated_width) / 2)
                    crop_right = updated_width
                    crop_bottom = updated_width + crop_top

                    # left, top, right, bottom
                    resized_image = image.crop((crop_left, crop_top, crop_right, crop_bottom))
                else:
                    """
                    Image is landscape
                    """
                    updated_height = 200
                    updated_width = int((updated_height * image.width) / image.height)
                    image = image.resize((updated_width, updated_height), PIL.Image.ANTIALIAS)

                    crop_left = int((updated_width - updated_height) / 2)
                    crop_top = 0
                    crop_right = crop_left + updated_height
                    crop_bottom = updated_height
                    # left, top, right, bottom
                    resized_image = image.crop((crop_left, crop_top, crop_right, crop_bottom))

                # image.save(f'{settings.MEDIA_ROOT}/profile_images/{image.name}')
                # Create a BytesIO buffer to temporarily hold the resized image data
                buffer = BytesIO()

                # Save the resized image to the buffer in the same format as the uploaded image
                resized_image.save(buffer, format='JPEG')

                # Create an InMemoryUploadedFile from the buffer with the same name as the original
                resized_image_file = InMemoryUploadedFile(
                    buffer,
                    None,  # field_name, not needed in this case
                    request_image.name,  # the original image filename
                    request_image.content_type,  # content type of the original image
                    resized_image.tell(),  # size of the resized image in bytes
                    None,  # charset, not needed in this case
                )

                # Remove previous image
                img_path = user_profile.image.path
                if os.path.exists(img_path):
                    os.remove(img_path)

                user_profile.image = resized_image_file
                # Save resized image
                user_profile.save()
                # Close Buffer
                buffer.close()

        user.save()
        user_profile.save()

        context = {
            'user': user,
            'user_profile': user_profile
        }

        return render(request, 'pages/profile.html', context)


@login_required(login_url='/accounts/login')
def detail(request, id):
    """
    View for stock detail. By given stock id, checks if
    it is present in model Stock and returns its data to the
    template.
    """
    stock = get_object_or_404(Stock, pk=id)
    data = {
        'stock': stock,
    }

    return render(request, 'pages/detail.html', data)


class StockListAPIView(viewsets.ReadOnlyModelViewSet):
    """
    API list View that will get:
    fa_score, rsi, avg_gain_loss, five_year_avg_dividend_yield
    from request. All indicators should be present.
    If they are not present an Exception will be raised.
    To test this API open
    http://localhost:8000/dashboard-api/?fa_score=30&rsi=40&avg_gain_loss=10&five_year_avg_dividend_yield=1
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        fa_score = self.request.query_params.get('fa_score')
        rsi = self.request.query_params.get('rsi')
        avg_gain_loss = self.request.query_params.get('avg_gain_loss')
        five_year_avg_dividend_yield = self.request.query_params.get('five_year_avg_dividend_yield')

        # If any of the parameters are missing, return an empty queryset
        if not (fa_score and rsi and avg_gain_loss and five_year_avg_dividend_yield):
            raise ParseError("All required indicators (fa_score, rsi, avg_gain_loss, "
                             "five_year_avg_dividend_yield) must be provided.")

        # Apply filters
        if fa_score:
            queryset = queryset.filter(fa_score__gt=int(fa_score))
        if rsi:
            queryset = queryset.filter(rsi__lte=int(rsi))
        if avg_gain_loss:
            queryset = queryset.filter(avg_gain_loss__gt=float(avg_gain_loss))
        if five_year_avg_dividend_yield:
            queryset = queryset.filter(five_year_avg_dividend_yield__gt=float(five_year_avg_dividend_yield))

        return queryset


class StockDetailViewSet(viewsets.ViewSet):
    """
    ViewSet for stocks. Retrieves data for given stock by its ID.
    If stock is not found ParseError is raised
    """
    queryset = Stock.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """
        Override the retrieve method.
        request is argument might see that is not used but without it
        the API returns html, not JSON.
        """
        try:
            stock = self.queryset.get(pk=pk)
        except Stock.DoesNotExist:
            return response.Response({"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StockSerializer(stock)
        return response.Response(serializer.data)


# class UserProfileViewSet(viewsets.ViewSet):
#     """
#     ViewSet for UserProfiles. Gets data for given user.
#     If user is not found Parse error is raised.
#     """
#     queryset = UserProfile.objects.all()
#     permission_classes = [IsAuthenticated]
#
#     def retrieve(self, request, pk=None):
#         """
#         Override the retrieve method.
#         """
#         try:
#             user = request.user
#             user_profile = self.queryset.get(pk=user.pk)
#         except UserProfile.DoesNotExist:
#             return response.Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = UserProfileSerializer(user_profile)
#         return response.Response(serializer.data)
