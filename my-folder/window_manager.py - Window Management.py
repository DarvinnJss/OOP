import customtkinter as ctk

class WindowManager:
    def __init__(self, root):
        self.root = root
        self.windows = {}

    def create_window(self, title, geometry="800x600"):
        window = ctk.CTkToplevel(self.root)
        window.title(title)
        window.geometry(geometry)
        window.transient(self.root)
        window.grab_set()
        return window

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()