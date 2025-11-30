import datetime
import customtkinter as ctk
from utils.constants import THEME_MODE


def apply_theme(window=None):
    """Apply theme to the application"""
    ctk.set_appearance_mode(THEME_MODE)
    ctk.set_default_color_theme("blue")
    if window is not None:
        try:
            window.update()
        except Exception:
            pass


def generate_invoice_number():
    """Generate unique invoice number"""
    return f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


def validate_number(value: str) -> bool:
    """Validate if string is a number"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def darken_color(color):
    """Darken color for hover effects"""
    color_map = {
        "#318675": "#00a085",
        "#0984e3": "#0971c2",
        "#f39c12": "#e67e22",
        "#6c5ce7": "#5649c0"
    }
    return color_map.get(color, color)
