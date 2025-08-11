from cart.models import Order, Payment


class OrderHandler:

    def __init__(self, order: Order):
        self.order = order

    def update_payment(self, payment_details: Payment):
        self.order.payment_details = payment_details
        self.order.save()
