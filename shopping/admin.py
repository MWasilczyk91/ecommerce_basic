from django.contrib.admin import ModelAdmin, register

from shopping.models import Cart, Order, OrderLimit, Shelf


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("status", "region")
    ordering = ("status", "region")


@register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("cart", "status", "region")
    ordering = ("status", "region")


@register(Shelf)
class ShelfAdmin(ModelAdmin):
    list_display = ("products",)
    list_filter = ("products",)
    ordering = ("products",)


@register(OrderLimit)
class OrderLimitAdmin(ModelAdmin):
    list_display = ("region", "used_limit", "daily_limit")
    ordering = ("used_limit", "daily_limit")
