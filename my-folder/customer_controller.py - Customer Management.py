import sqlite3
from db import Database

class CustomerController:
    def __init__(self):
        self.db = Database()

    def get_customer_sales(self, customer_name):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM sales WHERE customer_name LIKE ? ORDER BY date DESC", 
                       (f"%{customer_name}%",))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting customer sales: {e}")
            return []

    def get_all_customers(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT customer_name FROM sales WHERE customer_name != ''")
            return [row[0] for row in cur.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting customers: {e}")
            return []