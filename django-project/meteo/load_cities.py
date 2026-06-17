import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meteo.settings")
django.setup()

from meteo.models import City

# Очистка базы
City.objects.all().delete()
print("База городов очищена.")

# Загрузка JSON городов
json_file = r"C:\Users\Дарья\OneDrive\Desktop\coursework\project\django-project\city.list.json"
with open(json_file, "r", encoding="utf-8") as f:
    cities = json.load(f)

# Загрузка словаря перевода
translation_file = r"C:\Users\Дарья\OneDrive\Desktop\coursework\project\django-project\city_translations.json"
with open(translation_file, "r", encoding="utf-8") as f:
    city_translations = json.load(f)

count = 0
for c in cities:
    if c.get("country") != "RU":
        continue

    name_ru = city_translations.get(c["name"], c["name"])

    City.objects.get_or_create(
        name=name_ru,
        country="Россия",
        latitude=c["coord"]["lat"],
        longitude=c["coord"]["lon"]
    )
    count += 1

print(f"Всего добавлено городов России: {count}")
