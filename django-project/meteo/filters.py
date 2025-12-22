import django_filters

from .models import City, WeatherIcon


class CityFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name="country", lookup_expr="iexact", label="Страна"
    )
    lat = django_filters.NumberFilter(
        field_name="latitude", lookup_expr="exact", label="Точная широта"
    )
    lon = django_filters.NumberFilter(
        field_name="longitude", lookup_expr="exact", label="Точная долгота"
    )
    min_lat = django_filters.NumberFilter(
        field_name="latitude", lookup_expr="gte", label="Минимальная широта"
    )
    max_lat = django_filters.NumberFilter(
        field_name="latitude", lookup_expr="lte", label="Максимальная широта"
    )
    min_lon = django_filters.NumberFilter(
        field_name="longitude", lookup_expr="gte", label="Минимальная долгота"
    )
    max_lon = django_filters.NumberFilter(
        field_name="longitude", lookup_expr="lte", label="Максимальная долгота"
    )

    class Meta:
        model = City
        fields = ["country", "lat", "lon", "min_lat", "max_lat", "min_lon", "max_lon"]


historical_records = WeatherIcon.history.all()


class HistoricalWeatherIconFilter(django_filters.FilterSet):
    date_exact = django_filters.DateTimeFilter(
        field_name="history_date", lookup_expr="exact", label="Дата добавления"
    )
    date_before = django_filters.DateTimeFilter(
        field_name="history_date", lookup_expr="lte", label="До"
    )
    date_after = django_filters.DateTimeFilter(
        field_name="history_date", lookup_expr="gte", label="После"
    )
    date_range = django_filters.DateFromToRangeFilter(
        field_name="history_date", label="В промежутке между"
    )

    class Meta:
        model = WeatherIcon
        fields = ["date_exact", "date_before", "date_after", "date_range"]
