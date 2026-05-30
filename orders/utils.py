from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation(order):
    subject = f'Заказ №{order.id} оформлен'
    message = f'Здравствуйте, {order.first_name}!\n\nВаш заказ №{order.id} принят в обработку. Сумма: {order.total_price} $.'

    # Письмо покупателю
    send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])

    # Письмо администратору
    send_mail(f'Новый заказ №{order.id}', f'Поступил новый заказ от {order.first_name} {order.last_name}.',
              settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])