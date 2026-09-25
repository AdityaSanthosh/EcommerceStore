from django.urls import path
from .views import (
    CartView,
    CartCheckoutView,
    CartValueView,
    OrderView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/checkout/", CartCheckoutView.as_view(), name="cart-checkout"),
    path("cart/value/", CartValueView.as_view(), name="cart-value"),
    path("order/", OrderView.as_view(), name="order"),
]
