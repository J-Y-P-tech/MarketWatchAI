from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import BaseUserManager


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
