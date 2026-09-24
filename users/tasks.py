from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def block_inactive_users():
    """
    Периодическая задача Celery Beat.
    Блокирует пользователей (is_active=False), если они не заходили на платформу больше 30 дней.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    # Ищем всех активных пользователей, у которых дата последнего входа раньше, чем месяц назад
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago
    )

    count = inactive_users.count()
    if count > 0:
        # Массово обновляем флаг активности
        inactive_users.update(is_active=False)
        print(
            f"[Celery Beat] Успешно заблокировано неактивных пользователей: {count}")
    else:
        print(
            "[Celery Beat] Неактивных пользователей для блокировки не найдено.")