import sqlite3
from models.base import AutoParts


class SalesManager(AutoParts):
    """Manages sales operations"""

    def __init__(self, db_connection):
        super().__init__()
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
