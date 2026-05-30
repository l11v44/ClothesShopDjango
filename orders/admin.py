
from orders.models import Order, OrderItem
from django.contrib import admin

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'email', 'status', 'created_at']
    list_filter = ['status']
admin.site.register(OrderItem)