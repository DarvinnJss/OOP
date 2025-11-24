import datetime
import customtkinter as ctk

APP_TITLE = "Auto Parts Admin System"
THEME_MODE = "dark"


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
