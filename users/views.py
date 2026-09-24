from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Payment, User
from users.permissions import IsProfileOwner
from users.serializers import PaymentSerializer, UserRegisterSerializer, UserSerializer
from users.services import (
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    retrieve_stripe_session_status,
)


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)


class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [
                IsAuthenticated(),
                IsProfileOwner(),
            ]  # Редактировать может только хозяин профиля
        return [IsAuthenticated()]  # Смотреть общую инфу может любой вошедший


class PaymentCreateAPIView(generics.CreateAPIView):
    """Эндпоинт инициализации платежа за курс или урок"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Сначала валидируем и сохраняем черновик платежа в нашей системе
        payment = serializer.save(user=self.request.user, payment_status="unpaid")

        # Определяем, за что идет оплата (курс или урок)
        paid_item = payment.paid_course if payment.paid_course else payment.paid_lesson

        # 1. Создаем продукт в Stripe
        stripe_product_id = create_stripe_product(
            name=paid_item.title, description=paid_item.description
        )

        # 2. Создаем цену в копейках
        stripe_price_id = create_stripe_price(
            product_id=stripe_product_id, amount=payment.amount
        )

        # 3. Генерируем сессию оплаты
        if payment.paid_course:
            success_url = self.request.build_absolute_uri(
                reverse(
                    "materials:course-detail", kwargs={"pk": payment.paid_course.id}
                )
            )
        else:
            success_url = self.request.build_absolute_uri(
                reverse("materials:lesson-get", kwargs={"pk": payment.paid_lesson.id})
            )

        cancel_url = self.request.build_absolute_uri(
            reverse("users:payment-status", kwargs={"pk": payment.id})
        )

        session_id, payment_url = create_stripe_session(
            price_id=stripe_price_id, success_url=success_url, cancel_url=cancel_url
        )

        # 4. Сохраняем полученные данные платежной сессии в нашу БД
        payment.stripe_session_id = session_id
        payment.payment_link = payment_url
        payment.save()


# =========================================================================
# Контроллер синхронизации и проверки статуса
# =========================================================================
class PaymentStatusRetrieveAPIView(generics.RetrieveAPIView):
    """Эндпоинт для ручной или автоматической проверки актуального статуса платежа"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.stripe_session_id:
            # Запрашиваем актуальный статус у Stripe API
            stripe_status = retrieve_stripe_session_status(instance.stripe_session_id)
            # Синхронизируем статус с нашей базой данных
            instance.payment_status = stripe_status
            instance.save()

        # Возвращаем обновленный объект платежа
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Подключаем бэкенды для фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Поля для фильтрации по курсу, уроку или способу оплаты
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")

    # Поля для сортировки (по дате оплаты)
    ordering_fields = ("payment_date",)
