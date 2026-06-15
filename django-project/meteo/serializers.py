# критерий3 1
from rest_framework import serializers

from .models import *


class CitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    views_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        return City.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.country = validated_data.get("country", instance.country)
        instance.latitude = validated_data.get("latitude", instance.latitude)
        instance.longitude = validated_data.get("longitude", instance.longitude)
        instance.save()
        return instance


class WeatherIconSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)

    def create(self, validated_data):
        return WeatherIcon.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.image_url = validated_data.get("image_url", instance.image_url)
        instance.save()
        return instance


# критерий3 1



class HourlyForecastSerializer(serializers.ModelSerializer):
    temperature_info = serializers.SerializerMethodField()
    is_actual = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = HourlyForecast
        fields = '__all__'

    def get_temperature_info(self, obj):
        if obj.temperature < 0:
            return "Холодно"
        elif obj.temperature < 15:
            return "Прохладно"
        elif obj.temperature < 25:
            return "Тепло"
        else:
            return "Жарко"


class WeatherConfirmationSerializer(serializers.ModelSerializer):
    status_text = serializers.SerializerMethodField()

    class Meta:
        model = WeatherConfirmation
        fields = '__all__'
    
    def get_status_text(self, obj):
        return "Подтверждено" if obj.fact else "Опровергнуто"
    
    def get_is_owner(self, obj):
        user = self.context.get('request_user')
        if not user or user.is_anonymous:
            return False
        return obj.user == user



class ViewedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewedCity
        fields = '__all__'


from .models import SelectedCity


class SelectedCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedCity
        fields = '__all__'