from import_export import resources, fields
from .models import User, City, WeatherIcon, WeatherConfirmation
from django.utils.timezone import now


class UserResource(resources.ModelResource):
    full_name = fields.Field(column_name="Full Name")

    class Meta:
        model = User
        fields = ("id", "username", "email", "created_at")
        export_order = ("id", "username", "email", "created_at")

    def dehydrate_full_name(self, obj):
        return obj.username

    def get_export_queryset(self):
        if hasattr(User, "is_active"):
            return self.get_queryset().filter(is_active=True)
        return self.get_queryset()


class CityResource(resources.ModelResource):
    coords = fields.Field(column_name="Coordinates")

    class Meta:
        model = City
        fields = ("id", "name", "country", "latitude", "longitude")
        export_order = ("id", "name", "country", "latitude", "longitude")

    def dehydrate_coords(self, obj):
        return f"{obj.latitude}lat, {obj.longitude}lon"

    def get_export_queryset(self):
        return self.get_queryset()


class WeatherIconResource(resources.ModelResource):
    icon_name = fields.Field(column_name="Icon Name")
    image_url_field = fields.Field(column_name="Image URL")

    class Meta:
        model = WeatherIcon
        fields = ("id", "name", "icon_name", "image_url_field")
        export_order = ("id", "name", "icon_name", "image_url_field")

    def dehydrate_icon_name(self, obj):
        return f"{obj.name} (иконка)" if obj.name else "Нет имени"

    def dehydrate_image_url_field(self, obj):
        return obj.image_url if obj.image_url else "Нет URL"

    def get_export_queryset(self):
        return self.get_queryset().filter(name__isnull=False)


class WeatherConfirmationResource(resources.ModelResource):
    user_name = fields.Field(column_name="User")
    city_name = fields.Field(column_name="City")
    days_since_creation = fields.Field(column_name="Days Since Created")

    class Meta:
        model = WeatherConfirmation
        fields = (
            "id",
            "user",
            "city",
            "date",
            "fact",
            "days_since_creation",
            "comment",
        )
        export_order = (
            "id",
            "user",
            "city",
            "date",
            "fact",
            "days_since_creation",
            "comment",
        )

    def dehydrate_fact(self, obj):
        return "Да" if obj.fact else "Нет"

    def dehydrate_days_since_creation(self, obj):
        return (now() - obj.created_at).days
