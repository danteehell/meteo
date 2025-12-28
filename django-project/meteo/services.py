
import requests
import logging
from datetime import datetime
from django.utils import timezone
from .models import City, WeatherIcon, HourlyForecast, AtmosphericData, SunAndVisibility, MoonAndPhases

logger = logging.getLogger(__name__)

API_KEY = "53d088697ae38348278c04064b2a7a66"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


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
            response = requests.get(BASE_URL, params=params, timeout=30)
            if response.status_code == 401:
                print(f"Ошибка 401 Unauthorized для {city}.")
                print("Ответ сервера:", response.text)
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Попытка {attempt+1} для {city} не удалась, т.к.: {e}")
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
            "uv_index": None,
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
                "road_visibility": None,
            }
        )

    MoonAndPhases.objects.update_or_create(
        city=city,
        defaults={
            "moon_phase": "Неизвестно",
            "additional_info": "",
        }
    )
def sync_all_cities():
    for city in City.objects.all():
        data = fetch_weather_for_city(city)
        if not data:
            print(f"Пропускаем {city}, нет данных")
            continue
        update_models_from_weather(city, data)
        print(f"Обновлено: {city}")
