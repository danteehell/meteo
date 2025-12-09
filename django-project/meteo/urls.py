
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, WeatherIconViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'weather-icons', WeatherIconViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),  
    #критерий3 1  
    path('api/', include(router.urls)), 
    #критерий3 1 
]
