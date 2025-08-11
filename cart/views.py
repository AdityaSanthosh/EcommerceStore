import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import User, Cart
from cart.serializer import CartSerializer, AddToCartSerializer, OrderSerializer, CartCheckoutSerializer
from cart.services.order_service import OrderService


def get_user(request):
    user_id = request.META["HTTP_USER_ID"]
    return get_object_or_404(User, pk=user_id)


class CartView(APIView):
    def get(self, request):
        user = get_user(request)
        serializer = CartSerializer(user.cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT /cart/ {items: [{id: 1, quanti}]}
    def put(self, request):
        user = get_user(request)
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["items"]

        cart = user.cart
        success = cart.add_items(items=[{item.id, item.quantity} for item in items])
        if success:
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False)
    def checkout(self, request):
        user = get_user(request)
        # on checkout, freeze the price (copy item's actual_price to cart_item's locked_price and change the cart status to LOCKED)
        cart = Cart.objects.prefetch_related("added_items__item").get(user=user)
        if cart.status == Cart.Status.LOCKED:
            return Response(
                {"error": "Cart already checked out"},
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            for cart_item in cart.added_items.all().all():
                # Lock price at checkout time
                cart_item.locked_price = cart_item.item.actual_price
                cart_item.save()

            # Lock the cart for 10 minutes
            cart.status = Cart.Status.LOCKED
            cart.locked_at = timezone.now()
            cart.save()

        return Response({
            "message": "Cart locked for checkout for 10 minutes.",
            "locked_until": cart.locked_at + datetime.timedelta(minutes=10),
        })

    @action(methods=['get'], detail=False)
    def value(self, request):
        user = get_user(request)
        serializer = CartCheckoutSerializer(request.data)
        cart_id, address, discount_code = serializer.validated_data
        if user.cart.id != cart_id:
            return Response(data="This Cart ID doesn't belong to you", status=status.HTTP_403_FORBIDDEN)
        total_price = OrderService.calculate_total_price(cart_id, discount_code, shipping_code=address['pincode'])
        return Response({"total_price": total_price})


# 1. Checkout the cart which freezes the prices for 10 mins
# 2. Get total price which calculates cart value with frozen prices after checkout
# 3. Place order considering checked out prices
# 4. Proceed with payment which means order is placed and payment is attached to it later

# /order/ {"cart_id": , "address": {"pincode":}
class OrderView(APIView):
    def post(self, request):
        user = get_user(request)
        serializer = CartCheckoutSerializer(request.data)
        cart_id, address, discount_code = serializer.validated_data
        cart = user.cart
        if cart.id != cart_id:
            return Response(data="This Cart ID doesn't belong to you", status=status.HTTP_403_FORBIDDEN)
        # if valid_discount_code(user, discount_code):
        #     return Response(data="Invalid Coupon Code Entered", status=status.HTTP_400_BAD_REQUEST)
        order, error = OrderService.create_order(cart_id, address['pincode'], discount_code)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
