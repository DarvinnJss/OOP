import customtkinter as ctk
from tkinter import ttk, messagebox


class SalesScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()
        self.load_sales_history()

    def create_widgets(self):
        # Header
        title_label = ctk.CTkLabel(self.parent, text="💰 SALES HISTORY",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(pady=20)

        # Filter section
        filter_frame = ctk.CTkFrame(self.parent, fg_color=("#f8f9fa", "#2d3047"),
                                    corner_radius=15, border_width=2, border_color="#FF6B35")
        filter_frame.pack(fill="x", padx=20, pady=15)

        # Date filter
        ctk.CTkLabel(filter_frame, text="📅 Date:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=12)
        self.sales_date_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="YYYY-MM-DD", width=120, height=35,
            border_color="#3498db", corner_radius=8)
        self.sales_date_entry.grid(row=0, column=1, padx=5, pady=12)

        # Invoice filter
        ctk.CTkLabel(filter_frame, text="📋 Invoice:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=2, padx=10, pady=12)
        self.invoice_entry = ctk.CTkEntry(filter_frame, width=150, height=35,
                                          border_color="#3498db", corner_radius=8)
        self.invoice_entry.grid(row=0, column=3, padx=5, pady=12)

        # Action buttons
        search_btn = ctk.CTkButton(
            filter_frame, text="🔍 Search", command=self.search_sales,
            fg_color="#0984e3", hover_color="#0971c2", height=35, width=100)
        search_btn.grid(row=0, column=4, padx=8, pady=12)

        refresh_btn = ctk.CTkButton(
            filter_frame, text="🔄 Refresh", command=self.load_sales_history,
            fg_color="#00b894", hover_color="#00a085", height=35, width=100)
        refresh_btn.grid(row=0, column=5, padx=8, pady=12)

        # Clear history button
        clear_btn = ctk.CTkButton(
            filter_frame, text="🗑️ Clear All History",
            command=self.clear_sales_history,
            fg_color="#e74c3c", hover_color="#c0392b", height=35, width=140
        )
        clear_btn.grid(row=0, column=6, padx=8, pady=12)

        # Table section
        table_frame = ctk.CTkFrame(self.parent, fg_color=("#ffffff", "#4a4e69"),
                                   corner_radius=15, border_width=2, border_color="#FF6B35")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # Define columns
        columns = {
            "ID": ("🔢 ID", 60),
            "Invoice": ("📋 Invoice", 120),
            "Item": ("📦 Item", 150),
            "Qty": ("🔢 Qty", 80),
            "Subtotal": ("💰 Subtotal", 100),
            "Date": ("📅 Date", 120),
            "Customer": ("👤 Customer", 120),
            "Status": ("✅ Status", 100)
        }

        self.sales_tree = ttk.Treeview(table_frame, columns=list(
            columns.keys()), show="headings", height=20)

        # Configure columns
        for col, (heading, width) in columns.items():
            self.sales_tree.heading(col, text=heading)
            self.sales_tree.column(col, width=width)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        self.sales_tree.pack(side="left", fill="both",
                             expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def load_sales_history(self):
        try:
            sales = self.app.sales_manager.get_sales_history()

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            for sale in sales:
                self.sales_tree.insert("", "end", values=sale)

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not load sales history: {str(e)}")

    def search_sales(self):
        date = self.sales_date_entry.get()
        invoice = self.invoice_entry.get()

        try:
            sales = self.app.sales_manager.get_sales_history(date, invoice)

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            for sale in sales:
                self.sales_tree.insert("", "end", values=sale)

        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def clear_sales_history(self):
        result = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to delete ALL sales history?\nThis action cannot be undone!"
        )

        if not result:
            return

        try:
            conn = self.app.inventory_manager.db
            cur = conn.cursor()

            cur.execute("DELETE FROM sales")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='sales'")

            conn.commit()

            messagebox.showinfo(
                "Success", "All sales history has been cleared successfully!")
            self.load_sales_history()

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not clear sales history: {str(e)}")
