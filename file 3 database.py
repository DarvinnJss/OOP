import sqlite3
from tkinter import messagebox

DB_FILE = "autoparts.db"


def get_db():
    return sqlite3.connect(DB_FILE)


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
