import customtkinter as ctk


def create_sidebar(parent, app):
    """Create sidebar navigation"""
    sidebar = ctk.CTkFrame(parent, width=280, fg_color=(
        "#1a1a2e", "#16213e"), corner_radius=0)
    sidebar.pack(side="left", fill="y", padx=(0, 5), pady=10)
    sidebar.pack_propagate(False)

    # User profile section
    user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    user_frame.pack(pady=30, padx=20, fill="x")

    welcome_label = ctk.CTkLabel(user_frame, text=f"Welcome,", font=ctk.CTkFont(
        size=14), text_color=("#FF9A3D", "#FF9A3D"))
    welcome_label.pack()

    username_label = ctk.CTkLabel(user_frame, text=f"{app.current_user[1].title()}!", font=ctk.CTkFont(
        size=18, weight="bold"), text_color=("#FF6B35", "#FF6B35"))
    username_label.pack(pady=5)

    # Navigation section
    nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    nav_frame.pack(fill="both", expand=True, padx=15, pady=20)

    nav_buttons = [
        ("📊 Dashboard", app.show_dashboard),
        ("📦 Inventory", app.show_inventory),
        ("🛒 Point of Sale", app.show_pos),
        ("💰 Sales History", app.show_sales_history),
        ("🚗 Parts Catalog", app.show_parts_catalog),
        ("⚙️ Settings", app.show_settings),
    ]

    for text, command in nav_buttons:
        btn = ctk.CTkButton(nav_frame, text=text, command=command, font=ctk.CTkFont(size=14), anchor="w", height=45,
                            fg_color=("#2d3047", "#2d3047"), hover_color=("#FF6B35", "#FF6B35"), text_color="white", corner_radius=10)
        btn.pack(fill="x", pady=8)

    # Logout button at bottom
    logout_btn = ctk.CTkButton(sidebar, text="🚪 Logout", command=app.logout, font=ctk.CTkFont(size=14, weight="bold"),
                               height=45, fg_color=("#e74c3c", "#c0392b"), hover_color=("#ff7979", "#e74c3c"), corner_radius=10)
    logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)
