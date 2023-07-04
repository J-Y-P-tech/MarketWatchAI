from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def home(request):
    return render(request, 'pages/home.html')


@login_required(login_url='/accounts/login')
def dashboard(request):
    return render(request, 'pages/dashboard.html')
