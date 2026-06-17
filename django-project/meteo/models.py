from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from datetime import timedelta
from django.core.exceptions import ValidationError
from .validators import base_str_validator


class User(models.Model):
    """
    Пользователь системы.
    Хранит базовые данные аккаунта.
    """

    username = models.CharField(max_length=30, verbose_name="Имя пользователя")
    email = models.EmailField(max_length=50, verbose_name="Электронная почта")
    password = models.CharField(max_length=128, verbose_name="Пароль (хэш)")
    created_at = models.DateTimeField(verbose_name="Дата регистрации", auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        """Возвращает имя пользователя."""
        return self.username

    def clean(self) -> None:
        """Проверка корректности имени пользователя."""
        base_str_validator(self.username, model=User, field_name="username", instance=self)


class City(models.Model):
    """
    Город с координатами и страной.
    Используется для хранения погодных данных.
    """

    name = models.CharField(max_length=100, verbose_name="Название города")
    country = models.CharField(max_length=100, verbose_name="Страна")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    history = HistoricalRecords()

    def __str__(self) -> str:
        """Человекочитаемое название города."""
        return f"{self.name}, {self.country}"

    def clean(self) -> None:
        """
        Проверка бизнес-правил города:
        - уникальность координат
        - допустимый диапазон широты
        """
        if City.objects.filter(latitude=self.latitude, longitude=self.longitude).exclude(pk=self.pk).exists():
            raise ValidationError("Город с такими координатами уже существует")

        if not (-60 <= self.latitude <= 75):
            raise ValidationError("Город вне зоны поддерживаемого климатического анализа")


class SelectedCity(models.Model):
    """
    Выбранный пользователем город.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self) -> str:
        """Связь пользователь → город."""
        return f"{self.user.username} → {self.city.name}"


class ViewedCity(models.Model):
    """
    Просмотренные города пользователями.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.user.username} — {self.city.name}"


class WeatherIcon(models.Model):
    """
    Иконки погодных условий.
    """

    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to="weather_icons/", null=True, blank=True)
    image_url = models.URLField(blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """
        Проверка корректности названия и URL иконки.
        """
        base_str_validator(self.name, model=WeatherIcon, field_name="name", instance=self)
        if self.image_url:
            base_str_validator(self.image_url, model=WeatherIcon, field_name="image_url", instance=self)


class HourlyForecast(models.Model):
    """
    Почасовой прогноз погоды.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    temperature = models.FloatField()
    feels_like = models.FloatField(null=True, blank=True)
    icon = models.ForeignKey(WeatherIcon, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=100, blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.city.name} — {self.datetime}"

    def clean(self) -> None:
        """
        Валидация прогноза:
        - запрет устаревших данных
        - проверка адекватности температуры
        """
        if self.datetime < timezone.now() - timedelta(days=7):
            raise ValidationError("Прогноз устарел и не может быть сохранён")

        if self.feels_like is not None:
            if abs(self.feels_like - self.temperature) > 20:
                raise ValidationError("Некорректная разница между температурой и ощущаемой температурой")


class AtmosphericData(models.Model):
    """
    Атмосферные показатели города.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    precipitation = models.FloatField(default=0.0)
    wind_gusts = models.FloatField(null=True, blank=True)
    uv_index = models.FloatField(null=True, blank=True)
    humidity = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    dew_point = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ("city", "date")

    def __str__(self) -> str:
        return f"{self.city.name} — {self.date}"

    def clean(self) -> None:
        """
        Проверка физических границ давления.
        """
        if self.pressure is not None and not (800 <= self.pressure <= 1100):
            raise ValidationError("Атмосферное давление вне реалистичного диапазона")


class SunAndVisibility(models.Model):
    """
    Данные о солнце и видимости.
    """

    city = models.OneToOneField(City, on_delete=models.CASCADE)
    sunrise = models.TimeField()
    sunset = models.TimeField()
    road_visibility = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return self.city.name


class MoonAndPhases(models.Model):
    """
    Фазы луны.
    """

    city = models.OneToOneField(City, on_delete=models.CASCADE)
    moon_phase = models.CharField(max_length=50)
    additional_info = models.TextField(blank=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.city.name} — {self.moon_phase}"

    def clean(self) -> None:
        """
        Проверка корректности фазы луны.
        """
        if self.moon_phase:
            base_str_validator(self.moon_phase, model=MoonAndPhases, field_name="moon_phase", instance=self)


class WeatherConfirmation(models.Model):
    """
    Подтверждение погоды пользователем.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    date = models.DateField()
    fact = models.BooleanField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ("user", "city", "date")

    def __str__(self) -> str:
        return f"{self.user.username} → {self.city.name}"

    def clean(self) -> None:
        """
        Запрет повторного подтверждения погоды.
        """
        if WeatherConfirmation.objects.filter(
            user=self.user,
            city=self.city,
            date=self.date
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Вы уже подтвердили погоду для этого города в эту дату")