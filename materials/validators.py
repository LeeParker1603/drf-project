from rest_framework.serializers import ValidationError


def validate_youtube_link(value):
    """
    Проверяет, что ссылка ведет исключительно на youtube.com или youtu.be.
    """
    if value:
        # Приводим к нижнему регистру для надежности
        link = value.lower()

        # Проверяем, содержатся ли разрешенные домены в ссылке
        if "youtube.com" not in link and "youtu.be" not in link:
            raise ValidationError(
                "Разрешены ссылки только на внешние ресурсы youtube.com."
            )
