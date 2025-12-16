from utils import *

# SHOPPING CART CLASS
# ============================================================================
class ShoppingCart(AutoParts):
    """Manages shopping cart operations"""
    
    def __init__(self):
        super().__init__()
        self.items = []
        self.total = 0
        self.item_count = 0
    
    def add_item(self, product_id, product_name, price, quantity=1):
        """Add item to cart"""
        for item in self.items:
            if item['id'] == product_id:
                item['qty'] += quantity
                item['subtotal'] = item['price'] * item['qty']
                self.update_totals()
                return
        new_item = {
            'id': product_id,
            'name': product_name,
            'price': price,
            'qty': quantity,
            'subtotal': price * quantity
        }
        self.items.append(new_item)
        self.update_totals()
    
    def remove_item(self, product_id):
        """Remove item from cart"""
        self.items = [item for item in self.items if item['id'] != product_id]
        self.update_totals()
    
    def clear(self):
        """Clear all items from cart"""
        self.items = []
        self.update_totals()
    
    def update_totals(self):
        """Update total cart values"""
        self.total = sum(item['subtotal'] for item in self.items)
        self.item_count = sum(item['qty'] for item in self.items)
# ============================================================================
