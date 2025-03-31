from django.urls import path
from .views import (
    CartView,
    CartItemsView,
    CartCheckoutDiscountView,
    AdminDiscountCheck,
    AdminOrderAnalytics,
    CartCheckoutPaymentView,
)

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart-retrieve"),
    path("cart/items/", CartItemsView.as_view(), name="cart-update-items"),
    path(
        "cart/checkout/discount/",
        CartCheckoutDiscountView.as_view(),
        name="cart-checkout-discount",
    ),
    path(
        "cart/checkout/payment/",
        CartCheckoutPaymentView.as_view(),
        name="cart-checkout-payment",
    ),
    path(
        "Appadmin/check_discount/",
        AdminDiscountCheck.as_view(),
        name="admin-check-discount",
    ),
    path(
        "Appadmin/order_analytics/",
        AdminOrderAnalytics.as_view(),
        name="admin-order-analytics",
    ),
]
