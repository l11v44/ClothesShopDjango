from django.db import models
from catalog.models import ProductVariant
# Create your models here.

class CartItem(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    session_id = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.product_variant} {self.quantity} {self.session_id}'