import sqlite3
from db import Database
from models import Product

class InventoryController:
    def __init__(self):
        self.db = Database()

    def get_all_products(self):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory")
            rows = cur.fetchall()
            products = []
            for row in rows:
                product = Product(
                    id=row[0], name=row[1], price=row[2], stock=row[3],
                    category=row[4], brand=row[6], vehicle_model=row[7],
                    part_category=row[9], part_subcategory=row[10], year_range=row[8]
                )
                products.append(product)
            return products
        except sqlite3.Error as e:
            print(f"Error getting products: {e}")
            return []

    def search_products(self, search_term):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory WHERE name LIKE ?", (f"%{search_term}%",))
            rows = cur.fetchall()
            products = []
            for row in rows:
                product = Product(
                    id=row[0], name=row[1], price=row[2], stock=row[3],
                    category=row[4], brand=row[6], vehicle_model=row[7],
                    part_category=row[9], part_subcategory=row[10], year_range=row[8]
                )
                products.append(product)
            return products
        except sqlite3.Error as e:
            print(f"Error searching products: {e}")
            return []

    def update_product_stock(self, product_id, quantity_sold):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE inventory SET stock = stock - ? WHERE id = ?",
                    (quantity_sold, product_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating stock: {e}")
            return False

    def delete_product(self, product_id):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM inventory WHERE id = ?", (product_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting product: {e}")
            return False

    def add_product(self, product_data):
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO inventory 
                (name, price, stock, category, brand, vehicle_model, 
                part_category, part_subcategory, year_range)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_data['name'],
                product_data['price'],
                product_data['stock'],
                product_data['category'],
                product_data['brand'],
                product_data['vehicle_model'],
                product_data['part_category'],
                product_data['part_subcategory'],
                product_data['year_range']
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding product: {e}")
            return False