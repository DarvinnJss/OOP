import sqlite3
from utils.constants import DB_FILE


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)
