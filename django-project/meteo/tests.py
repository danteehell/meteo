# Create your tests here.
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import City, HourlyForecast, WeatherConfirmation, AtmosphericData, User, WeatherIcon


class CityTests(TestCase):

    def test_city_valid(self):
        city = City(name="Moscow", country="Russia", latitude=55, longitude=37)
        city.full_clean()
        city.save()
        self.assertEqual(City.objects.count(), 1)

    def test_duplicate_coordinates(self):
        City.objects.create(name="A", country="R", latitude=10, longitude=10)
        city = City(name="B", country="R", latitude=10, longitude=10)
        with self.assertRaises(ValidationError):
            city.full_clean()

    def test_latitude_out_of_range(self):
        city = City(name="Test", country="R", latitude=999, longitude=10)
        with self.assertRaises(ValidationError):
            city.full_clean()


class HourlyForecastTests(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="Paris", country="France", latitude=48, longitude=2)

    def test_old_forecast(self):
        forecast = HourlyForecast(
            city=self.city,
            datetime=timezone.now() - timedelta(days=10),
            temperature=10
        )
        with self.assertRaises(ValidationError):
            forecast.full_clean()

    def test_temperature_difference(self):
        forecast = HourlyForecast(
            city=self.city,
            datetime=timezone.now(),
            temperature=10,
            feels_like=50
        )
        with self.assertRaises(ValidationError):
            forecast.full_clean()


class WeatherConfirmationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="User1", email="u@mail.com", password="123")
        self.city = City.objects.create(name="Rome", country="Italy", latitude=41, longitude=12)

    def test_duplicate_confirmation(self):
        WeatherConfirmation.objects.create(user=self.user, city=self.city, date="2024-01-01", fact=True)

        obj = WeatherConfirmation(user=self.user, city=self.city, date="2024-01-01", fact=False)

        with self.assertRaises(ValidationError):
            obj.full_clean()


class AtmosphericDataTests(TestCase):

    def setUp(self):
        self.city = City.objects.create(name="Berlin", country="Germany", latitude=52, longitude=13)

    def test_pressure_invalid(self):
        data = AtmosphericData(city=self.city, date="2024-01-01", pressure=2000)
        with self.assertRaises(ValidationError):
            data.full_clean()


class WeatherIconTests(TestCase):

    def test_valid_icon(self):
        icon = WeatherIcon(name="Sun", image_url="")
        icon.full_clean()
        icon.save()
        self.assertEqual(WeatherIcon.objects.count(), 1)