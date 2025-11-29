from models import Sale
from utils import generate_invoice_number

class PaymentController:
    def __init__(self):
        pass

    def process_payment(self, cart_items, customer_name="", notes="", payment_method="CASH"):
        invoice_number = generate_invoice_number()
        sale = Sale(invoice_number, customer_name, notes)
        
        for item in cart_items:
            sale.add_item(item['name'], item['qty'], item['subtotal'])
        
        return sale

    def calculate_change(self, total_amount, amount_paid):
        if amount_paid < total_amount:
            return None  # Insufficient payment
        return amount_paid - total_amount