from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, date

from .models import (
    City,
    HourlyForecast,
    WeatherConfirmation,
    AtmosphericData,
    User,
    WeatherIcon
)


class CityTests(TestCase):
    """
    Тесты модели City.
    """

    def test_city_valid(self) -> None:
        """
        Проверка корректного создания города.
        """
        city = City(name="Moscow", country="Russia", latitude=55, longitude=37)
        city.full_clean()
        city.save()
        self.assertEqual(City.objects.count(), 1)

    def test_duplicate_coordinates(self) -> None:
        """
        Проверка уникальности координат города.
        """
        City.objects.create(name="A", country="R", latitude=10, longitude=10)
        city = City(name="B", country="R", latitude=10, longitude=10)
        with self.assertRaises(ValidationError):
            city.full_clean()

    def test_latitude_out_of_range(self) -> None:
        """
        Проверка диапазона широты.
        """
        city = City(name="Test", country="R", latitude=999, longitude=10)
        with self.assertRaises(ValidationError):
            city.full_clean()


class HourlyForecastTests(TestCase):
    """
    Тесты модели HourlyForecast.
    """

    def setUp(self) -> None:
        self.city = City.objects.create(
            name="Paris", country="France", latitude=48, longitude=2
        )

    def test_old_forecast(self) -> None:
        """
        Прогноз старше допустимого периода должен отклоняться.
        """
        forecast = HourlyForecast(
            city=self.city,
            datetime=timezone.now() - timedelta(days=10),
            temperature=10
        )
        with self.assertRaises(ValidationError):
            forecast.full_clean()

    def test_temperature_difference(self) -> None:
        """
        Проверка разницы температуры и ощущения.
        """
        forecast = HourlyForecast(
            city=self.city,
            datetime=timezone.now(),
            temperature=10,
            feels_like=50
        )
        with self.assertRaises(ValidationError):
            forecast.full_clean()

    def test_valid_forecast(self) -> None:
        """
        Корректное создание прогноза.
        """
        forecast = HourlyForecast(
            city=self.city,
            datetime=timezone.now(),
            temperature=10,
            feels_like=12
        )
        forecast.full_clean()
        forecast.save()
        self.assertEqual(HourlyForecast.objects.count(), 1)


class WeatherConfirmationTests(TestCase):
    """
    Тесты подтверждения погоды.
    """

    def setUp(self) -> None:
        self.user = User.objects.create(
            username="User1",
            email="u@mail.com",
            password="123"
        )
        self.city = City.objects.create(
            name="Rome",
            country="Italy",
            latitude=41,
            longitude=12
        )

    def test_duplicate_confirmation(self) -> None:
        """
        Проверка уникальности подтверждения погоды.
        """
        WeatherConfirmation.objects.create(
            user=self.user,
            city=self.city,
            date=date(2024, 1, 1),
            fact=True
        )

        obj = WeatherConfirmation(
            user=self.user,
            city=self.city,
            date=date(2024, 1, 1),
            fact=False
        )

        with self.assertRaises(ValidationError):
            obj.full_clean()

    def test_valid_confirmation(self) -> None:
        """
        Корректное подтверждение погоды.
        """
        obj = WeatherConfirmation(
            user=self.user,
            city=self.city,
            date=date(2024, 1, 2),
            fact=True
        )
        obj.full_clean()
        obj.save()
        self.assertEqual(WeatherConfirmation.objects.count(), 1)


class AtmosphericDataTests(TestCase):
    """
    Тесты атмосферных данных.
    """

    def setUp(self) -> None:
        self.city = City.objects.create(
            name="Berlin",
            country="Germany",
            latitude=52,
            longitude=13
        )

    def test_pressure_invalid(self) -> None:
        """
        Некорректное давление должно вызывать ошибку.
        """
        data = AtmosphericData(
            city=self.city,
            date=date(2024, 1, 1),
            pressure=2000
        )
        with self.assertRaises(ValidationError):
            data.full_clean()

    def test_valid_atmospheric_data(self) -> None:
        """
        Корректные атмосферные данные.
        """
        data = AtmosphericData(
            city=self.city,
            date=date(2024, 1, 1),
            pressure=1010,
            humidity=50
        )
        data.full_clean()
        data.save()
        self.assertEqual(AtmosphericData.objects.count(), 1)


class WeatherIconTests(TestCase):
    """
    Тесты иконок погоды.
    """

    def test_valid_icon(self) -> None:
        """
        Проверка корректного создания иконки.
        """
        icon = WeatherIcon(name="Sun", image_url="")
        icon.full_clean()
        icon.save()
        self.assertEqual(WeatherIcon.objects.count(), 1)

    def test_duplicate_icon_name(self) -> None:
        """
        Проверка уникальности названия иконки.
        """
        WeatherIcon.objects.create(name="Cloud", image_url="")
        icon = WeatherIcon(name="Cloud", image_url="")
        with self.assertRaises(ValidationError):
            icon.full_clean()