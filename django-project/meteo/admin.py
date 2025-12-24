from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from import_export.admin import ImportExportModelAdmin
from .models import (
    User,
    City,
    SelectedCity,
    ViewedCity,
    WeatherIcon,
    HourlyForecast,
    AtmosphericData,
    SunAndVisibility,
    MoonAndPhases,
    WeatherConfirmation,
)
from django.utils.timezone import now
from .resource import (
    UserResource,
    CityResource,
    WeatherIconResource,
    WeatherConfirmationResource,
)


class HourlyForecastInline(admin.TabularInline):
    model = HourlyForecast
    extra = 0
    raw_id_fields = ["icon"]


class AtmosphericDataInline(admin.TabularInline):
    model = AtmosphericData
    extra = 0


class SunAndVisibilityInline(admin.StackedInline):
    model = SunAndVisibility
    extra = 0


class MoonAndPhasesInline(admin.StackedInline):
    model = MoonAndPhases
    extra = 0


class SelectedCityInline(admin.TabularInline):
    model = SelectedCity
    extra = 0
    raw_id_fields = ["user"]


class ViewedCityInline(admin.TabularInline):
    model = ViewedCity
    extra = 0
    raw_id_fields = ["user"]


@admin.register(City)
class CityAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = CityResource

    @admin.display(description="Координаты")
    def coords(self, obj):
        return f"{obj.latitude}, {obj.longitude}"

    list_display = ["name", "country", "coords"]
    list_display_links = ["name"]
    list_filter = ["country"]
    search_fields = ["name", "country"]
    inlines = [
        HourlyForecastInline,
        AtmosphericDataInline,
        SunAndVisibilityInline,
        MoonAndPhasesInline,
    ]
    fieldsets = (
        ("Основная информация", {"fields": ("name", "country")}),
        ("Географические данные", {"fields": ("latitude", "longitude")}),
    )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = UserResource

    @admin.display(description="Дней с регистрации")
    def days_since_registration(self, obj):
        return (now() - obj.created_at).days

    list_display = ["id", "username", "email", "days_since_registration"]
    list_display_links = ["username"]
    list_filter = ["username", "email", "created_at"]
    search_fields = ["username", "email"]
    readonly_fields = ["created_at"]
    inlines = [SelectedCityInline, ViewedCityInline]
    date_hierarchy = "created_at"


@admin.register(WeatherIcon)
class WeatherIconAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = WeatherIconResource
    list_display = ["name", "image", "image_url"]
    search_fields = ["name"]
    search_fields = ["name", "country"]


@admin.register(WeatherConfirmation)
class WeatherConfirmationAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = WeatherConfirmationResource
    list_display = ["user", "city", "date", "fact", "created_at"]
    list_filter = ["fact", "date"]
    search_fields = ["user__username", "city__name"]
    readonly_fields = ["created_at"]
    date_hierarchy = "date"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(fact=True)
