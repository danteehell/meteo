from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CityViewSet, WeatherIconViewSet, home, city
from . import views

router = DefaultRouter()
router.register(r"cities", CityViewSet)
router.register(r"weather-icons", WeatherIconViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("city/", city, name="city"),
    path("api/", include(router.urls)), 
    path("cities/<int:pk>/delete/", views.city_delete, name="city-delete"),
    path("cities/<int:pk>/update/", views.city_update, name="city-update"),
    path("cities/add/", views.city_create, name="city-add"),
]
