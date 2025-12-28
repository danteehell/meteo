from django.core.management.base import BaseCommand
from meteo.services import sync_all_cities

class Command(BaseCommand):
    help = "Заполняет модели погодой из OpenWeatherMap"

    def handle(self, *args, **options):
        sync_all_cities()
        self.stdout.write(self.style.SUCCESS("Данные о погоде обновлены для всех городов"))
