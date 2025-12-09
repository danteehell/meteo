from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, WeatherIconViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'weather-icons', WeatherIconViewSet)

def home(request):
    return HttpResponse(
        "<h1>Meteo API</h1>"
        "<p>Админка: <a href='/admin/'>/admin/</a></p>"
        "<p>API города: <a href='/api/cities/'>/api/cities/</a></p>"
        "<p>API иконки погоды: <a href='/api/weather-icons/'>/api/weather-icons/</a></p>"
    )

urlpatterns = [
    path('admin/', admin.site.urls),  
    #критерий3 1  
    path('api/', include(router.urls)), 
    #критерий3 1 
    path('', home),
]