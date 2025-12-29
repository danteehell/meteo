import requests
import logging
from datetime import datetime
from django.utils import timezone
from .models import City, WeatherIcon, HourlyForecast, AtmosphericData, SunAndVisibility, MoonAndPhases

logger = logging.getLogger(__name__)

API_KEY = "53d088697ae38348278c04064b2a7a66"

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

BASE_GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"


def fetch_weather_for_city(city: City):
    params = {
        "lat": city.latitude,
        "lon": city.longitude,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    for attempt in range(3):
        try:
            response = requests.get(BASE_WEATHER_URL, params=params, timeout=30)
            if response.status_code == 401:
                print(f"Ошибка 401 Unauthorized для {city}. Ответ сервера: {response.text}")
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Попытка {attempt+1} для {city} не удалась: {e}")
    return None


def fetch_or_create_city_by_name(city_name: str, country: str = None):
    qs = City.objects.filter(name__iexact=city_name)
    if country:
        qs = qs.filter(country__iexact=country)
    if qs.exists():
        return qs.first()

    params = {"q": city_name, "limit": 1, "appid": API_KEY}
    if country:
        params["q"] = f"{city_name},{country}"

    try:
        response = requests.get(BASE_GEOCODE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data:
            print(f"Город {city_name} не найден через API")
            return None

        city_info = data[0]
        city_obj = City.objects.create(
            name=city_info["name"],
            country=city_info.get("country", ""),
            latitude=city_info["lat"],
            longitude=city_info["lon"]
        )
        return city_obj
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при поиске города {city_name}: {e}")
        return None


def update_models_from_weather(city: City, data: dict):
    weather = data.get("weather", [{}])[0]
    main = data.get("main", {})
    icon_code = weather.get("icon")
    condition = weather.get("description", "")

    icon, _ = WeatherIcon.objects.get_or_create(
        name=icon_code,
        defaults={"image_url": f"http://openweathermap.org/img/wn/{icon_code}.png"}
    )
    dt_now = timezone.now()
    HourlyForecast.objects.update_or_create(
        city=city,
        datetime=dt_now,
        defaults={
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "icon": icon,
            "condition": condition,
        }
    )

    AtmosphericData.objects.update_or_create(
        city=city,
        date=dt_now.date(),
        defaults={
            "precipitation": data.get("rain", {}).get("1h", 0.0),
            "wind_gusts": data.get("wind", {}).get("gust"),
            "humidity": main.get("humidity"),
            "dew_point": None,
            "pressure": main.get("pressure"),
            "uv_index": data.get("uvi"),
        }
    )

    sys_data = data.get("sys", {})
    sunrise_ts = sys_data.get("sunrise")
    sunset_ts = sys_data.get("sunset")
    if sunrise_ts and sunset_ts:
        sunrise_time = datetime.fromtimestamp(sunrise_ts).time()
        sunset_time = datetime.fromtimestamp(sunset_ts).time()
        SunAndVisibility.objects.update_or_create(
            city=city,
            defaults={
                "sunrise": sunrise_time,
                "sunset": sunset_time,
                "road_visibility": data.get("visibility"),
            }
        )

    MoonAndPhases.objects.update_or_create(
        city=city,
        defaults={
            "moon_phase": "Неизвестно",
            "additional_info": "",
        }
    )


def sync_all_cities(city_names=None):
    if city_names:
        for name in city_names:
            fetch_or_create_city_by_name(name)

    for city in City.objects.all():
        data = fetch_weather_for_city(city)
        if not data:
            print(f"Пропускаем {city}, нет данных")
            continue
        update_models_from_weather(city, data)
        print(f"Обновлено: {city}")
