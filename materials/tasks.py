from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from materials.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Асинхронная задача отправки писем всем подписчикам курса при его обновлении.
    Уведомление уходит только если курс не обновлялся последние 4 часа.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    now = timezone.now()

    # проверяем, когда курс обновлялся последний раз

    if course.last_update and (now - course.last_update) < timedelta(hours=4):
        return  # Если прошло меньше 4 часов, прерываем отправку

    # Фиксируем новое время обновления курса перед рассылкой
    course.last_update = now
    course.save()

    # Получаем email-адреса всех активных подписчиков этого курса
    subscriptions = Subscription.objects.filter(course=course)
    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if recipient_list:
        send_mail(
            subject=f"Обновление курса: {course.title}",
            message=f"Здравствуйте! Материалы курса '{course.title}' были обновлены. Зайдите на платформу, чтобы изучить новые уроки.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )
