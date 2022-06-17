import json

from django.core.serializers import serialize
from rest_framework import serializers

from shopping.models import Cart, Order, OrderLimit, Shelf


class ShelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelf
        fields = ("products",)


class OrderLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLimit
        fields = ("region",)


class CartSerializer(serializers.ModelSerializer):
    region = OrderLimitSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(queryset=OrderLimit.objects.all())
    shelves_in_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        fields = (
            "id",
            "status",
            "shelves",
            "region",
            "region_id",
            "shelves_in_cart",
        )

    def get_shelves_in_cart(self, obj):
        return obj.shelves.count() if hasattr(obj, "shelves") else len(obj["shelves"])


class OrderSerializer(serializers.ModelSerializer):
    region = OrderLimitSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(queryset=OrderLimit.objects.all())
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all())

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "cart",
            "cart_id",
            "region",
            "region_id",
        )
        depth = 2
