from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from cart.models import DiscountCodes, Cart, Order, OrderItem, Item


class OrderService:

    @staticmethod
    def calculate_total_price(cart_id: int, discount_code: str, shipping_code: str):
        """
        calculate value of items along with considering shipping, taxes, fees, offers/discounts
        """
        discount_perc = 0
        if discount_code:
            discount_perc = DiscountCodes.objects.get(code=discount_code).perc
        cart = Cart.objects.get(pk=cart_id)
        # Also Calculate Shipping Costs and factor in taxes
        return cart.value() * (1 - discount_perc / 100)

    @classmethod
    def create_order(cls, cart_id, shipping_code, discount_code):
        cart = Cart.objects.get(pk=cart_id)
        if cart.status != Cart.Status.LOCKED or not cart.locked_at:
            return None, "Cannot create an order without checking it out"
        if cart.locked_at < timezone.now() - timedelta(minutes=10):
            cart.status = Cart.Status.ACTIVE
            cart.locked_at = None
            cart.save()
            cart.added_items.update(locked_price=None)
            return None, "Cart Checkout process timed out. Please Checkout again"
        user_id = cart.user_id
        discount_value = 0
        if discount_code:
            discount_value = DiscountCodes.objects.get(code=discount_code).perc
        with transaction.atomic():
            order = Order.objects.create(user_id=user_id, status="payment_pending",
                                         actual_price=cls.calculate_total_price(cart_id, discount_code, shipping_code),
                                         discount_code=discount_code, discount_value=discount_value)
            # copy Cart Items into Order Items with frozen prices from cart items
            for cart_item in cart.added_items.all():
                actual_item = Item.objects.get(id=cart_item.item_id)
                OrderItem.objects.create(order=order, item=actual_item, price=cart_item.locked_price,
                                         quantity=cart_item.quantity)
            # Cart is closed once ordered; the user gets a fresh cart on the next access
            cart.status = Cart.Status.ORDERED
            cart.save()
        return order, None
