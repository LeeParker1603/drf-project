import os

from celery import Celery

# Устанавливаем настройки Django по умолчанию для celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Читаем настройки из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим задачи в файлах tasks.py ваших приложений
app.autodiscover_tasks()
