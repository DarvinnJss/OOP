from models.base import AutoParts


class CartItem(AutoParts):
    """Represents an item in the shopping cart"""

    def __init__(self, product_id, name, price, quantity=1):
        super().__init__()
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def subtotal(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            'id': self.product_id,
            'name': self.name,
            'price': self.price,
            'qty': self.quantity,
            'subtotal': self.subtotal
        }


class ShoppingCart(AutoParts):
    """Manages shopping cart operations"""

    def __init__(self):
        super().__init__()
        self.items = []

    def add_item(self, product_id, product_name, price, quantity=1):
        """Add item to cart"""
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return

        new_item = CartItem(product_id, product_name, price, quantity)
        self.items.append(new_item)

    def remove_item(self, product_id):
        """Remove item from cart"""
        self.items = [
            item for item in self.items if item.product_id != product_id]

    def clear(self):
        """Clear all items from cart"""
        self.items = []

    @property
    def total(self):
        """Calculate total cart value"""
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)

    def to_legacy_format(self):
        """Convert to legacy format for existing code"""
        return [item.to_dict() for item in self.items]
