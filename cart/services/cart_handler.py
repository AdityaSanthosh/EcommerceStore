from cart.models import Cart, Item, CartItem
import typing
from dataclasses import dataclass


@dataclass
class CartItemType:
    item: Item
    quantity: int = 1


class CartHandler:

    def __init__(self, cart: Cart):
        self.cart = cart
        self.cart_items = self.cart.added_items.all()

    def add_items(self, items: typing.List[typing.Dict]):
        # Adding items to a checked out cart invalidates the frozen prices, so the cart has to be checked out again
        if self.cart.status == Cart.Status.LOCKED:
            self.cart.status = Cart.Status.ACTIVE
            self.cart.locked_at = None
            self.cart.save()
            self.cart_items.update(locked_price=None)
        for item in items:
            try:
                # Cart might already have the item. If so, just increase the quantity by specified amount
                cart_item = CartItem.objects.get(cart=self.cart, item=item["item"])
                cart_item.quantity += item["quantity"]
                cart_item.save()
            except CartItem.DoesNotExist:
                CartItem.objects.create(cart=self.cart, item=item["item"], quantity=item["quantity"])
        return True

    def get_value(self):
        if self.cart.status == Cart.Status.ACTIVE:
            return sum(cart_item.item.actual_price * cart_item.quantity for cart_item in self.cart_items)
        else:
            return sum(cart_item.locked_price * cart_item.quantity for cart_item in self.cart_items)

    def clear_items(self):
        self.cart_items.delete()
