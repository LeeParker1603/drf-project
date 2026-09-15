from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer

class UserUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Подключаем бэкенды для фильтрации и сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # Поля для фильтрации по курсу, уроку или способу оплаты
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')

    # Поля для сортировки (по дате оплаты)
    ordering_fields = ('payment_date',)

