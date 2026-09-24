from django.urls import path
from users.apps import UsersConfig
from users.views import UserRegisterAPIView, PaymentListAPIView, \
    UserUpdateAPIView, PaymentStatusRetrieveAPIView, PaymentCreateAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("profile/<int:pk>/", UserUpdateAPIView.as_view(), name="user-profile"),
    # Регистрация и получение токенов
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payment/status/<int:pk>/', PaymentStatusRetrieveAPIView.as_view(), name='payment-status'),
]
