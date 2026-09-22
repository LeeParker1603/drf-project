import re
from rest_framework.serializers import ValidationError

def validate_youtube_link(value):
    """
    Проверяет, что ссылка ведет исключительно на youtube.com.
    """
    if value:
        # Регулярное выражение для проверки домена youtube.com или youtu.be
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
        if not re.match(youtube_regex, value):
            raise ValidationError("Разрешены ссылки только на внешние ресурсы youtube.com.")