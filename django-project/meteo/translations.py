import json
from deep_translator import GoogleTranslator

json_file = r"C:\Users\Дарья\OneDrive\Desktop\coursework\project\django-project\city.list.json"
translation_file = r"C:\Users\Дарья\OneDrive\Desktop\coursework\project\django-project\city_translations.json"

translator = GoogleTranslator(source='en', target='ru')
translations = {}

with open(json_file, "r", encoding="utf-8") as f:
    cities = json.load(f)

for c in cities:
    if c.get("country") != "RU":
        continue
    name_en = c["name"]
    if name_en not in translations:
        try:
            name_ru = translator.translate(name_en)
        except Exception:
            name_ru = name_en
        translations[name_en] = name_ru

# Сохраняем словарь
with open(translation_file, "w", encoding="utf-8") as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print("Словарь перевода создан")
