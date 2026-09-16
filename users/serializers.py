from rest_framework import serializers
from users.models import Payment, User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only={'password': True})

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'city']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    # Включаем историю платежей пользователя
    payments_history = PaymentSerializer(source='payments', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'payments_history']

