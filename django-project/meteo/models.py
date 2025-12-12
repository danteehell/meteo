from django.db import models
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=30, verbose_name="Имя пользователя")
    email = models.EmailField(max_length=50, verbose_name="Электронная почта")
    password = models.CharField(max_length=128, verbose_name="Пароль (хэш)")
    created_at = models.DateTimeField(verbose_name='Дата регистрации', auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название города")
    country = models.CharField(max_length=100, verbose_name="Страна")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ("country", "name")

    def __str__(self):
        return f"{self.name}, {self.country}"


class SelectedCity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    history = HistoricalRecords()


    class Meta:
        verbose_name = "Выбранный город"
        verbose_name_plural = "Выбранные города"

    def __str__(self):
        return f"{self.user.username} → {self.city.name}"


class ViewedCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    history = HistoricalRecords()


    class Meta:
        verbose_name = "Просмотренный город"
        verbose_name_plural = "Просмотренные города"
        indexes = [
            models.Index(fields=["user", "city"]),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.city.name}"


class WeatherIcon(models.Model):
    name = models.CharField(max_length=50, verbose_name="Код / название иконки")
    image = models.ImageField(upload_to="weather_icons/", null=True, blank=True, verbose_name="Файл иконки")
    image_url = models.URLField(blank=True, verbose_name="URL иконки")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Иконка погоды"
        verbose_name_plural = "Иконки погоды"

    def __str__(self):
        return self.name


class HourlyForecast(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    datetime = models.DateTimeField(verbose_name="Дата и время прогноза")
    temperature = models.FloatField(verbose_name="Температура (°C)")
    feels_like = models.FloatField(verbose_name="Ощущается как (°C)", null=True, blank=True)
    icon = models.ForeignKey(WeatherIcon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Иконка погоды")
    condition = models.CharField(max_length=100, blank=True, verbose_name="Состояние (текст)")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Почасовой прогноз"
        verbose_name_plural = "Почасовые прогнозы"
        ordering = ("city", "datetime")
        indexes = [
            models.Index(fields=["city", "datetime"]),
        ]

    def __str__(self):
        dt = timezone.localtime(self.datetime) if self.datetime else None
        return f"{self.city.name} — {dt.strftime('%Y-%m-%d %H:%M') if dt else '—'}"


class AtmosphericData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    date = models.DateField(verbose_name="Дата")
    precipitation = models.FloatField(verbose_name="Осадки (мм)", default=0.0)
    wind_gusts = models.FloatField(verbose_name="Порывы ветра (м/с)", null=True, blank=True)
    uv_index = models.FloatField(verbose_name="УФ-индекс", null=True, blank=True)
    humidity = models.PositiveIntegerField(
        verbose_name="Влажность (%)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    dew_point = models.FloatField(verbose_name="Точка росы (°C)", null=True, blank=True)
    pressure = models.FloatField(verbose_name="Давление (гПа)", null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Атмосферные показатели"
        verbose_name_plural = "Атмосферные показатели"
        ordering = ("city", "date")
        unique_together = ("city", "date")
        indexes = [
            models.Index(fields=["city", "date"]),
        ]

    def __str__(self):
        return f"Атмосфера: {self.city.name} — {self.date}"


class SunAndVisibility(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, verbose_name="Город")
    sunrise = models.TimeField(verbose_name="Время восхода")
    sunset = models.TimeField(verbose_name="Время заката")
    road_visibility = models.FloatField(verbose_name="Видимость на дорогах (км)", null=True, blank=True)
    history = HistoricalRecords()


    class Meta:
        verbose_name = "Солнце и видимость"
        verbose_name_plural = "Солнце и видимость"

    def __str__(self):
        return f"{self.city.name} — восход {self.sunrise}, закат {self.sunset}"


class MoonAndPhases(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, verbose_name="Город")
    moon_phase = models.CharField(max_length=50, verbose_name="Фаза Луны")
    additional_info = models.TextField(blank=True, verbose_name="Дополнительные параметры")
    history = HistoricalRecords()


    class Meta:
        verbose_name = "Луна и фазы"
        verbose_name_plural = "Луна и фазы"

    def __str__(self):
        return f"{self.city.name} — {self.moon_phase}"


class WeatherConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    date = models.DateField(verbose_name="Дата")
    fact = models.BooleanField(verbose_name="Факт погоды (Да/Нет)")
    comment = models.TextField(blank=True, verbose_name="Комментарий пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время подтверждения")
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Подтверждение погоды"
        verbose_name_plural = "Подтверждения погоды"
        ordering = ("-created_at",)
        unique_together = ("user", "city", "date")

    def __str__(self):
        return f"{self.user.username} → {self.city.name} ({self.date}) : {'Да' if self.fact else 'Нет'}"

