from models.base import AutoParts


class ReceiptManager(AutoParts):
    """Manages receipt generation and printing"""

    @staticmethod
    def generate_receipt_text(invoice_number, customer_name, notes, date, total_amount, cart_items):
        """Generate receipt as text string"""
        receipt = "=" * 50 + "\n"
        receipt += "         AUTO PARTS STORE\n"
        receipt += "       Official Sales Receipt\n"
        receipt += "   123 Main Street, City, Philippines\n"
        receipt += "          Tel: (02) 1234-5678\n"
        receipt += "=" * 50 + "\n\n"

        receipt += f"Invoice: {invoice_number}\n"
        receipt += f"Date: {date}\n"
        receipt += f"Customer: {customer_name}\n"
        if notes:
            receipt += f"Notes: {notes}\n"
        receipt += "\n" + "-" * 50 + "\n"
        receipt += "ITEM                            QTY   PRICE   SUBTOTAL\n"
        receipt += "-" * 50 + "\n"

        for item in cart_items:
            item_name = item['name']
            if len(item_name) > 30:
                item_name = item_name[:27] + "..."

            receipt += f"{item_name:<30} {item['qty']:>3}  ₱{item['price']:>6.2f}  ₱{item['subtotal']:>7.2f}\n"

        receipt += "-" * 50 + "\n"
        receipt += f"TOTAL: ₱{total_amount:>38.2f}\n"
        receipt += "=" * 50 + "\n\n"

        receipt += "RETURN POLICY:\n"
        receipt += "• Returns accepted within 7 days\n"
        receipt += "• Original receipt required\n"
        receipt += "• Items must be in original condition\n"
        receipt += "• No returns on installed parts\n\n"

        receipt += "Thank you for your business!\n"
        receipt += "Please keep this receipt for returns\n"
        receipt += "=" * 50 + "\n"

        return receipt
