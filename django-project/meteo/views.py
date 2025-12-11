#критерий3 1
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import City, WeatherIcon
from .serializers import CitySerializer, WeatherIconSerializer
from django.db.models import Q
from .filters import CityFilter

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend]
    #критерий3 2
    def get_queryset(self):
        return City.objects.filter((Q(country='Россия') | Q(country='Польша')) & Q(latitude__lte=50) & ~Q(longitude__lte=30)
        )
        #критерий3 4
class WeatherIconViewSet(viewsets.ModelViewSet):
    queryset = WeatherIcon.objects.all()
    serializer_class = WeatherIconSerializer
    #критерий4 1
    def get_queryset(self):
        return WeatherIcon.objects.filter(
    (Q(name__icontains="sun") | Q(name__icontains="cloud")) & ~Q(image__isnull=True) & Q(image_url="")
    #критерий4 1
)
#критерий3 1