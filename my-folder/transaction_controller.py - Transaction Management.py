import sqlite3
from db import Database

class TransactionController:
    def __init__(self):
        self.db = Database()

    def get_transactions_by_date(self, start_date, end_date):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT * FROM sales 
                WHERE date BETWEEN ? AND ? 
                ORDER BY date DESC
            ''', (start_date, end_date))
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting transactions: {e}")
            return []

    def get_transaction_summary(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT 
                    COUNT(DISTINCT invoice) as total_transactions,
                    SUM(subtotal) as total_revenue,
                    AVG(subtotal) as avg_sale
                FROM sales
            ''')
            return cur.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting transaction summary: {e}")
            return None