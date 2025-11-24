class InventoryManager:
    """Manages inventory operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_products(self):
        """Get all products from inventory"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM inventory")
            rows = cur.fetchall()
            products = []
            for row in rows:
                product = Product(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    stock=row[3],
                    category=row[4],
                    brand=row[6],
                    vehicle_model=row[7],
                    part_category=row[9],
                    part_subcategory=row[10],
                    year_range=row[8]
                )
                products.append(product)
            return products
        except sqlite3.Error as e:
            print(f"Error getting products: {e}")
            return []

    def search_products(self, search_term):
        """Search products by name"""
        try:
            cur = self.db.cursor()
            cur.execute("SELECT * FROM inventory WHERE name LIKE ?",
                        (f"%{search_term}%",))
            rows = cur.fetchall()
            products = []
            for row in rows:
                product = Product(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    stock=row[3],
                    category=row[4],
                    brand=row[6],
                    vehicle_model=row[7],
                    part_category=row[9],
                    part_subcategory=row[10],
                    year_range=row[8]
                )
                products.append(product)
            return products
        except sqlite3.Error as e:
            print(f"Error searching products: {e}")
            return []

    def update_product_stock(self, product_id, quantity_sold):
        """Update product stock after sale"""
        try:
            cur = self.db.cursor()
            cur.execute("UPDATE inventory SET stock = stock - ? WHERE id = ?",
                        (quantity_sold, product_id))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating stock: {e}")
            return False


class SalesManager:
    """Manages sales operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def record_sale(self, sale):
        """Record a sale in the database"""
        try:
            cur = self.db.cursor()
            for item in sale.items:
                cur.execute("""INSERT INTO sales 
                            (invoice, item, qty, subtotal, date, notes, customer_name, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (sale.invoice_number, item['item'], item['qty'], item['subtotal'],
                             sale.date, sale.notes, sale.customer_name, sale.status))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording sale: {e}")
            return False

    def get_sales_history(self, date_filter="", invoice_filter=""):
        """Get sales history with optional filters"""
        try:
            cur = self.db.cursor()
            query = "SELECT * FROM sales WHERE 1=1"
            params = []

            if date_filter:
                query += " AND date LIKE ?"
                params.append(f"{date_filter}%")

            if invoice_filter:
                query += " AND invoice LIKE ?"
                params.append(f"%{invoice_filter}%")

            query += " ORDER BY date DESC"
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting sales history: {e}")
            return []


class ShoppingCart:
    """Manages shopping cart operations"""

    def __init__(self):
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


class ReceiptManager:
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
