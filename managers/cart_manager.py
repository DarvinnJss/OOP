from models.cart import ShoppingCart
from models.base import AutoParts


class CartManager(AutoParts):
    """Manages cart operations"""

    def __init__(self):
        super().__init__()
        self.cart = ShoppingCart()

    def add_item(self, product_id, product_name, price, quantity=1):
        """Add item to cart"""
        self.cart.add_item(product_id, product_name, price, quantity)

    def remove_item(self, product_id):
        """Remove item from cart"""
        self.cart.remove_item(product_id)

    def clear_cart(self):
        """Clear all items from cart"""
        self.cart.clear()

    def get_cart_items(self):
        """Get cart items in legacy format"""
        return self.cart.to_legacy_format()

    def get_total(self):
        """Get cart total"""
        return self.cart.total

    def get_item_count(self):
        """Get total item count"""
        return self.cart.item_count
