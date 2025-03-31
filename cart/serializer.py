from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Cart, Item, CartItem, Order

User = get_user_model()


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            "name",
            "created_at",
            "updated_at",
            "actual_price",
            "discounted_price",
        )


class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ("item", "quantity")


class CartSerializer(serializers.ModelSerializer):
    added_items = CartItemSerializer(many=True, required=False)

    class Meta:
        model = Cart
        fields = ["added_items", "actual_price", "discounted_price"]


class AddToCartSerializer(serializers.Serializer):
    items = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), label="Item ID", many=True, required=True
    )


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = "__all__"
