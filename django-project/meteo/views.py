#критерий3 1
from django.shortcuts import render
from rest_framework import viewsets
from .models import City, WeatherIcon
from .serializers import CitySerializer, WeatherIconSerializer

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
class WeatherIconViewSet(viewsets.ModelViewSet):
    queryset = WeatherIcon.objects.all()
    serializer_class = WeatherIconSerializer
#критерий3 1