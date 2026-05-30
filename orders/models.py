from django.contrib.auth.models import User
from django.db import models

from catalog.models import Product
from config import settings
STATUS_CHOICES = [
    ('pending', 'В обработке'),
    ('shipped', 'Отправлен'),
    ('delivered', 'Доставлен'),
]

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    address = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def get_total_cost(self):
        # self.items.all() — это 'related_name' из модели OrderItem.
        # Если ты его не задавал, попробуй self.orderitem_set.all()
        return sum(item.get_cost() for item in self.items.all())

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.paid}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items' ,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    def __str__(self):
        return f'{self.order} {self.product} {self.quantity}'

    def get_cost(self):
        return self.price * self.quantity