import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(name, description=None):
    """Создает продукт в платежной системе Stripe"""
    product = stripe.Product.create(
        name=name,
        description=description
    )
    return product.get('id')

def create_stripe_price(product_id, amount):
    """Создает цену для продукта в копейках (умножаем на 100)"""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency="rub",  # или "usd" в зависимости от валюты проекта
    )
    return price.get('id')

def create_stripe_session(price_id, success_url, cancel_url):
    """Создает Checkout-сессию Stripe для получения ссылки на оплату"""
    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
    )
    return session.get('id'), session.get('url')

def retrieve_stripe_session_status(session_id):
    """Получает актуальный статус сессии из Stripe (Дополнительное задание)"""
    session = stripe.checkout.Session.retrieve(session_id)
    return session.get('payment_status')  # Вернет 'paid', 'unpaid' или 'no_payment_required'