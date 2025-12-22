# критерий3 1
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CityFilter, HistoricalWeatherIconFilter
from .models import City, WeatherIcon
from .serializers import CitySerializer, WeatherIconSerializer
from django.shortcuts import render, get_object_or_404, redirect
from .forms import CityForm


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend]

    # критерий3 2
    def get_queryset(self):
        return City.objects.filter(
            (Q(country="Россия") | Q(country="Польша"))
            & Q(latitude__lte=55)
            & Q(latitude__gte=45)
            & ~Q(longitude__lte=10)
            & Q(longitude__lte=40)
        )

    # критерий3 4

    @action(methods=["GET"], detail=False)
    def count(self, request):
        return Response({"count": City.objects.count()})


class WeatherIconViewSet(viewsets.ModelViewSet):
    queryset = WeatherIcon.objects.all()
    serializer_class = WeatherIconSerializer
    filterset_class = HistoricalWeatherIconFilter
    filter_backends = [DjangoFilterBackend]

    # критерий4 1
    def get_queryset(self):
        return WeatherIcon.objects.filter(
            (Q(name__icontains="sun") | Q(name__icontains="cloud"))
            & ~Q(image__isnull=True)
            & Q(image_url="")
            # критерий4 1
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


# критерий3 1


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
