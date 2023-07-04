from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from rest_framework import generics
from .serializers import UserSerializer, AuthTokenSerializer
from rest_framework.response import Response
from rest_framework import status, generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


def login(request):
    """
    Login already registered user
    """

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=BaseUserManager.normalize_email(email),
                                 password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


def register(request):
    """
    Register new user
    """
    if request.method == 'POST':

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                # Email exists
                messages.error(request, 'This email already exists. Try another one.')
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                                email=email, username=BaseUserManager.normalize_email(email),
                                                password=password)
                user.save()
                # Automatically log in registered user
                auth.login(request, user)
                messages.success(request, 'Successful registration.')
                return redirect('home')

        else:
            # Password missmatch
            messages.error(request, 'Password missmatch.')
            return redirect('register')
    else:
        # Method is not POST
        return render(request, 'accounts/register.html')


def logout(request):
    """
    Logout user that has already logged in
    """
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')

    return redirect('home')


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system.
    The CreateAPIView handles an HTTP POST request that's
    designed for creating objects. So it creates objects in the
    database. It handles all of that logic for us.
    """
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # call the original create method
        response = super().create(request, *args, **kwargs)
        # check if the response has a 400 status code
        if response.status_code == 400:
            # return a custom response with the same data and status
            return Response(data=response.data, status=status.HTTP_400_BAD_REQUEST)
        # otherwise, return the response as it is
        return response


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user.
    When a user sends a POST request to the CreateTokenView endpoint with valid credentials,
    the view will authenticate the user and generate a new token.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user
