import customtkinter as ctk
from payment_controller import PaymentController
from sales_controller import SalesController
from inventory_controller import InventoryController

class CheckInSystem:
    def __init__(self, parent):
        self.parent = parent
        self.payment_controller = PaymentController()
        self.sales_controller = SalesController()
        self.inventory_controller = InventoryController()
        self.cart = []

    def add_to_cart(self, product_id, product_name, price, quantity=1):
        for item in self.cart:
            if item['id'] == product_id:
                item['qty'] += quantity
                item['subtotal'] = item['price'] * item['qty']
                return

        self.cart.append({
            'id': product_id,
            'name': product_name,
            'price': price,
            'qty': quantity,
            'subtotal': price * quantity
        })

    def remove_from_cart(self, product_id):
        self.cart = [item for item in self.cart if item['id'] != product_id]

    def clear_cart(self):
        self.cart = []

    def get_cart_total(self):
        return sum(item['subtotal'] for item in self.cart)

    def process_checkout(self, customer_name="", notes=""):
        if not self.cart:
            return False, "Cart is empty"

        sale = self.payment_controller.process_payment(self.cart, customer_name, notes)
        success = self.sales_controller.record_sale(sale)
        
        if success:
            # Update inventory
            for item in self.cart:
                self.inventory_controller.update_product_stock(item['id'], item['qty'])
            self.clear_cart()
            return True, f"Sale completed! Invoice: {sale.invoice_number}"
        
        return False, "Failed to process sale"