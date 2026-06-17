from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from meteo.models import (
    City,

)


class Command(BaseCommand):
    help = "Fill database with bulk test data"

    def handle(self, *args, **kwargs):
        self.stdout.write("START")
        self.stdout.write("Seeding database...")

        users = []
        cities = []
        icons = []
        # CITIES (15)
        city_names = [
            "Moscow", "Paris", "Oslo", "Berlin", "Rome",
            "Madrid", "London", "Tokyo", "Seoul", "Prague",
            "Warsaw", "Helsinki", "Vienna", "Lisbon", "Dublin"
        ]

        for i in range(15):
            cities.append(
                City.objects.create(
                    name=city_names[i],
                    country="Country" + str(i),
                    latitude=random.randint(40, 60),
                    longitude=random.randint(10, 40)
                )
            )

       

        self.stdout.write(self.style.SUCCESS("Database fully seeded (15+ each table)!"))