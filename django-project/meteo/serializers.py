#критерий3 1
from rest_framework import serializers

from .models import User, City, WeatherIcon


class CitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    def create(self, validated_data):
        return City.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.country = validated_data.get('country', instance.country)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance

class WeatherIconSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)

    def create(self, validated_data):
        return WeatherIcon.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.save()
        return instance
#критерий3 1

