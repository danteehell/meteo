from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CityViewSet, WeatherIconViewSet
from . import views

router = DefaultRouter()
router.register(r"cities", CityViewSet)
router.register(r"weather-icons", WeatherIconViewSet)


def home(request):
    return HttpResponse(
        "<h1>Meteo API</h1>"
        "<p>Админка: <a href='/admin/'>/admin/</a></p>"
        "<p>API города: <a href='/api/cities/'>/api/cities/</a></p>"
        "<p>API иконки погоды: <a href='/api/weather-icons/'>/api/weather-icons/</a></p>"
        "<h2>Города</h2>"
        "<p>Посмотреть города: <a href='/cities/'>/cities/</a></p>"
        "<p>Добавить город: <a href='/cities/add/'>/cities/add/</a></p>"
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("", home),
    path("cities/", views.city_list, name="city-list"),
    path("cities/<int:pk>/delete/", views.city_delete, name="city-delete"),
    path("cities/<int:pk>/update/", views.city_update, name="city-update"),
    path("cities/add/", views.city_create, name="city-add"),
]
