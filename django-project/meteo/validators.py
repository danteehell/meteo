from django.conf import settings
from django.core.exceptions import ValidationError


def base_str_validator(
    value: str,
    model=None,
    field_name: str | None = None,
    instance=None
) -> None:
    """
    Базовый валидатор строковых значений.

    Проверяет:
    - первая буква заглавная
    - отсутствие цифр
    - отсутствие запрещённых слов
    - уникальность значения в модели (если передана модель)

    Args:
        value: проверяемая строка
        model: Django-модель для проверки уникальности
        field_name: имя поля модели
        instance: текущий объект (для исключения при update)
    """

    if not value:
        return

    if value != value.capitalize():
        raise ValidationError(
            "Первая буква должна быть заглавной, остальные строчные."
        )

    lower_value = value.lower()

    for word in getattr(settings, "FORBIDDEN_WORDS", []):
        if word.lower() in lower_value:
            raise ValidationError(
                "Введённое содержит недопустимую лексику."
            )

    if any(char.isdigit() for char in value):
        raise ValidationError(
            "Название не должно содержать цифры."
        )

    if model and field_name:
        qs = model.objects.filter(**{f"{field_name}__iexact": value})

        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise ValidationError(
                f'Значение "{value}" уже существует в базе.'
            )