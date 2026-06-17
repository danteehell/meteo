from rest_framework import serializers
from typing import Any

from .models import *


class CitySerializer(serializers.Serializer):
    """
    Сериализатор города.
    """

    name = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    views_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data: dict[str, Any]):
        """
        Создание города.
        """
        return City.objects.create(**validated_data)

    def update(self, instance, validated_data: dict[str, Any]):
        """
        Обновление города.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.country = validated_data.get("country", instance.country)
        instance.latitude = validated_data.get("latitude", instance.latitude)
        instance.longitude = validated_data.get("longitude", instance.longitude)
        instance.save()
        return instance


class WeatherIconSerializer(serializers.Serializer):
    """
    Сериализатор иконки погоды.
    """

    name = serializers.CharField(max_length=50)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)

    def create(self, validated_data: dict[str, Any]):
        return WeatherIcon.objects.create(**validated_data)

    def update(self, instance, validated_data: dict[str, Any]):
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.image_url = validated_data.get("image_url", instance.image_url)
        instance.save()
        return instance


class HourlyForecastSerializer(serializers.ModelSerializer):
    """
    Сериализатор почасового прогноза.
    """

    temperature_info = serializers.SerializerMethodField()
    is_actual = serializers.BooleanField(read_only=True)

    class Meta:
        model = HourlyForecast
        fields = [
            "id",
            "city",
            "datetime",
            "temperature",
            "feels_like",
            "icon",
            "condition",
            "temperature_info",
            "is_actual",
        ]

    def get_temperature_info(self, obj) -> str:
        """
        Человекочитаемое описание температуры.
        """
        if obj.temperature < 0:
            return "Холодно"
        elif obj.temperature < 15:
            return "Прохладно"
        elif obj.temperature < 25:
            return "Тепло"
        else:
            return "Жарко"


class WeatherConfirmationSerializer(serializers.ModelSerializer):
    """
    Сериализатор подтверждения погоды.
    """

    status_text = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    total_user_confirmations = serializers.IntegerField(read_only=True)

    class Meta:
        model = WeatherConfirmation
        fields = [
            "id",
            "user",
            "city",
            "date",
            "fact",
            "comment",
            "created_at",
            "status_text",
            "is_owner",
            "total_user_confirmations",
        ]

    def get_status_text(self, obj) -> str:
        """
        Текстовый статус подтверждения.
        """
        return "Подтверждено" if obj.fact else "Опровергнуто"

    def get_is_owner(self, obj) -> bool:
        """
        Проверка владельца записи.
        """
        user = self.context.get("request_user")
        if not user or user.is_anonymous:
            return False
        return obj.user == user


class ViewedCitySerializer(serializers.ModelSerializer):
    """
    Просмотренные города.
    """

    class Meta:
        model = ViewedCity
        fields = "__all__"


class SelectedCitySerializer(serializers.ModelSerializer):
    """
    Выбранный город пользователя.
    """

    class Meta:
        model = SelectedCity
        fields = "__all__"