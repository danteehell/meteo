from django.core.exceptions import ValidationError
from django.conf import settings

def base_str_validator(value, model=None, field_name=None, instance=None):
    if not value:
        return

    if value != value.capitalize():
        raise ValidationError('Первая буква должна быть заглавной, остальные строчные.')

    lower_value = value.lower()
    for word in getattr(settings, 'FORBIDDEN_WORDS', []):
        if word in lower_value:
            raise ValidationError('Введённое содержит недопустимую лексику.')
    
    if any(char.isdigit() for char in value):
        raise ValidationError('Название не должно содержать цифры.')

    if model and field_name:
        qs = model.objects.filter(**{f"{field_name}__iexact": value})
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise ValidationError(f'Значение "{value}" уже существует в базе.')
