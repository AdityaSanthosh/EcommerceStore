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

    def add_items(self, items: typing.List[typing.Dict[CartItemType]]):
        for item in items:
            try:
                # Cart might already have the item. If so, just increase the quantity by specified amount
                cart_item = CartItem.objects.get(cart=self.cart, item=item)
                cart_item.quantity += item.quantity
            except CartItem.DoesNotExist:
                cart_item = CartItem.objects.create(cart=self.cart, item=item, quantity=item.quantity)
                self.cart_items.add(cart_item)

    def get_value(self):
        if self.cart.status == Cart.Status.ACTIVE:
            return sum([cart_item.item.actual_price for cart_item in self.cart_items])
        else:
            return sum(cart_item.locked_price for cart_item in self.cart.added_items.all())

    def clear_items(self):
        self.cart_items.clear()