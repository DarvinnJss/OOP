import sqlite3
from db import Database
from datetime import datetime, timedelta

class ReportController:
    def __init__(self):
        self.db = Database()

    def get_daily_sales_report(self, date=None):
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT invoice, customer_name, SUM(subtotal), date 
                FROM sales 
                WHERE date LIKE ? 
                GROUP BY invoice
            ''', (f"{date}%",))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting daily sales report: {e}")
            return []

    def get_inventory_report(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT category, COUNT(*), SUM(stock), 
                       SUM(price * stock) as total_value 
                FROM inventory 
                GROUP BY category
            ''')
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting inventory report: {e}")
            return []

    def get_low_stock_report(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory WHERE stock < 10")
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting low stock report: {e}")
            return []