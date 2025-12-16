from utils import *

# DATABASE CLASSES
# ============================================================================
class Database(AutoParts):
    """Database management class"""
    
    def __init__(self):
        super().__init__()
        self.db_file = DB_FILE
        self.init_db()
    
    def get_db(self):
        """Get database connection"""
        return sqlite3.connect(self.db_file)
    
    def init_db(self):
        """Initialize the database with required tables"""
        try:
            conn = self.get_db()
            cur = conn.cursor()
            
            # Create users table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )
                """
            )
            
            # Create inventory table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL,
                    stock INTEGER,
                    category TEXT,
                    image TEXT,
                    brand TEXT,
                    vehicle_model TEXT,
                    year_range TEXT,
                    part_category TEXT,
                    part_subcategory TEXT
                )
                """
            )
            # Create trash table for deleted products
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS trash(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_id INTEGER,
                    name TEXT,
                    price REAL,
                    stock INTEGER,
                    category TEXT,
                    image TEXT,
                    brand TEXT,
                    vehicle_model TEXT,
                    year_range TEXT,
                    part_category TEXT,
                    part_subcategory TEXT,
                    deleted_at TEXT,
                    deleted_by TEXT
                )
                """
            )
            # Create sales table with all required columns
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sales(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice TEXT,
                    item TEXT,
                    qty INTEGER,
                    subtotal REAL,
                    date TEXT,
                    notes TEXT,
                    customer_name TEXT,
                    status TEXT DEFAULT 'COMPLETED',
                    return_reason TEXT,
                    return_date TEXT,
                    returned_qty INTEGER DEFAULT 0,
                    original_sale_id INTEGER,
                    original_invoice TEXT
                )
                """
            )
            
            # Check and add missing columns if needed
            cur.execute("PRAGMA table_info(sales)")
            columns = cur.fetchall()
            column_names = [col[1] for col in columns]
            
            # Add missing columns
            missing_columns = {
                'original_invoice': 'TEXT',
                'return_date': 'TEXT',
                'returned_qty': 'INTEGER DEFAULT 0',
                'original_sale_id': 'INTEGER',
                'status': 'TEXT DEFAULT "COMPLETED"'
            }
            
            for column, column_type in missing_columns.items():
                if column not in column_names:
                    print(f"Adding missing column: {column}")
                    cur.execute(f"ALTER TABLE sales ADD COLUMN {column} {column_type}")
            
            # Create default user
            try:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO users(id, username, password)
                    VALUES(1, ?, ?)
                    """,
                    ("autoparts", "oilengine"),
                )
            except:
                pass
            
            conn.commit()
            conn.close()
            print("Database initialization completed successfully")
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Database Error", f"Database initialization failed: {str(e)}")