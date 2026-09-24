from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import Payment, User


class PaymentTestCase(APITestCase):

    def setUp(self):
        # Создаем тестового пользователя и авторизуем его
        self.user = User.objects.create_user(
            email="student@test.com", password="password123"
        )

        # Создаем тестовый курс и урок в материалах, чтобы было за что платить
        self.course = Course.objects.create(
            title="Python Advanced", description="LMS Project"
        )
        self.lesson = Lesson.objects.create(
            title="Stripe Integration", description="Lesson 1", course=self.course
        )

        # Создаем один черновик платежа в базе данных для теста статуса (ID будет равен 1)
        self.payment = Payment.objects.create(
            user=self.user,
            amount=5000,
            paid_course=self.course,
            payment_method="transfer",
            stripe_session_id="cs_test_initial_id",
            payment_status="unpaid",
        )

    # ==========================================
    # ТЕСТЫ ИНТЕГРАЦИИ STRIPE
    # ==========================================

    @patch("users.services.stripe.Product.create")
    @patch("users.services.stripe.Price.create")
    @patch("users.services.stripe.checkout.Session.create")
    def test_payment_create_endpoint(
        self, mock_session_create, mock_price_create, mock_product_create
    ):
        """Тестирование создания платежа и получения ссылки на оплату Stripe"""
        self.client.force_authenticate(user=self.user)

        # Подменяем ответы от Stripe API имитацией JSON-структур
        mock_product_create.return_value = {"id": "prod_mock_123"}
        mock_price_create.return_value = {"id": "price_mock_123"}
        mock_session_create.return_value = {
            "id": "cs_mock_123",
            "url": "https://stripe.com",
        }

        # Данные для POST-запроса на создание нового платежа
        data = {
            "amount": 7500,
            "user": self.user.id,
            "paid_course": self.course.id,
            "payment_method": "cash",
        }

        response = self.client.post(reverse("users:payment-create"), data=data)

        # print("\n=== ОШИБКА СЕРИАЛИЗАТОРА ПЛАТЕЖЕЙ ===", response.data)

        # Проверяем успешность создания
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что в ответе пользователю вернулась сгенерированная ссылка на оплату
        self.assertEqual(response.data["payment_link"], "https://stripe.com")

        # Проверяем, что ID сессии успешно сохранился в базе данных
        last_payment = Payment.objects.order_by("id").last()
        self.assertEqual(last_payment.stripe_session_id, "cs_mock_123")

    # ==========================================
    # ТЕСТ ПРОВЕРКИ СТАТУСА
    # ==========================================

    @patch("users.services.stripe.checkout.Session.retrieve")
    def test_payment_status_sync_endpoint(self, mock_session_retrieve):
        """Тестирование эндпоинта получения актуального статуса сессии из Stripe"""
        self.client.force_authenticate(user=self.user)

        # Имитируем, что Stripe возвращает статус 'paid' (оплачено)
        mock_session_retrieve.return_value = {"payment_status": "paid"}

        # Делаем GET-запрос на проверку статуса созданного в setUp платежа
        response = self.client.get(
            reverse("users:payment-status", kwargs={"pk": self.payment.pk})
        )

        # Проверяем успешность GET-запроса
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что статус в JSON-ответе изменился на 'paid'
        self.assertEqual(response.data["payment_status"], "paid")

        # Проверяем, что изменения засинхронизировались и сохранились в локальной базе данных
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.payment_status, "paid")
