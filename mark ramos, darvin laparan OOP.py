import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# ==================== NEW OOP CLASSES ====================


class Product:
    """Represents a product in the inventory"""

    def __init__(self, id=None, name="", price=0.0, stock=0, category="", brand="",
                 vehicle_model="", part_category="", part_subcategory="", year_range=""):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.brand = brand
        self.vehicle_model = vehicle_model
        self.part_category = part_category
        self.part_subcategory = part_subcategory
        self.year_range = year_range

    def to_dict(self):
        """Convert product to dictionary for database operations"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'brand': self.brand,
            'vehicle_model': self.vehicle_model,
            'part_category': self.part_category,
            'part_subcategory': self.part_subcategory,
            'year_range': self.year_range
        }

    @classmethod
    def from_dict(cls, data):
        """Create Product instance from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            vehicle_model=data.get('vehicle_model', ''),
            part_category=data.get('part_category', ''),
            part_subcategory=data.get('part_subcategory', ''),
            year_range=data.get('year_range', '')
        )


class CartItem:
    """Represents an item in the shopping cart"""

    def __init__(self, product_id, name, price, quantity=1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def subtotal(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            'id': self.product_id,
            'name': self.name,
            'price': self.price,
            'qty': self.quantity,
            'subtotal': self.subtotal
        }


class Sale:
    """Represents a sales transaction"""

    def __init__(self, invoice_number="", customer_name="", notes="", status="COMPLETED"):
        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.notes = notes
        self.status = status
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items = []
        self.total_amount = 0.0

    def add_item(self, product_name, quantity, subtotal):
        """Add item to sale"""
        self.items.append({
            'item': product_name,
            'qty': quantity,
            'subtotal': subtotal
        })
        self.total_amount += subtotal

    def to_dict(self):
        """Convert sale to dictionary for database operations"""
        return {
            'invoice': self.invoice_number,
            'customer_name': self.customer_name,
            'notes': self.notes,
            'status': self.status,
            'date': self.date,
            'total_amount': self.total_amount,
            'items': self.items
        }


class User:
    """Represents a system user"""

    def __init__(self, id=None, username="", password=""):
        self.id = id
        self.username = username
        self.password = password

    def authenticate(self, input_username, input_password):
        """Authenticate user credentials"""
        return self.username == input_username and self.password == input_password


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

# ==================== EXISTING CODE CONTINUES UNCHANGED ====================


APP_TITLE = "Auto Parts Admin System"
DB_FILE = "autoparts.db"
THEME_MODE = "dark"


def get_db():
    return sqlite3.connect(DB_FILE)


def apply_theme(window=None):
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme("blue")
    if window is not None:
        try:
            window.update()
        except tk.TclError:
            pass


def generate_invoice_number():
    return f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


def validate_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
            """
        )

        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory'"
        )
        inv_exists = cur.fetchone()

        if not inv_exists:
            cur.execute(
                """
                CREATE TABLE inventory(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL,
                    stock INTEGER,
                    category TEXT,
                    image TEXT,
                    brand TEXT,
                    vehicle_model TEXT,
                    model_group TEXT,
                    year_range TEXT,
                    part_category TEXT,
                    part_subcategory TEXT
                )
                """
            )
        else:
            cur.execute("PRAGMA table_info(inventory)")
            cols = {row[1] for row in cur.fetchall()}
            extra_cols = {
                "brand": "ALTER TABLE inventory ADD COLUMN brand TEXT",
                "vehicle_model": "ALTER TABLE inventory ADD COLUMN vehicle_model TEXT",
                "model_group": "ALTER TABLE inventory ADD COLUMN model_group TEXT",
                "year_range": "ALTER TABLE inventory ADD COLUMN year_range TEXT",
                "part_category": "ALTER TABLE inventory ADD COLUMN part_category TEXT",
                "part_subcategory": "ALTER TABLE inventory ADD COLUMN part_subcategory TEXT",
            }
            for col, sql in extra_cols.items():
                if col not in cols:
                    cur.execute(sql)

        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sales'"
        )
        sales_exists = cur.fetchone()

        if not sales_exists:
            cur.execute(
                """
                CREATE TABLE sales(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice TEXT,
                    item TEXT,
                    qty INTEGER,
                    subtotal REAL,
                    date TEXT,
                    notes TEXT,
                    customer_name TEXT,
                    status TEXT
                )
                """
            )
        else:
            cur.execute("PRAGMA table_info(sales)")
            cols = {row[1] for row in cur.fetchall()}
            if "notes" not in cols:
                cur.execute("ALTER TABLE sales ADD COLUMN notes TEXT")
            if "customer_name" not in cols:
                cur.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT")
            if "status" not in cols:
                cur.execute("ALTER TABLE sales ADD COLUMN status TEXT")
            cur.execute(
                "UPDATE sales SET status='COMPLETED' WHERE status IS NULL OR status=''"
            )

        default_username = "autoparts"
        default_password = "oilengine"
        cur.execute(
            """
            INSERT OR REPLACE INTO users(id, username, password)
            VALUES(1, ?, ?)
            """,
            (default_username, default_password),
        )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        messagebox.showerror(
            "Database Error", f"Database initialization failed: {str(e)}")

# ==================== COMPLETE PRODUCT CATALOGS ====================


TOYOTA_PARTS_CATALOG = {
    "vios": {
        "engine_parts": {
            "engine_oil": {
                "Toyota Genuine Engine Oil 5W-30 (1L)": {"price": 450.00, "models": "All Vios 2003-2023", "years": "2003-2023"},
                "Toyota Genuine Engine Oil 10W-30 (1L)": {"price": 420.00, "models": "All Vios 2003-2023", "years": "2003-2023"},
                "Fully Synthetic 5W-30 (1L)": {"price": 650.00, "models": "Vios 2014-2023", "years": "2014-2023"},
            },
            "filters": {
                "Oil Filter 90915-YZZE1": {"price": 380.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Oil Filter 90915-YZZE2": {"price": 420.00, "models": "Vios 2008-2023", "years": "2008-2023"},
                "Air Filter 17801-0H010": {"price": 850.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Air Filter 17801-0H020": {"price": 920.00, "models": "Vios 2008-2013", "years": "2008-2013"},
                "Fuel Filter 23300-15030": {"price": 1250.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Cabin Air Filter 87139-0H010": {"price": 680.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            },
            "spark_plugs": {
                "Denso Standard K20HR-U11": {"price": 280.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "NGK Iridium BKR6EIX-11": {"price": 650.00, "models": "Vios 2008-2023", "years": "2008-2023"},
                "Denso Iridium Power IK20": {"price": 580.00, "models": "All Vios", "years": "2003-2023"},
            },
            "cooling_system": {
                "Radiator 16400-0H010": {"price": 4800.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Radiator 16400-0H020": {"price": 5200.00, "models": "Vios 2008-2023", "years": "2008-2023"},
                "Thermostat 90916-03100": {"price": 850.00, "models": "All Vios", "years": "2003-2023"},
                "Water Pump 16100-0H010": {"price": 3200.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Coolant 1L": {"price": 350.00, "models": "All Vios", "years": "2003-2023"},
            },
            "ignition_system": {
                "Ignition Coil 90919-02239": {"price": 1850.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Ignition Coil 90919-02240": {"price": 2200.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            }
        },
        "brake_system": {
            "brake_pads": {
                "Front Brake Pads 04465-0H010": {"price": 1850.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Rear Brake Pads 04466-0H010": {"price": 1650.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Front Ceramic Brake Pads": {"price": 2800.00, "models": "Vios 2008-2023", "years": "2008-2023"},
                "Rear Ceramic Brake Pads": {"price": 2200.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            },
            "brake_discs": {
                "Front Brake Disc 43512-0H010": {"price": 3200.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Rear Brake Disc 42431-0H010": {"price": 2800.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Front Vented Brake Disc": {"price": 4500.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            },
            "brake_fluid": {
                "DOT 3 Brake Fluid 500ml": {"price": 450.00, "models": "All Vios", "years": "2003-2023"},
                "DOT 4 Brake Fluid 500ml": {"price": 550.00, "models": "Vios 2014-2023", "years": "2014-2023"},
            }
        },
        "suspension_steering": {
            "shock_absorbers": {
                "Front Shock Absorber 48510-0H010": {"price": 3200.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Rear Shock Absorber 48530-0H010": {"price": 2800.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Gas Shock Absorbers Set": {"price": 8500.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            },
            "tie_rods": {
                "Inner Tie Rod End 45503-0H010": {"price": 1200.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Outer Tie Rod End 45504-0H010": {"price": 950.00, "models": "Vios 2003-2007", "years": "2003-2007"},
            }
        },
        "electrical_system": {
            "battery": {
                "Maintenance-Free Battery 55D23L": {"price": 4800.00, "models": "Vios 2003-2013", "years": "2003-2013"},
                "Maintenance-Free Battery NS60": {"price": 5200.00, "models": "Vios 2014-2023", "years": "2014-2023"},
            },
            "alternator": {
                "Alternator 27060-0H010": {"price": 8500.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Alternator 27060-0H020": {"price": 9800.00, "models": "Vios 2008-2023", "years": "2008-2023"},
            }
        },
        "transmission": {
            "automatic_transmission": {
                "ATF WS Fluid 1L": {"price": 650.00, "models": "Vios 2008-2023", "years": "2008-2023"},
                "Transmission Filter Kit": {"price": 1850.00, "models": "All Vios AT", "years": "2003-2023"},
            },
            "manual_transmission": {
                "Gear Oil 75W-90 1L": {"price": 550.00, "models": "All Vios MT", "years": "2003-2023"},
                "Clutch Kit 31250-0H010": {"price": 6800.00, "models": "Vios 2003-2007", "years": "2003-2007"},
            }
        },
        "wheels_tires": {
            "tires": {
                "Bridgestone Ecopia EP150 175/65R14": {"price": 2200.00, "models": "Vios Base 2003-2023", "years": "2003-2023"},
                "Michelin Energy XM2 185/60R15": {"price": 3200.00, "models": "Vios G 2003-2023", "years": "2003-2023"},
                "Yokohama BluEarth 195/55R16": {"price": 3800.00, "models": "Vios Sportivo 2008-2013", "years": "2008-2013"},
            },
            "wheels": {
                "14-inch Steel Wheel": {"price": 1800.00, "models": "Vios Base", "years": "2003-2023"},
                "15-inch Alloy Wheel": {"price": 4500.00, "models": "Vios G", "years": "2003-2023"},
                "16-inch Sport Alloy": {"price": 6800.00, "models": "Vios Sportivo", "years": "2008-2013"},
            }
        },
        "body_parts": {
            "headlights": {
                "Headlight Assembly LH 81110-0H010": {"price": 8500.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Headlight Assembly RH 81150-0H010": {"price": 8500.00, "models": "Vios 2003-2007", "years": "2003-2007"},
            },
            "bumpers": {
                "Front Bumper 52111-0H010": {"price": 6800.00, "models": "Vios 2003-2007", "years": "2003-2007"},
                "Rear Bumper 52171-0H010": {"price": 6200.00, "models": "Vios 2003-2007", "years": "2003-2007"},
            }
        }
    }
}

HONDA_PARTS_CATALOG = {
    "civic": {
        "engine_parts": {
            "engine_oil": {
                "Honda Genuine Oil 0W-20 (1L)": {"price": 520.00, "models": "Civic 1.5T 2016+", "years": "2016-present"},
                "Honda Genuine Oil 5W-30 (1L)": {"price": 480.00, "models": "Civic 2.0L 2016+", "years": "2016-present"},
            },
            "filters": {
                "Oil Filter 15400-PLM-A02": {"price": 420.00, "models": "Civic 2016+", "years": "2016-present"},
                "Air Filter 17220-5BA-A00": {"price": 1250.00, "models": "Civic 2016-2021", "years": "2016-2021"},
            }
        }
    }
}

MITSUBISHI_PARTS_CATALOG = {
    "mirage": {
        "engine_parts": {
            "engine_oil": {
                "Mitsubishi Genuine Oil 5W-30 (1L)": {"price": 420.00, "models": "Mirage 1.2L 2012+", "years": "2012-present"},
            },
            "filters": {
                "Oil Filter MD360478": {"price": 320.00, "models": "Mirage 2012+", "years": "2012-present"},
                "Air Filter MN167205": {"price": 780.00, "models": "Mirage 2012-2017", "years": "2012-2017"},
            }
        }
    }
}

FORD_PARTS_CATALOG = {
    "ranger": {
        "engine_parts": {
            "engine_oil": {
                "Ford Genuine Oil 5W-30 (1L)": {"price": 550.00, "models": "Ranger 2.0L EcoBlue", "years": "2019-present"},
            },
            "filters": {
                "Oil Filter LB7Z-6731-BA": {"price": 650.00, "models": "Ranger 2.0L EcoBlue", "years": "2019-present"},
            }
        }
    }
}

NISSAN_PARTS_CATALOG = {
    "navara": {
        "engine_parts": {
            "engine_oil": {
                "Nissan Genuine Oil 5W-30 (1L)": {"price": 520.00, "models": "Navara 2.5L YD25", "years": "2015-present"},
            },
            "filters": {
                "Oil Filter 15208-9L20A": {"price": 580.00, "models": "Navara 2.5L YD25", "years": "2015-present"},
            }
        }
    }
}

HYUNDAI_PARTS_CATALOG = {
    "accent": {
        "engine_parts": {
            "engine_oil": {
                "Hyundai Genuine Oil 5W-30 (1L)": {"price": 450.00, "models": "Accent 1.4L 2011+", "years": "2011-present"},
            },
            "filters": {
                "Oil Filter 26300-35503": {"price": 320.00, "models": "Accent 2011+", "years": "2011-present"},
            }
        }
    }
}

# ==================== CATALOG POPULATION FUNCTIONS ====================


def add_all_toyota_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in TOYOTA_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Toyota Parts",
                                "Toyota",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Toyota parts: {e}")
        return False


def add_all_honda_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in HONDA_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Honda Parts",
                                "Honda",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Honda parts: {e}")
        return False


def add_all_mitsubishi_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in MITSUBISHI_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Mitsubishi Parts",
                                "Mitsubishi",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Mitsubishi parts: {e}")
        return False


def add_all_ford_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in FORD_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Ford Parts",
                                "Ford",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Ford parts: {e}")
        return False


def add_all_nissan_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in NISSAN_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Nissan Parts",
                                "Nissan",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Nissan parts: {e}")
        return False


def add_all_hyundai_parts_to_inventory():
    try:
        conn = get_db()
        cur = conn.cursor()

        for model, categories in HYUNDAI_PARTS_CATALOG.items():
            for category, subcategories in categories.items():
                for subcategory, parts in subcategories.items():
                    for part_name, part_info in parts.items():
                        cur.execute(
                            "SELECT id FROM inventory WHERE name = ?", (part_name,))
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO inventory 
                                (name, price, stock, category, brand, vehicle_model, 
                                 part_category, part_subcategory, year_range)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                part_name,
                                part_info['price'],
                                50,
                                "Hyundai Parts",
                                "Hyundai",
                                model,
                                category,
                                subcategory,
                                part_info['years']
                            ))

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Error adding Hyundai parts: {e}")
        return False

# ==================== ENHANCED MAIN CLASS ====================


class AutoPartsAdminSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry("1200x800")
        apply_theme(self.root)

        init_db()

        self.current_user = None
        # Using new OOP classes while maintaining backward compatibility
        self.cart = []  # Legacy cart (will be synchronized with new OOP cart)
        self.oop_cart = ShoppingCart()  # New OOP cart
        self.inventory_manager = InventoryManager(get_db())
        self.sales_manager = SalesManager(get_db())
        self.receipt_manager = ReceiptManager()

        self.setup_gui()

    def setup_gui(self):
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_login_screen()

    def show_login_screen(self):
        self.clear_screen()

        login_frame = ctk.CTkFrame(self.main_container)
        login_frame.pack(expand=True, fill="both", padx=200, pady=100)

        title_label = ctk.CTkLabel(login_frame, text="Auto Parts Admin System",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=40)

        ctk.CTkLabel(login_frame, text="Username:",
                     font=ctk.CTkFont(size=14)).pack(pady=5)
        self.username_entry = ctk.CTkEntry(login_frame, width=200)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "autoparts")

        ctk.CTkLabel(login_frame, text="Password:",
                     font=ctk.CTkFont(size=14)).pack(pady=5)
        self.password_entry = ctk.CTkEntry(login_frame, width=200, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "oilengine")

        login_btn = ctk.CTkButton(login_frame, text="Login", command=self.login,
                                  font=ctk.CTkFont(size=14))
        login_btn.pack(pady=20)

        populate_btn = ctk.CTkButton(login_frame, text="Populate Sample Data",
                                     command=self.populate_sample_data,
                                     font=ctk.CTkFont(size=12))
        populate_btn.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                        (username, password))
            user = cur.fetchone()
            conn.close()

            if user:
                self.current_user = user
                self.show_main_dashboard()
            else:
                messagebox.showerror(
                    "Login Failed", "Invalid username or password")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")

    def show_main_dashboard(self):
        self.clear_screen()

        self.create_sidebar()

        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both",
                                expand=True, padx=10, pady=10)

        self.show_dashboard()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self.main_container, width=200)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)
        sidebar.pack_propagate(False)

        welcome_label = ctk.CTkLabel(sidebar, text=f"Welcome, {self.current_user[1]}",
                                     font=ctk.CTkFont(size=16, weight="bold"))
        welcome_label.pack(pady=20)

        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📦 Inventory", self.show_inventory),
            ("🛒 Point of Sale", self.show_pos),
            ("💰 Sales History", self.show_sales_history),
            ("🚗 Parts Catalog", self.show_parts_catalog),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Logout", self.logout)
        ]

        for text, command in nav_buttons:
            btn = ctk.CTkButton(sidebar, text=text, command=command,
                                font=ctk.CTkFont(size=14), anchor="w")
            btn.pack(fill="x", padx=10, pady=5)

    def show_dashboard(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Dashboard",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Using OOP classes to get data
        try:
            conn = get_db()
            inventory_manager = InventoryManager(conn)
            sales_manager = SalesManager(conn)

            products = inventory_manager.get_all_products()
            total_products = len(products)
            low_stock = len([p for p in products if p.stock < 10])

            today = datetime.datetime.now().strftime('%Y-%m-%d')
            today_sales = sales_manager.get_sales_history(today)
            today_sales_count = len(today_sales)
            # subtotal is index 4
            today_sales_total = sum(sale[4] for sale in today_sales)

            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Could not load dashboard data: {str(e)}")
            return

        metrics_frame = ctk.CTkFrame(self.content_frame)
        metrics_frame.pack(fill="x", padx=20, pady=20)

        metrics_data = [
            ("Total Products", total_products, "blue"),
            ("Low Stock Items", low_stock, "red"),
            ("Today's Sales", today_sales_count, "green"),
            ("Today's Revenue", f"₱{today_sales_total:,.2f}", "purple")
        ]

        for i, (label, value, color) in enumerate(metrics_data):
            metric_frame = ctk.CTkFrame(metrics_frame)
            metric_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(metric_frame, text=label,
                         font=ctk.CTkFont(size=14)).pack(pady=5)
            ctk.CTkLabel(metric_frame, text=str(value),
                         font=ctk.CTkFont(size=18, weight="bold"),
                         text_color=color).pack(pady=5)

        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Quick actions
        actions_frame = ctk.CTkFrame(self.content_frame)
        actions_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(actions_frame, text="Quick Actions",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        action_buttons = [
            ("Add New Product", self.show_add_product),
            ("Process Sale", self.show_pos),
            ("View Inventory", self.show_inventory),
            ("Generate Report", self.generate_report)
        ]

        for text, command in action_buttons:
            btn = ctk.CTkButton(actions_frame, text=text, command=command)
            btn.pack(pady=5, padx=50, fill="x")

    def show_inventory(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Inventory Management",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        search_frame = ctk.CTkFrame(self.content_frame)
        search_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(search_frame, text="Search:").grid(
            row=0, column=0, padx=5, pady=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=200)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        search_btn = ctk.CTkButton(
            search_frame, text="Search", command=self.search_inventory)
        search_btn.grid(row=0, column=2, padx=5, pady=5)

        refresh_btn = ctk.CTkButton(
            search_frame, text="Refresh", command=self.load_inventory)
        refresh_btn.grid(row=0, column=3, padx=5, pady=5)

        add_btn = ctk.CTkButton(
            search_frame, text="Add New Product", command=self.show_add_product)
        add_btn.grid(row=0, column=4, padx=5, pady=5)

        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Price", "Stock", "Category", "Brand")
        self.inventory_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        self.inventory_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_inventory()

        self.inventory_tree.bind("<Double-1>", self.edit_inventory_item)

    def load_inventory(self):
        try:
            # Using OOP InventoryManager
            inventory_manager = InventoryManager(get_db())
            products = inventory_manager.get_all_products()

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            for product in products:
                self.inventory_tree.insert("", "end", values=(
                    product.id, product.name, product.price,
                    product.stock, product.category, product.brand
                ))

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Could not load inventory: {str(e)}")

    def search_inventory(self):
        search_term = self.search_entry.get()

        try:
            # Using OOP InventoryManager
            inventory_manager = InventoryManager(get_db())
            products = inventory_manager.search_products(search_term)

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            for product in products:
                self.inventory_tree.insert("", "end", values=(
                    product.id, product.name, product.price,
                    product.stock, product.category, product.brand
                ))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def show_add_product(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add New Product", font=ctk.CTkFont(
            size=18, weight="bold")).pack(pady=10)

        fields = [
            ("Name", "entry"),
            ("Price", "entry"),
            ("Stock", "entry"),
            ("Category", "entry"),
            ("Brand", "entry"),
            ("Vehicle Model", "entry"),
            ("Year Range", "entry")
        ]

        entries = {}

        for field, field_type in fields:
            ctk.CTkLabel(dialog, text=field).pack(pady=5)
            if field_type == "entry":
                entry = ctk.CTkEntry(dialog, width=300)
                entry.pack(pady=5)
                entries[field] = entry

        def save_product():
            try:
                # Using OOP approach
                new_product = Product(
                    name=entries["Name"].get(),
                    price=float(entries["Price"].get()),
                    stock=int(entries["Stock"].get()),
                    category=entries["Category"].get(),
                    brand=entries["Brand"].get(),
                    vehicle_model=entries["Vehicle Model"].get(),
                    year_range=entries["Year Range"].get()
                )

                conn = get_db()
                cur = conn.cursor()
                cur.execute("""INSERT INTO inventory 
                            (name, price, stock, category, brand, vehicle_model, year_range) 
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (
                                new_product.name,
                                new_product.price,
                                new_product.stock,
                                new_product.category,
                                new_product.brand,
                                new_product.vehicle_model,
                                new_product.year_range
                            ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Product added successfully!")
                dialog.destroy()
                self.load_inventory()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Could not add product: {str(e)}")

        ctk.CTkButton(dialog, text="Save Product",
                      command=save_product).pack(pady=20)

    def edit_inventory_item(self, event):
        selection = self.inventory_tree.selection()
        if not selection:
            return

        item = self.inventory_tree.item(selection[0])
        item_data = item['values']

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Edit Product", font=ctk.CTkFont(
            size=18, weight="bold")).pack(pady=10)

        fields = ["Name", "Price", "Stock", "Category",
                  "Brand", "Vehicle Model", "Year Range"]
        entries = {}

        for i, field in enumerate(fields):
            ctk.CTkLabel(dialog, text=field).pack(pady=5)
            entry = ctk.CTkEntry(dialog, width=300)
            if i < len(item_data) - 1:
                entry.insert(0, str(item_data[i+1]))
            entry.pack(pady=5)
            entries[field] = entry

        def update_product():
            try:
                conn = get_db()
                cur = conn.cursor()

                cur.execute("""UPDATE inventory 
                            SET name=?, price=?, stock=?, category=?, brand=?, vehicle_model=?, year_range=?
                            WHERE id=?""",
                            (
                                entries["Name"].get(),
                                float(entries["Price"].get()),
                                int(entries["Stock"].get()),
                                entries["Category"].get(),
                                entries["Brand"].get(),
                                entries["Vehicle Model"].get(),
                                entries["Year Range"].get(),
                                item_data[0]
                            ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Product updated successfully!")
                dialog.destroy()
                self.load_inventory()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Could not update product: {str(e)}")

        ctk.CTkButton(dialog, text="Update Product",
                      command=update_product).pack(pady=20)

    def show_pos(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Point of Sale",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        pos_frame = ctk.CTkFrame(self.content_frame)
        pos_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = ctk.CTkFrame(pos_frame)
        left_frame.pack(side="left", fill="both",
                        expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Products", font=ctk.CTkFont(
            size=16, weight="bold")).pack(pady=10)

        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.pos_search_entry = ctk.CTkEntry(search_frame, width=200)
        self.pos_search_entry.pack(side="left", padx=5)
        self.pos_search_entry.bind("<KeyRelease>", self.search_products_pos)

        self.pos_products_tree = ttk.Treeview(left_frame, columns=("ID", "Name", "Price", "Stock"),
                                              show="headings", height=15)
        for col in ["ID", "Name", "Price", "Stock"]:
            self.pos_products_tree.heading(col, text=col)
            self.pos_products_tree.column(col, width=100)

        self.pos_products_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.pos_products_tree.bind("<Double-1>", self.add_to_cart)

        right_frame = ctk.CTkFrame(pos_frame)
        right_frame.pack(side="right", fill="both", padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Shopping Cart",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.cart_tree = ttk.Treeview(right_frame, columns=("Product", "Qty", "Price", "Subtotal"),
                                      show="headings", height=10)
        for col in ["Product", "Qty", "Price", "Subtotal"]:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)

        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=10)

        cart_actions = ctk.CTkFrame(right_frame)
        cart_actions.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(cart_actions, text="Remove Item",
                      command=self.remove_from_cart).pack(side="left", padx=5)
        ctk.CTkButton(cart_actions, text="Clear Cart",
                      command=self.clear_cart).pack(side="left", padx=5)

        info_frame = ctk.CTkFrame(right_frame)
        info_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(info_frame, text="Customer Name:").pack(pady=5)
        self.customer_entry = ctk.CTkEntry(info_frame)
        self.customer_entry.pack(pady=5)

        ctk.CTkLabel(info_frame, text="Notes:").pack(pady=5)
        self.notes_entry = ctk.CTkEntry(info_frame)
        self.notes_entry.pack(pady=5)

        self.total_label = ctk.CTkLabel(info_frame, text="Total: ₱0.00",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.total_label.pack(pady=10)

        ctk.CTkButton(right_frame, text="Process Sale", command=self.process_sale,
                      font=ctk.CTkFont(size=14)).pack(pady=10)

        self.cart = []
        self.oop_cart.clear()
        self.load_products_pos()

    def load_products_pos(self):
        try:
            # Using OOP InventoryManager
            inventory_manager = InventoryManager(get_db())
            products = inventory_manager.get_all_products()

            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)

            for product in products:
                if product.stock > 0:  # Only show products with stock
                    self.pos_products_tree.insert("", "end", values=(
                        product.id, product.name, product.price, product.stock
                    ))

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Could not load products: {str(e)}")

    def search_products_pos(self, event=None):
        search_term = self.pos_search_entry.get()

        try:
            # Using OOP InventoryManager
            inventory_manager = InventoryManager(get_db())
            products = inventory_manager.search_products(search_term)

            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)

            for product in products:
                if product.stock > 0:  # Only show products with stock
                    self.pos_products_tree.insert("", "end", values=(
                        product.id, product.name, product.price, product.stock
                    ))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def add_to_cart(self, event):
        selection = self.pos_products_tree.selection()
        if not selection:
            return

        item = self.pos_products_tree.item(selection[0])
        product_data = item['values']

        # Using OOP cart
        self.oop_cart.add_item(
            product_data[0], product_data[1], float(product_data[2]), 1)

        # Synchronize with legacy cart
        self.cart = self.oop_cart.to_legacy_format()

        self.update_cart_display()

    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            return

        item_index = self.cart_tree.index(selection[0])
        if 0 <= item_index < len(self.cart):
            # Remove from both carts
            product_id = self.cart[item_index]['id']
            self.oop_cart.remove_item(product_id)
            self.cart = self.oop_cart.to_legacy_format()
            self.update_cart_display()

    def clear_cart(self):
        self.cart = []
        self.oop_cart.clear()
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0
        for i, item in enumerate(self.cart):
            self.cart_tree.insert("", "end", values=(
                item['name'], item['qty'], f"₱{item['price']:.2f}", f"₱{item['subtotal']:.2f}"
            ))
            total += item['subtotal']

        self.total_label.configure(text=f"Total: ₱{total:.2f}")

    def process_sale(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        try:
            conn = get_db()

            # Using OOP classes
            invoice_number = generate_invoice_number()
            customer_name = self.customer_entry.get() or "Walk-in Customer"
            notes = self.notes_entry.get()

            # Create Sale object
            sale = Sale(invoice_number, customer_name, notes)

            # Add items to sale
            for cart_item in self.cart:
                sale.add_item(cart_item['name'],
                              cart_item['qty'], cart_item['subtotal'])

                # Update inventory using InventoryManager
                inventory_manager = InventoryManager(conn)
                inventory_manager.update_product_stock(
                    cart_item['id'], cart_item['qty'])

            # Record sale using SalesManager
            sales_manager = SalesManager(conn)
            sales_manager.record_sale(sale)

            conn.close()

            # Generate and show receipt
            self.generate_receipt(
                invoice_number, customer_name, notes, sale.date, sale.total_amount)

            messagebox.showinfo("Sale Completed",
                                f"Sale processed successfully!\nInvoice: {invoice_number}\nTotal: ₱{sale.total_amount:.2f}")

            # Clear both carts
            self.clear_cart()
            self.customer_entry.delete(0, 'end')
            self.notes_entry.delete(0, 'end')
            self.load_products_pos()

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Could not process sale: {str(e)}")

    def generate_receipt(self, invoice_number, customer_name, notes, date, total_amount):
        """Generate and display a receipt for the sale"""
        receipt_window = ctk.CTkToplevel(self.root)
        receipt_window.title("Sales Receipt")
        receipt_window.geometry("600x900")
        receipt_window.transient(self.root)
        receipt_window.grab_set()

        # Create receipt frame
        receipt_frame = ctk.CTkFrame(receipt_window)
        receipt_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Receipt header
        header_frame = ctk.CTkFrame(receipt_frame)
        header_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header_frame, text="AUTO PARTS STORE",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=5)
        ctk.CTkLabel(header_frame, text="Official Sales Receipt",
                     font=ctk.CTkFont(size=16)).pack(pady=2)
        ctk.CTkLabel(header_frame, text="123 Main Street, City, Philippines",
                     font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(header_frame, text="Tel: (02) 1234-5678",
                     font=ctk.CTkFont(size=12)).pack(pady=2)

        # Separator
        separator = ctk.CTkFrame(header_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=10)

        # Receipt details
        details_frame = ctk.CTkFrame(receipt_frame)
        details_frame.pack(fill="x", padx=10, pady=5)

        # Invoice and date
        ctk.CTkLabel(details_frame, text=f"Invoice: {invoice_number}",
                     font=ctk.CTkFont(size=12, weight="bold"), justify="left").pack(anchor="w")
        ctk.CTkLabel(details_frame, text=f"Date: {date}",
                     font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")
        ctk.CTkLabel(details_frame, text=f"Customer: {customer_name}",
                     font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")

        if notes:
            ctk.CTkLabel(details_frame, text=f"Notes: {notes}",
                         font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")

        # Items table
        items_frame = ctk.CTkFrame(receipt_frame)
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create table header
        header_frame = ctk.CTkFrame(items_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="Item", width=200,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Qty", width=60,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Price", width=80,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Subtotal", width=100,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)

        # Add items to receipt
        for item in self.cart:
            item_frame = ctk.CTkFrame(items_frame)
            item_frame.pack(fill="x", pady=2)

            # Item name (truncate if too long)
            item_name = item['name']
            if len(item_name) > 25:
                item_name = item_name[:22] + "..."

            ctk.CTkLabel(item_frame, text=item_name, width=200,
                         justify="left").pack(side="left", padx=2)
            ctk.CTkLabel(item_frame, text=str(
                item['qty']), width=60).pack(side="left", padx=2)
            ctk.CTkLabel(item_frame, text=f"₱{item['price']:.2f}", width=80).pack(
                side="left", padx=2)
            ctk.CTkLabel(item_frame, text=f"₱{item['subtotal']:.2f}", width=100).pack(
                side="left", padx=2)

        # Total section
        total_frame = ctk.CTkFrame(receipt_frame)
        total_frame.pack(fill="x", padx=10, pady=10)

        separator = ctk.CTkFrame(total_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=5)

        ctk.CTkLabel(total_frame, text=f"TOTAL: ₱{total_amount:.2f}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Return policy
        policy_frame = ctk.CTkFrame(receipt_frame)
        policy_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(policy_frame, text="RETURN POLICY:",
                     font=ctk.CTkFont(weight="bold")).pack(pady=2)
        ctk.CTkLabel(policy_frame, text="• Returns accepted within 7 days",
                     font=ctk.CTkFont(size=10)).pack(anchor="w")
        ctk.CTkLabel(policy_frame, text="• Original receipt required",
                     font=ctk.CTkFont(size=10)).pack(anchor="w")
        ctk.CTkLabel(policy_frame, text="• Items must be in original condition",
                     font=ctk.CTkFont(size=10)).pack(anchor="w")
        ctk.CTkLabel(policy_frame, text="• No returns on installed parts",
                     font=ctk.CTkFont(size=10)).pack(anchor="w")

        # Footer
        footer_frame = ctk.CTkFrame(receipt_frame)
        footer_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(footer_frame, text="Thank you for your business!",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(footer_frame, text="Please keep this receipt for returns",
                     font=ctk.CTkFont(size=10)).pack(pady=2)

        # Action buttons
        button_frame = ctk.CTkFrame(receipt_window)
        button_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(button_frame, text="Print Receipt",
                      command=lambda: self.print_receipt(invoice_number, customer_name, notes, date, total_amount)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Save as Text",
                      command=lambda: self.save_receipt_as_text(invoice_number, customer_name, notes, date, total_amount)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close",
                      command=receipt_window.destroy).pack(side="right", padx=5)

    def print_receipt(self, invoice_number, customer_name, notes, date, total_amount):
        """Simple print functionality - saves as text file that can be printed"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"receipt_{invoice_number}.txt"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.generate_receipt_text(invoice_number,
                            customer_name, notes, date, total_amount))

                messagebox.showinfo(
                    "Success", f"Receipt saved as: {filename}\nYou can print this file.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save receipt: {str(e)}")

    def save_receipt_as_text(self, invoice_number, customer_name, notes, date, total_amount):
        """Save receipt as text file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"receipt_{invoice_number}.txt"
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.generate_receipt_text(invoice_number,
                            customer_name, notes, date, total_amount))

                messagebox.showinfo("Success", f"Receipt saved as: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save receipt: {str(e)}")

    def generate_receipt_text(self, invoice_number, customer_name, notes, date, total_amount):
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

        for item in self.cart:
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

    def show_sales_history(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Sales History",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        filter_frame = ctk.CTkFrame(self.content_frame)
        filter_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(filter_frame, text="Date:").grid(
            row=0, column=0, padx=5, pady=5)
        self.sales_date_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="YYYY-MM-DD")
        self.sales_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(filter_frame, text="Invoice:").grid(
            row=0, column=2, padx=5, pady=5)
        self.invoice_entry = ctk.CTkEntry(filter_frame)
        self.invoice_entry.grid(row=0, column=3, padx=5, pady=5)

        search_btn = ctk.CTkButton(
            filter_frame, text="Search", command=self.search_sales)
        search_btn.grid(row=0, column=4, padx=5, pady=5)

        refresh_btn = ctk.CTkButton(
            filter_frame, text="Refresh", command=self.load_sales_history)
        refresh_btn.grid(row=0, column=5, padx=5, pady=5)

        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Invoice", "Item", "Qty",
                   "Subtotal", "Date", "Customer", "Status")
        self.sales_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        self.sales_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_sales_history()

    def load_sales_history(self):
        try:
            # Using OOP SalesManager
            sales_manager = SalesManager(get_db())
            sales = sales_manager.get_sales_history()

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            for sale in sales:
                self.sales_tree.insert("", "end", values=sale)

        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Could not load sales history: {str(e)}")

    def search_sales(self):
        date = self.sales_date_entry.get()
        invoice = self.invoice_entry.get()

        try:
            # Using OOP SalesManager
            sales_manager = SalesManager(get_db())
            sales = sales_manager.get_sales_history(date, invoice)

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            for sale in sales:
                self.sales_tree.insert("", "end", values=sale)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def show_parts_catalog(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Parts Catalog",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        brand_frame = ctk.CTkFrame(self.content_frame)
        brand_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(brand_frame, text="Select Brand:").pack(
            side="left", padx=5)

        brands = ["Toyota", "Honda", "Mitsubishi", "Ford", "Nissan", "Hyundai"]

        self.brand_var = ctk.StringVar(value="Toyota")
        brand_combo = ctk.CTkComboBox(brand_frame, values=brands, variable=self.brand_var,
                                      command=self.load_brand_catalog)
        brand_combo.pack(side="left", padx=5)

        self.catalog_text = ctk.CTkTextbox(
            self.content_frame, width=800, height=500)
        self.catalog_text.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_brand_catalog()

    def load_brand_catalog(self, brand=None):
        if not brand:
            brand = self.brand_var.get()

        catalog_text = f"=== {brand.upper()} PARTS CATALOG ===\n\n"

        catalogs = {
            "Toyota": TOYOTA_PARTS_CATALOG,
            "Honda": HONDA_PARTS_CATALOG,
            "Mitsubishi": MITSUBISHI_PARTS_CATALOG,
            "Ford": FORD_PARTS_CATALOG,
            "Nissan": NISSAN_PARTS_CATALOG,
            "Hyundai": HYUNDAI_PARTS_CATALOG
        }

        catalog = catalogs.get(brand, {})

        for model, categories in catalog.items():
            catalog_text += f"🚗 {model.upper()}\n"
            catalog_text += "=" * 40 + "\n"

            for category, subcategories in categories.items():
                catalog_text += f"\n📁 {category.replace('_', ' ').title()}\n"
                catalog_text += "-" * 30 + "\n"

                for subcategory, parts in subcategories.items():
                    catalog_text += f"\n  🔧 {subcategory.replace('_', ' ').title()}\n"

                    for part_name, part_info in parts.items():
                        catalog_text += f"    • {part_name}: ₱{part_info['price']:.2f}\n"
                        catalog_text += f"      Models: {part_info['models']} | Years: {part_info['years']}\n"

            catalog_text += "\n" + "=" * 50 + "\n\n"

        self.catalog_text.delete("1.0", "end")
        self.catalog_text.insert("1.0", catalog_text)

    def show_settings(self):
        self.clear_content()

        title_label = ctk.CTkLabel(self.content_frame, text="Settings",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(settings_frame, text="Database Management:",
                     font=ctk.CTkFont(size=16)).pack(pady=20)

        db_frame = ctk.CTkFrame(settings_frame)
        db_frame.pack(pady=10)

        ctk.CTkButton(db_frame, text="Populate Sample Data",
                      command=self.populate_sample_data).pack(pady=5)

    def populate_sample_data(self):
        try:
            success_count = 0
            total_count = 0

            if add_all_toyota_parts_to_inventory():
                success_count += 1
            total_count += 1

            if add_all_honda_parts_to_inventory():
                success_count += 1
            total_count += 1

            if add_all_mitsubishi_parts_to_inventory():
                success_count += 1
            total_count += 1

            if add_all_ford_parts_to_inventory():
                success_count += 1
            total_count += 1

            if add_all_nissan_parts_to_inventory():
                success_count += 1
            total_count += 1

            if add_all_hyundai_parts_to_inventory():
                success_count += 1
            total_count += 1

            messagebox.showinfo(
                "Success", f"Sample data populated successfully!\n{success_count}/{total_count} brands added.")

            if hasattr(self, 'inventory_tree'):
                self.load_inventory()

        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not populate sample data: {str(e)}")

    def generate_report(self):
        try:
            conn = get_db()
            inventory_manager = InventoryManager(conn)
            sales_manager = SalesManager(conn)

            report = "=== AUTO PARTS SALES REPORT ===\n\n"
            report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            report += "SALES SUMMARY:\n"
            report += "=" * 50 + "\n"

            sales = sales_manager.get_sales_history()
            total_sales = sum(sale[4] for sale in sales)  # subtotal is index 4
            total_transactions = len(
                set(sale[1] for sale in sales))  # unique invoices

            report += f"Total Sales: ₱{total_sales:.2f}\n"
            report += f"Total Transactions: {total_transactions}\n"
            if total_transactions > 0:
                report += f"Average Sale: ₱{total_sales/total_transactions:.2f}\n\n"

            # Get top products
            product_sales = {}
            for sale in sales:
                product = sale[2]  # item name
                qty = sale[3]      # quantity
                if product in product_sales:
                    product_sales[product] += qty
                else:
                    product_sales[product] = qty

            top_products = sorted(product_sales.items(),
                                  key=lambda x: x[1], reverse=True)[:5]

            report += "TOP SELLING PRODUCTS:\n"
            for product, qty in top_products:
                report += f"  {product}: {qty} units\n"

            report += "\n" + "=" * 50 + "\n\n"

            report += "INVENTORY SUMMARY:\n"
            report += "=" * 50 + "\n"

            products = inventory_manager.get_all_products()
            total_products = len(products)
            low_stock = len([p for p in products if p.stock < 10])
            total_value = sum(p.price * p.stock for p in products)

            report += f"Total Products: {total_products}\n"
            report += f"Low Stock Items: {low_stock}\n"
            report += f"Total Inventory Value: ₱{total_value:.2f}\n"

            conn.close()

            report_dialog = ctk.CTkToplevel(self.root)
            report_dialog.title("Sales Report")
            report_dialog.geometry("600x500")

            report_text = ctk.CTkTextbox(report_dialog, width=580, height=450)
            report_text.pack(padx=10, pady=10)
            report_text.insert("1.0", report)
            report_text.configure(state="disabled")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not generate report: {str(e)}")

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def clear_content(self):
        if hasattr(self, 'content_frame'):
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoPartsAdminSystem()
    app.run()
