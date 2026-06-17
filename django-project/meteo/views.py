from django.db.models import Q, Count, Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect

from .filters import CityFilter, HistoricalWeatherIconFilter
from .models import City, WeatherIcon, HourlyForecast, WeatherConfirmation, ViewedCity, SelectedCity
from .serializers import *
from .forms import CityForm


class CityViewSet(viewsets.ModelViewSet):
    """
    API для работы с городами.
    """

    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_class = CityFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Возвращает отфильтрованный список городов
        с аннотацией количества просмотров.
        """
        return City.objects.annotate(
            views_count=Count('viewedcity')
        )

    @action(methods=["GET"], detail=False)
    def count(self, request) -> Response:
        """
        Возвращает общее количество городов.
        """
        return Response({"count": City.objects.count()})


class WeatherIconViewSet(viewsets.ModelViewSet):
    """
    API для иконок погоды.
    """

    queryset = WeatherIcon.objects.all()
    serializer_class = WeatherIconSerializer
    filterset_class = HistoricalWeatherIconFilter
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Возвращает иконки с изображениями и ключевыми словами.
        """
        return WeatherIcon.objects.filter(
            (Q(name__icontains="sun") | Q(name__icontains="cloud"))
            & ~Q(image__isnull=True)
            & Q(image_url="")
        )

    @action(methods=["GET"], detail=False)
    def with_file(self, request) -> Response:
        """
        Количество иконок с изображениями или URL.
        """
        count = WeatherIcon.objects.filter(
            Q(image__isnull=False) | Q(image_url__isnull=False)
        ).count()
        return Response({"count": count})

    @action(methods=["POST"], detail=True)
    def update_url(self, request, pk=None) -> Response:
        """
        Обновляет URL иконки.
        """
        icon = self.get_object()
        new_url = request.data.get("image_url")

        if not new_url:
            return Response({"error": "image_url не указан"}, status=400)

        icon.image_url = new_url
        icon.save()

        return Response(
            {"status": f"URL для {icon.name} обновлён", "image_url": icon.image_url}
        )


class HourlyForecastViewSet(viewsets.ModelViewSet):
    """
    API почасового прогноза погоды.
    """

    queryset = HourlyForecast.objects.all()
    serializer_class = HourlyForecastSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Добавляет поле актуальности прогноза.
        """
        now = timezone.now()

        return HourlyForecast.objects.select_related('city', 'icon').annotate(
            is_actual=Case(
                When(datetime__gte=now, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )


class WeatherConfirmationViewSet(viewsets.ModelViewSet):
    """
    API подтверждений погоды пользователями.
    """

    queryset = WeatherConfirmation.objects.all()
    serializer_class = WeatherConfirmationSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Добавляет количество подтверждений пользователя.
        """
        return WeatherConfirmation.objects.select_related('user', 'city').annotate(
            total_user_confirmations=Count('user')
        )

    def get_serializer_context(self):
        """
        Передаёт текущего пользователя в сериализатор.
        """
        context = super().get_serializer_context()
        context['request_user'] = self.request.user
        return context


class ViewedCityViewSet(viewsets.ModelViewSet):
    """
    API просмотренных городов.
    """

    queryset = ViewedCity.objects.all()
    serializer_class = ViewedCitySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Оптимизированный запрос с select_related.
        """
        return ViewedCity.objects.select_related('user', 'city').all()


class SelectedCityViewSet(viewsets.ModelViewSet):
    """
    API выбранного города пользователя.
    """

    queryset = SelectedCity.objects.all()
    serializer_class = SelectedCitySerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        """
        Оптимизированный запрос с select_related.
        """
        return SelectedCity.objects.select_related('user', 'city').all()