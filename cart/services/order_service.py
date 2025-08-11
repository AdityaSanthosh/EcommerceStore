from datetime import timedelta

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
            discount_perc = DiscountCodes.objects.get(discount_code).perc
        cart = Cart.objects.get(cart_id)
        # Also Calculate Shipping Costs and factor in taxes
        return cart.value() * (1 - discount_perc)

    @classmethod
    def create_order(cls, cart_id, shipping_code, discount_code):
        cart = Cart.objects.get(cart_id)
        if not cart.locked_at:
            return None, "Cannot create an order without checking it out"
        if cart.locked_at < timezone.now() - timedelta(minutes=10):
            cart.locked_at = None
            for cart_item in cart.added_items.all():
                cart_item.locked_price = None
            return None, "Cart Checkout process timed out. Please Checkout again"
        user_id = cart.user_id
        discount_obj = DiscountCodes.objects.get(code=discount_code)
        order = Order.objects.create(user_id=user_id, status="payment_pending",
                                     actual_price=cls.calculate_total_price(cart_id, discount_code, shipping_code),
                                     discount_code=discount_code, discount_value=discount_obj.perc)
        # copy Cart Items into Order Items with frozen prices from cart items
        for cart_item in cart.added_items.all():
            actual_item = Item.objects.get(id=cart_item.item_id)
            OrderItem.objects.create(order=order, item=actual_item, price=cart_item.locked_price,
                                     quantity=cart_item.quantity)
        cart.clear()
        return order, None
