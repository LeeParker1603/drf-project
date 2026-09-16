from django.urls import path
from users.apps import UsersConfig
from users.views import PaymentListAPIView, UserUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('profile/<int:pk>/', UserUpdateAPIView.as_view(), name='user-profile'),
]