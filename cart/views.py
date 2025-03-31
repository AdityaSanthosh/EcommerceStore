from django.contrib.auth import get_user_model
from django.db.models import Sum, Case, When, Value, F
from django.forms import DecimalField
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from cart.domain.discount import is_discount_available
from cart.models import Cart, Order
from cart.serializer import CartSerializer, AddToCartSerializer, OrderSerializer

User = get_user_model()


def get_user(request):
    user_id = request.META["HTTP_USER_ID"]
    return get_object_or_404(User, pk=user_id)


class CartView(APIView):
    def get(self, request):
        user = get_user(request)
        cart, _ = Cart.objects.get_or_create(user_id=user.id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemsView(APIView):
    def put(self, request):
        user = get_user(request)

        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["items"]

        cart, _ = Cart.objects.get_or_create(user_id=user.id)
        success = cart.add_items(item_ids=[item.id for item in items])
        if success:
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartCheckoutDiscountView(APIView):

    def get(self, request):
        get_user(request)
        return Response(is_discount_available(), status=status.HTTP_200_OK)

    def put(self, request):
        user = get_user(request)

        cart, _ = Cart.objects.get_or_create(user_id=user.id)
        discount_data = is_discount_available()
        if discount_data["eligible"]:
            cart.apply_discount(
                code=discount_data["details"]["code"],
                value=discount_data["details"]["value"],
            )
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartCheckoutPaymentView(APIView):

    def put(self, request):
        user = get_user(request)
        cart = user.cart
        order = Order(
            user=user,
            status="paid",
            price_paid=cart.discounted_price,
            actual_price=cart.actual_price,
            discount_value=cart.discount_value,
            discount_code=cart.discount_code,
        )
        order.save()
        cart.clear()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class AdminDiscountCheck(APIView):
    def get(self, request):
        get_user(request)
        return Response(is_discount_available(), status=status.HTTP_200_OK)


class AdminOrderAnalytics(APIView):
    def get(self, request):
        orders = Order.objects.filter(status="paid")
        total_purchased_amount = float(
            orders.aggregate(total_purchased=Sum("actual_price"))["total_purchased"]
            or 0.00
        )
        discount_codes = orders.values_list("discount_code", flat=True).distinct()
        total_discount_amount = orders.aggregate(
            total_discount=Sum(F("discount_value"))
        )["total_discount"]

        return Response(
            {
                "no_of_orders": orders.count(),
                "total_purchased_amount": total_purchased_amount,
                "discount_codes": list(filter(None, discount_codes)),
                "total_discount_amount": total_discount_amount,
            },
            status=status.HTTP_200_OK,
        )
