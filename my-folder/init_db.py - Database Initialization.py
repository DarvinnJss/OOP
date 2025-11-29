import sqlite3
from db import Database

def init_database():
    """Initialize the database with required tables"""
    db = Database()
    conn = db.get_connection()
    cur = conn.cursor()

    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # Inventory table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS inventory(
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
    ''')

    # Sales table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales(
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
    ''')

    # Insert default user
    cur.execute('''
        INSERT OR IGNORE INTO users(id, username, password)
        VALUES(1, 'autoparts', 'oilengine')
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()