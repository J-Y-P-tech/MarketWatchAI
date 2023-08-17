from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dashboard-api', views.StockListAPIView, basename='dashboard-api')
router.register(r'stock', views.StockDetailViewSet, basename='stock')
# router.register(r'profile-api', views.UserProfileViewSet, basename='profile-api')

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('stock/<int:id>', views.detail, name='detail'),
    path('', include(router.urls)),
    path('profile-update', views.profile_update, name='profile-update'),
    path('profile', views.profile, name='profile'),
]
