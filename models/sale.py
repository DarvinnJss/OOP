import datetime
from models.base import AutoParts


class Sale(AutoParts):
    """Represents a sales transaction"""

    def __init__(self, invoice_number="", customer_name="", notes="", status="COMPLETED"):
        super().__init__()
        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.notes = notes
        self.status = status
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items = []
        self.total_amount = 0.0

    def add_item(self, product_name, quantity, subtotal):
        """Add item to sale"""
        self.items.append({
            'item': product_name,
            'qty': quantity,
            'subtotal': subtotal
        })
        self.total_amount += subtotal

    def to_dict(self):
        """Convert sale to dictionary for database operations"""
        return {
            'invoice': self.invoice_number,
            'customer_name': self.customer_name,
            'notes': self.notes,
            'status': self.status,
            'date': self.date,
            'total_amount': self.total_amount,
            'items': self.items
        }
