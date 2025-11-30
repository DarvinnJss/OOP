import sqlite3
from models.product import Product
from models.base import AutoParts


class InventoryManager(AutoParts):
    """Manages inventory operations"""

    def __init__(self, db_connection):
        super().__init__()
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

    def delete_product(self, product_id):
        """Delete a product from inventory"""
        try:
            cur = self.db.cursor()
            cur.execute("DELETE FROM inventory WHERE id = ?", (product_id,))
            self.db.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting product: {e}")
            return False
