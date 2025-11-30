import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from utils.helpers import apply_theme


class LoginScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()

    def create_widgets(self):
        # Main container
        login_container = ctk.CTkFrame(
            self.parent, fg_color=("white", "#1a1a2e"))
        login_container.pack(expand=True, fill="both", padx=150, pady=80)

        # Header
        header_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        header_frame.pack(pady=(40, 30))

        title_label = ctk.CTkLabel(
            header_frame, text="Auto Parts Pro", font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=5)

        subtitle_label = ctk.CTkLabel(
            header_frame, text="Admin System", font=ctk.CTkFont(size=18), text_color="#FF6B35")
        subtitle_label.pack()

        decor_line = ctk.CTkFrame(
            header_frame, height=3, fg_color="#FF6B35", width=100)
        decor_line.pack(pady=10)

        # Form
        form_frame = ctk.CTkFrame(login_container, fg_color=(
            "#f8f9fa", "#2d3047"), corner_radius=20, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)

        form_title = ctk.CTkLabel(
            form_frame, text="Welcome Back!", font=ctk.CTkFont(size=22, weight="bold"))
        form_title.pack(pady=(30, 20))

        # Username
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.pack(pady=15, padx=40, fill="x")

        ctk.CTkLabel(username_frame, text="👤 Username", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w")

        self.username_entry = ctk.CTkEntry(username_frame, height=45, placeholder_text="Enter your username", font=ctk.CTkFont(
            size=14), border_width=2, border_color=("#FF6B35", "#FF9A3D"), corner_radius=12)
        self.username_entry.pack(pady=(8, 0), fill="x")
        self.username_entry.insert(0, "autoparts")

        # Password
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(pady=15, padx=40, fill="x")

        ctk.CTkLabel(password_frame, text="🔒 Password", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w")

        self.password_entry = ctk.CTkEntry(password_frame, height=45, placeholder_text="Enter your password", show="•", font=ctk.CTkFont(
            size=14), border_width=2, border_color=("#FF6B35", "#FF9A3D"), corner_radius=12)
        self.password_entry.pack(pady=(8, 0), fill="x")
        self.password_entry.insert(0, "oilengine")

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=(30, 20), padx=40, fill="x")

        login_btn = ctk.CTkButton(button_frame, text="🚀 Login to Dashboard", command=self.login, font=ctk.CTkFont(
            size=16, weight="bold"), height=50, fg_color=("#FF6B35", "#FF9A3D"), hover_color=("#E55A30", "#FF8C2D"), corner_radius=12)
        login_btn.pack(fill="x", pady=10)

        populate_btn = ctk.CTkButton(button_frame, text="📊 Populate Sample Data", command=self.app.populate_sample_data, font=ctk.CTkFont(size=14), height=40, fg_color=(
            "#2d3047", "#4a4e69"), hover_color=("#3d405b", "#5a5e7d"), corner_radius=10, border_color=("#FF6B35", "#FF9A3D"), border_width=1)
        populate_btn.pack(fill="x", pady=(5, 10))

        # Footer
        footer_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        footer_frame.pack(pady=(20, 30))

        dots_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        dots_frame.pack()

        colors = ["#FF6B35", "#FF9A3D", "#2d3047", "#4a4e69"]
        for color in colors:
            dot = ctk.CTkFrame(dots_frame, width=8, height=8,
                               fg_color=color, corner_radius=4)
            dot.pack(side="left", padx=3)

        footer_text = ctk.CTkLabel(footer_frame, text="Auto Parts Management System v2.0", font=ctk.CTkFont(
            size=12), text_color=("#7f8c8d", "#bdc3c7"))
        footer_text.pack(pady=10)

        self.app.root.after(100, lambda: self.username_entry.focus())
        apply_theme(self.app.root)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            conn = self.app.inventory_manager.db
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                        (username, password))
            user = cur.fetchone()

            if user:
                self.app.current_user = user
                self.app.show_main_dashboard()
            else:
                messagebox.showerror(
                    "Login Failed", "Invalid username or password")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")
