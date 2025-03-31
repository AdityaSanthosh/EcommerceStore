import typing
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Item(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    actual_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discounted_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    actual_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discounted_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discount_code = models.CharField(max_length=10, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def value(self):
        return self.actual_price

    def apply_discount(self, code, value):
        if self.discounted_price < self.actual_price:
            return
        self.discounted_price = (1 - Decimal(value)) * self.value()
        self.discount_code = code
        self.discount_value = Decimal(value) * self.value()
        self.save()

    def add_items(self, item_ids: typing.List[int]):
        try:
            cart_items = [
                CartItem.objects.get_or_create(cart_id=self.id, item_id=item_id)[0]
                for item_id in item_ids
            ]
            self.added_items.set(cart_items)
            self.actual_price = sum(
                [cart_item.item.discounted_price for cart_item in cart_items]
            )
            if self.discounted_price < self.actual_price:
                self.discounted_price = self.actual_price
            self.save()
            return True
        except Exception:
            return False

    def clear(self):
        self.added_items.clear()
        self.discount_value = 0.0
        self.discount_code = ""
        self.discounted_price = 0.0
        self.actual_price = 0.0


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.get_or_create(user=instance)


class CartItem(models.Model):
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    discounted = models.BooleanField(default=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="added_items",
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["cart", "item"], name="unique_cart_item")
        ]


class Order(models.Model):
    ORDER_STATUS = [
        ("fulfilled", "Fulfilled"),
        ("pending", "Pending"),
        ("refunded", "Refunded"),
        ("paid", "Paid"),
    ]
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(choices=['fulfilled', 'pending', 'refunded'], db_index=True)
    final_price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, db_index=True)
    discount_code = models.CharField(max_length=10, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    actual_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    price_paid = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE)
