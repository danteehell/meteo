from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    CityViewSet,
    WeatherIconViewSet,
    HourlyForecastViewSet,
    WeatherConfirmationViewSet,
    ViewedCityViewSet,
    SelectedCityViewSet,
)

router = DefaultRouter()

router.register(r"cities", CityViewSet)
router.register(r"weather-icons", WeatherIconViewSet)
router.register(r"hourly-forecast", HourlyForecastViewSet)
router.register(r"weather-confirmations", WeatherConfirmationViewSet)
router.register(r"viewed-cities", ViewedCityViewSet)
router.register(r"selected-cities", SelectedCityViewSet)


def home(request):
    return HttpResponse(
        "<h1>Meteo API</h1>"
        "<p>Админка: <a href='/admin/'>/admin/</a></p>"
        "<p>API города: <a href='/api/cities/'>/api/cities/</a></p>"
        "<p>API иконки погоды: <a href='/api/weather-icons/'>/api/weather-icons/</a></p>"
        "<p>API прогнозов: <a href='/api/hourly-forecast/'>/api/hourly-forecast/</a></p>"
        "<p>API подтверждений: <a href='/api/weather-confirmations/'>/api/weather-confirmations/</a></p>"
        "<p>API просмотров: <a href='/api/viewed-cities/'>/api/viewed-cities/</a></p>"
        "<p>API выбранных городов: <a href='/api/selected-cities/'>/api/selected-cities/</a></p>"
        "<h2>Города</h2>"
        "<p>Посмотреть города: <a href='/cities/'>/cities/</a></p>"
        "<p>Добавить город: <a href='/cities/add/'>/cities/add/</a></p>"
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),

    path("", home),

    path("cities/", views.city_list, name="city-list"),
    path("cities/add/", views.city_create, name="city-add"),
    path("cities/<int:pk>/update/", views.city_update, name="city-update"),
    path("cities/<int:pk>/delete/", views.city_delete, name="city-delete"),
]