from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model as djangoUser
from django.db.models import UniqueConstraint

from cart.services.cart_handler import CartHandler


class User(djangoUser):
    class Meta:
        proxy = True

    def save(self):
        super().save()
        User.create_cart(self.id)

    @property
    def cart(self):
        return Cart.objects.get_or_create(user_id=self.id, status=Cart.Status.ACTIVE)

class Item(models.Model):
    """
    Supports Dynamic Pricing (actual_price and discounted_price will vary with time). Historical prices can be stored
    elsewhere in another table
    """
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    actual_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))
    discounted_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))


class DiscountCodes(models.Model):
    code = models.CharField(max_length=10, null=False)
    perc = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))

    class Meta:
        constraints = [
            UniqueConstraint(fields=["code"], name="unique_discount_code_name")
        ]


class Cart(models.Model):
    """
    Cart will be cleared when it is checked out including all the CartItems
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        LOCKED = 'locked', 'Locked'
        ORDERED = 'ordered', 'Ordered'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='cart')
    status = models.CharField(choices=Status.choices, default=Status.ACTIVE)
    locked_at = models.DateTimeField(null=True)

    def value(self):
        return CartHandler(self).get_value()

    def clear(self):
        CartHandler(self).clear_items()

    def add(self, item):
        CartHandler(self).add_items([item])

class CartItem(models.Model):
    """
    To Store What Items are stored in a cart before the cart is checkout. Helps if the user closes the site and
    revisits the page after some time. The price will be fetched from the item itself (Dynamic Pricing).
    Cart Items will be deleted
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="added_items",
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    locked_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'), null=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["cart", "item"], name="unique_cart_item")
        ]


class Payment(models.Model):
    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("refunded", "Refunded")
    ]
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, db_index=True)
    external_payment_id = models.CharField(max_length=20, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))


class Order(models.Model):
    """
    Order is created when a cart is checkout.
    Details:
        PaymentDetails can be none to support free/no payment scenarios
    """
    ORDER_STATUS = [
        ("fulfilled", "Fulfilled"),
        ("payment_pending", "PaymentPending"),
        ("refunded", "Refunded"),
        ("paid", "Paid"),
    ]
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, db_index=True)
    payment_details = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)
    discount_code = models.CharField(max_length=10, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def items(self):
        return self.items


class OrderItem(models.Model):
    """
    To associate an order with its items and to store record of historical prices for an item.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.0'))
    quantity = models.IntegerField(default=0)
