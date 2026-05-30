from django.contrib import admin

# Register your models here.
from catalog.models import Product , Category , ProductVariant

admin.site.register(Category)


from django.contrib import admin
from .models import Product, Category, ProductVariant

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1 # Сколько пустых полей показывать для новых вариаций

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = ('name', 'price', 'category')