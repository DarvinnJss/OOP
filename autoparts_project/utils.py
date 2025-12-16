"""
AUTO PARTS ADMIN SYSTEM - Complete Application
With Auto Parts Catalog Integration
"""
import sqlite3
import datetime
import os
import sys
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
# Add current directory to path to import catalog modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================
DB_FILE = "autoparts.db"
APP_TITLE = "Auto Parts Admin System"
THEME_MODE = "dark"

# BASE CLASS
# ============================================================================
class AutoParts:
    """Base class for all Auto Parts components"""
    
   
    def validate_number(self, value: str) -> bool:
        """Validate if value is a number"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def get_current_time(self):
        """Get current datetime"""
        return datetime.datetime.now()
    
    def format_currency(self, amount):
        """Format amount as currency"""
        return f"₱{amount:,.2f}"
    
    def apply_theme(self, window=None):
        """Apply theme to application"""
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme("blue")
        if window is not None:
            try:
                window.update()
            except:
                pass
    
    def darken_color(self, color):
        """Darken a hex color for hover effects"""
        color_map = {
            "#00b894": "#00a085",
            "#0984e3": "#0971c2",
            "#f39c12": "#e67e22",
            "#6c5ce7": "#5649c0"
        }
        return color_map.get(color, color)
