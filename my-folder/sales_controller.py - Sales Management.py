import sqlite3
from db import Database
from models import Sale
from utils import generate_invoice_number

class SalesController:
    def __init__(self):
        self.db = Database()

    def record_sale(self, sale):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            for item in sale.items:
                cur.execute('''INSERT INTO sales 
                            (invoice, item, qty, subtotal, date, notes, customer_name, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (sale.invoice_number, item['item'], item['qty'], item['subtotal'],
                           sale.date, sale.notes, sale.customer_name, sale.status))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error recording sale: {e}")
            return False

    def get_sales_history(self, date_filter="", invoice_filter=""):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
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

    def clear_sales_history(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM sales")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='sales'")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing sales history: {e}")
            return False