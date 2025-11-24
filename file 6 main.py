import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# Import from separated files
from models import Product, CartItem, Sale, User
from managers import InventoryManager, SalesManager, ShoppingCart, ReceiptManager
from database import init_db, get_db
from catalogs import *
from utils import *


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

    # ALL YOUR EXISTING GUI METHODS GO HERE
    # setup_gui(), show_login_screen(), login(), show_main_dashboard(), etc.
    # ... (copy all the GUI methods from your original code)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoPartsAdminSystem()
    app.run()
