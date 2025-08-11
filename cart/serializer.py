from django.db.models import CharField
from rest_framework import serializers

from .models import Cart, CartItem, Order


class CartItemSerializer(serializers.Serializer):
    class Meta:
        model = CartItem
        fields = ("item", "quantity")


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, required=True)

    class Meta:
        fields = ["items"]


# POST {items: [{id: 1, quanti}]}
class AddToCartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, required=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


# /order/ {"cart_id": , "address": {"pincode":}, "discount_code": ""}
class CartCheckoutSerializer(serializers.Serializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), label="Cart ID", required=True)
    address = serializers.DictField(pincode=CharField())
    discount_code = serializers.CharField()
