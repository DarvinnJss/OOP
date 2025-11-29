import sqlite3
import os

class Database:
    def __init__(self, db_file="auto_parts.db"):
        self.db_file = db_file
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_file)