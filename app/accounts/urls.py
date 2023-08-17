from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('api-register', views.CreateUserView.as_view(), name='api-register'),
    path('api-token', views.CreateTokenView.as_view(), name='api-token'),
    path('me', views.ManageUserView.as_view(), name='me'),
    path('api-user-profile', views.UserProfileRetrieveUpdateAPIView.as_view(),
         name='api-user-profile')
]
