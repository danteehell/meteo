import django_filters
from .models import City

class CityFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(field_name='country', lookup_expr='iexact')
    min_lat = django_filters.NumberFilter(field_name='latitude', lookup_expr='gte')

    class Meta:
        model = City
        fields = ['country', 'min_lat']
