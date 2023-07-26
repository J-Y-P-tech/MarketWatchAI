from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dashboard-api', views.StockListAPIView, basename='dashboard-api')
router.register(r'stock', views.StockDetailViewSet, basename='stock')

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('<int:id>', views.detail, name='detail'),
    path('', include(router.urls)),
]
