from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug= models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True , on_delete=models.CASCADE , related_name='children')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug= models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.db import models

class ProductVariant(models.Model):
    class Size(models.TextChoices):
        XS = 'XS', 'Extra Small'
        S = 'S', 'Small'
        M = 'M', 'Medium'
        L = 'L', 'Large'
        XL = 'XL', 'Extra Large'

    class Color(models.TextChoices):
        BLACK = 'BLACK', 'Black'
        WHITE = 'WHITE', 'White'
        BLUE = 'BLUE', 'Blue'
        RED = 'RED', 'Red'
        GREEN = 'GREEN', 'Green'

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=5, choices=Size.choices)
    color = models.CharField(max_length=10, choices=Color.choices)
    stock = models.IntegerField(default=0)

    class Meta:
        # Уникальный индекс: не может быть двух одинаковых размеров одного цвета для одного товара
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f"{self.product.name} | {self.size} | {self.color}"

