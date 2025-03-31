"""
CartItem.create(cart_id, item_id, quantity)
Cart.get_value() -> displays final price
request_discount() -> returns discount eligibility and discount value
Cart.apply_discount() -> ...
Order.create() -> Cart.

GET /cart                          returns CartValue, CartItems and their quantity
PUT /cart/items                    adds items into user cart
GET /cart/checkout/discount        checks if any discount is applicable for this upcoming order
PUT /cart/checkout/discount        applies the discount to the checked out cart and returns the Cart Items with updated prices plus discount status
"""
