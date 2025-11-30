import customtkinter as ctk
import datetime
from database.db_connection import get_db


class Dashboard:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()
        self.load_dashboard_data()

    def create_widgets(self):
        # Header with professional styling
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=20)

        title_label = ctk.CTkLabel(header_frame, text="📊 DASHBOARD OVERVIEW",
                                   font=ctk.CTkFont(size=28, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(side="left")

        refresh_btn = ctk.CTkButton(header_frame, text="🔄 Refresh",
                                    command=self.refresh_dashboard_data,
                                    width=120, height=35,
                                    fg_color="#2d3047", hover_color="#FF6B35",
                                    corner_radius=8)
        refresh_btn.pack(side="right", padx=10)

        # Metrics Cards Section
        self.metrics_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.metrics_frame.pack(fill="x", padx=20, pady=20)

        # Quick Actions Section
        actions_frame = ctk.CTkFrame(self.parent, fg_color=("#f8f9fa", "#2d3047"),
                                     corner_radius=15, border_width=2, border_color="#FF6B35")
        actions_frame.pack(fill="x", padx=20, pady=20)

        # Quick Actions Header
        actions_header = ctk.CTkFrame(
            actions_frame, fg_color="#FF6B35", corner_radius=10)
        actions_header.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(actions_header, text="⚡ QUICK ACTIONS",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(pady=8)

        # Action Buttons
        action_buttons_frame = ctk.CTkFrame(
            actions_frame, fg_color="transparent")
        action_buttons_frame.pack(fill="both", expand=True, padx=20, pady=20)

        action_buttons = [
            {"text": "➕ ADD NEW PRODUCT",
                "command": self.app.show_add_product, "color": "#00b894"},
            {"text": "🛒 PROCESS SALE", "command": self.app.show_pos, "color": "#0984e3"},
            {"text": "📦 VIEW INVENTORY",
                "command": self.app.show_inventory, "color": "#f39c12"},
            {"text": "📊 GENERATE REPORT",
                "command": self.generate_report, "color": "#6c5ce7"}
        ]

        for action in action_buttons:
            btn = ctk.CTkButton(action_buttons_frame,
                                text=action["text"],
                                command=action["command"],
                                font=ctk.CTkFont(size=14, weight="bold"),
                                height=50,
                                fg_color=action["color"],
                                hover_color=self.darken_color(action["color"]),
                                corner_radius=10)
            btn.pack(pady=10, padx=20, fill="x")

    def load_dashboard_data(self):
        try:
            conn = get_db()
            cur = conn.cursor()

            # Get accurate product count directly from database
            cur.execute("SELECT COUNT(*) FROM inventory")
            total_products = cur.fetchone()[0]

            # Get low stock count
            cur.execute("SELECT COUNT(*) FROM inventory WHERE stock < 10")
            low_stock = cur.fetchone()[0]

            # Get today's sales
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cur.execute(
                "SELECT COUNT(DISTINCT invoice), SUM(subtotal) FROM sales WHERE date LIKE ?", (f"{today}%",))
            today_sales_data = cur.fetchone()
            today_sales_count = today_sales_data[0] or 0
            today_sales_total = today_sales_data[1] or 0.0

            conn.close()

            # Update metrics display
            self.update_metrics_display(
                total_products, low_stock, today_sales_count, today_sales_total)

        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    def update_metrics_display(self, total_products, low_stock, today_sales_count, today_sales_total):
        # Clear previous metrics
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        metrics_data = [
            {"title": "📦 TOTAL PRODUCTS", "value": total_products,
                "color": "#0984e3", "icon": "📦"},
            {"title": "⚠️ LOW STOCK ITEMS", "value": low_stock,
                "color": "#e74c3c", "icon": "⚠️"},
            {"title": "💰 TODAY'S SALES", "value": today_sales_count,
                "color": "#00b894", "icon": "💰"},
            {"title": "💵 TODAY'S REVENUE", "value": f"₱{today_sales_total:,.2f}",
                "color": "#f39c12", "icon": "💵"}
        ]

        for i, metric in enumerate(metrics_data):
            metric_card = ctk.CTkFrame(
                self.metrics_frame, fg_color=metric["color"], corner_radius=15)
            metric_card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            # Icon and Title
            icon_frame = ctk.CTkFrame(metric_card, fg_color="transparent")
            icon_frame.pack(pady=(15, 5))

            ctk.CTkLabel(icon_frame, text=metric["icon"], font=ctk.CTkFont(
                size=20)).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(icon_frame, text=metric["title"], font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="left")

            # Value
            ctk.CTkLabel(metric_card, text=str(metric["value"]),
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color="white").pack(pady=(5, 15))

        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def refresh_dashboard_data(self):
        """Refresh dashboard data"""
        self.load_dashboard_data()

    def darken_color(self, color):
        """Darken color for hover effects"""
        color_map = {
            "#00b894": "#00a085",
            "#0984e3": "#0971c2",
            "#f39c12": "#e67e22",
            "#6c5ce7": "#5649c0"
        }
        return color_map.get(color, color)

    def generate_report(self):
        # Report generation implementation would go here
        pass
