from cart.models import Order


def generate_discount_code(value=0.1):
    return "Apply10", value


def is_discount_available():
    order_count = Order.objects.filter(status="paid").count()
    eligible = False
    details = {}
    if order_count % 10 == 0:  # Every 10th order in the system gets a discount
        eligible = True
        discount_code, discount_value = generate_discount_code()
        details = {"code": discount_code, "value": discount_value}
    return {"eligible": eligible, "details": details}
