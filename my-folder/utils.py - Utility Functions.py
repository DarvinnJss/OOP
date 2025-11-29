import datetime
import sqlite3
import customtkinter as ctk

def get_db():
    return sqlite3.connect("auto_parts.db")

def apply_theme(window=None):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    if window is not None:
        try:
            window.update()
        except:
            pass

def generate_invoice_number():
    return f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def validate_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False

def format_currency(amount: float) -> str:
    return f"₱{amount:,.2f}"