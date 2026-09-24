from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class MaterialsTestCase(APITestCase):

    def setUp(self):
        # Создаем тестовых пользователей
        self.user = User.objects.create_user(
            email="user@test.com", password="password123"
        )
        self.another_user = User.objects.create_user(
            email="another@test.com", password="password123"
        )

        # Создаем тестовый курс и урок
        self.course = Course.objects.create(
            title="Django Course", description="Learn DRF"
        )
        self.lesson = Lesson.objects.create(
            title="Lesson 1",
            description="Intro",
            video_url="https://youtube.com",
            course=self.course,
            owner=self.user,
        )

    # ==========================================
    # ТЕСТЫ CRUD ДЛЯ УРОКОВ
    # ==========================================

    def test_lesson_create_valid_video(self):
        """Тестирование создания урока с валидной ссылкой на youtube"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "New Lesson",
            "description": "Valid video link",
            "video_url": "https://youtube.com",
            "course": self.course.id,
            "owner": self.user.id,
        }

        response = self.client.post(reverse("materials:lesson-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_invalid_video(self):
        """Тестирование создания урока с запрещенной ссылкой"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Bad Lesson",
            "description": "Invalid link",
            "video_url": "https://wikipedia.org",
            "course": self.course.id,
            "owner": self.user.id,
        }
        response = self.client.post(reverse("materials:lesson-create"), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_list(self):
        """Тестирование получения списка уроков (Read List)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("materials:lesson-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_lesson_retrieve(self):
        """Тестирование получения одного конкретного урока (Read Detail)"""
        self.client.force_authenticate(user=self.user)
        # Для generic-путей обычно используется kwargs={'pk': self.lesson.pk}
        response = self.client.get(
            reverse("materials:lesson-get", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.lesson.title)

    def test_lesson_update_owner(self):
        """Тестирование обновления урока его владельцем (Update)"""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Updated Lesson Title", "course": self.course.id}
        response = self.client.patch(
            reverse("materials:lesson-update", kwargs={"pk": self.lesson.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Lesson Title")

    def test_lesson_delete_owner(self):
        """Тестирование удаления урока владельцем (Delete)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("materials:lesson-delete", kwargs={"pk": self.lesson.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    # ==========================================
    # ТЕСТЫ ПРАВ ДОСТУПА (Permissions)
    # ==========================================

    def test_lesson_update_anonymous(self):
        """Попытка обновления урока неавторизованным пользователем"""

        data = {"title": "Hack Title"}
        response = self.client.patch(
            reverse("materials:lesson-update", kwargs={"pk": self.lesson.pk}), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================================
    # ТЕСТ ФУНКЦИОНАЛА ПОДПИСКИ
    # ==========================================

    def test_subscription_toggle(self):
        """Тестирование добавления и удаления подписки"""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:course-subscribe")
        data = {"course_id": self.course.id}

        # Добавление подписки
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

        # Удаление подписки
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )
