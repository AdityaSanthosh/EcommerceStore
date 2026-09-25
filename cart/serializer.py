from rest_framework import serializers

from .models import Cart, CartItem, Order, DiscountCodes


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, default=1)

    class Meta:
        model = CartItem
        fields = ("item", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="added_items", many=True, required=True)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "status", "locked_at", "items", "value"]


# POST {items: [{id: 1, quanti}]}
class AddToCartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, required=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class AddressSerializer(serializers.Serializer):
    pincode = serializers.CharField()


# /order/ {"cart_id": , "address": {"pincode":}, "discount_code": ""}
class CartCheckoutSerializer(serializers.Serializer):
    cart_id = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), label="Cart ID", required=True)
    address = AddressSerializer()
    discount_code = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_discount_code(self, value):
        if value and not DiscountCodes.objects.filter(code=value).exists():
            raise serializers.ValidationError("Invalid discount code")
        return value
