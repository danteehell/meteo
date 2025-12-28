# критерий3 1
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CityFilter, HistoricalWeatherIconFilter
from .models import City, WeatherIcon, HourlyForecast, AtmosphericData, SunAndVisibility
from .serializers import CitySerializer, WeatherIconSerializer
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CityForm


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return City.objects.filter(
            (Q(country="Россия") | Q(country="Польша"))
            & Q(latitude__lte=55)
            & Q(latitude__gte=45)
            & ~Q(longitude__lte=10)
            & Q(longitude__lte=40)
        )

    @action(methods=["GET"], detail=False)
    def count(self, request):
        return Response({"count": City.objects.count()})


class WeatherIconViewSet(viewsets.ModelViewSet):
    queryset = WeatherIcon.objects.all()
    serializer_class = WeatherIconSerializer
    filterset_class = HistoricalWeatherIconFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return WeatherIcon.objects.filter(
            (Q(name__icontains="sun") | Q(name__icontains="cloud"))
            & ~Q(image__isnull=True)
            & Q(image_url="")
        )

    @action(methods=["GET"], detail=False)
    def with_file(self, request):
        count = WeatherIcon.objects.filter(
            Q(image__isnull=False) | Q(image_url__isnull=False)
        ).count()
        return Response({"count": count})

    @action(methods=["POST"], detail=True)
    def update_url(self, request, pk=None):
        icon = self.get_object()
        new_url = request.data.get("image_url")
        if not new_url:
            return Response({"error": "image_url не указан"}, status=400)
        icon.image_url = new_url
        icon.save()
        return Response(
            {"status": f"URL для {icon.name} обновлён", "image_url": icon.image_url}
        )

def home(request):
    return render(request, "home.html")

from django.shortcuts import get_object_or_404, render
from .models import City, HourlyForecast, AtmosphericData, SunAndVisibility

def city(request):
    city_name = request.GET.get("city")
    city = get_object_or_404(City, name__iexact=city_name)

    # Последние почасовые прогнозы (например, на 24 часа)
    hourly_qs = list(HourlyForecast.objects.filter(city=city).order_by('datetime')[:24])
    if hourly_qs:
        hourly = [
            {
                "time": h.datetime.strftime("%H:%M"),
                "temp": h.temperature,
                "feels_like": h.feels_like,
                "description": h.condition or "нет данных",
                "icon": h.icon.name if h.icon else "01d",
            }
            for h in hourly_qs
        ]
        current_obj = hourly_qs[-1]
        current = {
            "temp": getattr(current_obj, "temperature", "нет данных"),
            "feels_like": getattr(current_obj, "feels_like", "нет данных"),
            "description": getattr(current_obj, "condition", "нет данных"),
            "icon": getattr(current_obj.icon, "name", "01d") if current_obj and current_obj.icon else "01d",
        }
    else:
        hourly = []
        current = {
            "temp": "нет данных",
            "feels_like": "нет данных",
            "description": "нет данных",
            "icon": "01d",
        }

    # Последние атмосферные показатели
    atmosphere_obj = AtmosphericData.objects.filter(city=city).order_by('-date').first()
    if atmosphere_obj:
        atmosphere = {
            "precipitation": getattr(atmosphere_obj, "precipitation", "нет данных"),
            "humidity": getattr(atmosphere_obj, "humidity", "нет данных"),
            "pressure": getattr(atmosphere_obj, "pressure", "нет данных"),
            "wind": getattr(atmosphere_obj, "wind_gusts", "нет данных"),
            "uv": getattr(atmosphere_obj, "uv_index", "нет данных"),
            "dew_point": getattr(atmosphere_obj, "dew_point", "нет данных"),
        }
    else:
        atmosphere = {
            "precipitation": "нет данных",
            "humidity": "нет данных",
            "pressure": "нет данных",
            "wind": "нет данных",
            "uv": "нет данных",
            "dew_point": "нет данных",
        }

    # Солнце и видимость
    sun_obj = SunAndVisibility.objects.filter(city=city).first()
    if sun_obj:
        sun = {
            "sunrise": getattr(sun_obj, "sunrise", None).strftime("%H:%M") if sun_obj.sunrise else "нет данных",
            "sunset": getattr(sun_obj, "sunset", None).strftime("%H:%M") if sun_obj.sunset else "нет данных",
        }
    else:
        sun = {
            "sunrise": "нет данных",
            "sunset": "нет данных",
        }

    context = {
        "city": city,
        "current": current,
        "hourly": hourly,
        "atmosphere": atmosphere,
        "sun": sun,
    }

    return render(request, "city.html", context)




def city_list(request):
    cities = City.objects.all()
    return render(request, "city_list.html", {"cities": cities})


def city_create(request):
    if request.method == "POST":
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("city-list")
    else:
        form = CityForm()
    return render(request, "city_form.html", {"form": form})


def city_update(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == "POST":
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            return redirect("city-list")
    else:
        form = CityForm(instance=city)
    return render(request, "city_form.html", {"form": form})


def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)
    if request.method == "POST":
        city.delete()
        return redirect("city-list")
    return render(request, "city_delete.html", {"city": city})
