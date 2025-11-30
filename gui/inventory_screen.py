import customtkinter as ctk
from tkinter import ttk, messagebox
from models.product import Product


class InventoryScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()
        self.load_inventory()

    def create_widgets(self):
        # Header
        title_label = ctk.CTkLabel(self.parent, text="📦 Inventory Management",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color=("#FF6B35", "#FF6B35"))
        title_label.pack(pady=20)

        # Search and Actions Bar
        search_frame = ctk.CTkFrame(
            self.parent, corner_radius=15, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        search_frame.pack(fill="x", padx=20, pady=10)

        # Search Components
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(
            weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, width=200, height=35, placeholder_text="Search products...",
                                         border_color=("#FF6B35", "#FF9A3D"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10)

        # Action Buttons
        buttons = [
            ("🔎 Search", self.search_inventory, 2, "#FF6B35", "#E55A30"),
            ("🔄 Refresh", self.load_inventory, 3, "#0984e3", "#0971c2"),
            ("➕ Add Product", self.show_add_product, 4, "#00b894", "#00a085"),
            ("🗑️ Delete", self.delete_selected_product, 5, "#e74c3c", "#c0392b"),
            ("📊 Populate Catalog", self.app.populate_sample_data, 6, "#fdcb6e", "#f9a825")
        ]

        for text, command, col, fg_color, hover_color in buttons:
            btn = ctk.CTkButton(search_frame, text=text, command=command, height=35,
                                fg_color=fg_color, hover_color=hover_color,
                                font=ctk.CTkFont(size=12, weight="bold"))
            btn.grid(row=0, column=col, padx=5, pady=10)

        # Table
        table_frame = ctk.CTkFrame(
            self.parent, corner_radius=15, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Price", "Stock", "Category",
                   "Brand", "Vehicle Model", "Part Category", "Year Range")
        self.inventory_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=20)

        # Column Configuration
        column_config = {
            "ID": ("🔢 ID", 60),
            "Name": ("📛 Name", 150),
            "Price": ("💰 Price", 80),
            "Stock": ("📊 Stock", 60),
            "Category": ("📁 Category", 120),
            "Brand": ("🏷️ Brand", 100),
            "Vehicle Model": ("🚗 Model", 120),
            "Part Category": ("🔧 Part Type", 120),
            "Year Range": ("📅 Years", 100)
        }

        for col in columns:
            heading_text, width = column_config[col]
            self.inventory_tree.heading(col, text=heading_text)
            self.inventory_tree.column(col, width=width)

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)

        self.inventory_tree.pack(
            side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Bind double-click to edit
        self.inventory_tree.bind("<Double-1>", self.edit_inventory_item)

    def load_inventory(self):
        try:
            products = self.app.inventory_manager.get_all_products()

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            for product in products:
                self.inventory_tree.insert("", "end", values=(
                    product.id,
                    product.name,
                    f"₱{product.price:.2f}",
                    product.stock,
                    product.category,
                    product.brand,
                    product.vehicle_model,
                    product.part_category,
                    product.year_range
                ))

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not load inventory: {str(e)}")

    def search_inventory(self):
        search_term = self.search_entry.get()

        try:
            products = self.app.inventory_manager.search_products(search_term)

            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)

            if not products:
                self.inventory_tree.insert("", "end", values=(
                    "", "There's no product in the inventory", "", "", "", "", "", "", ""
                ))
            else:
                for product in products:
                    self.inventory_tree.insert("", "end", values=(
                        product.id,
                        product.name,
                        f"₱{product.price:.2f}",
                        product.stock,
                        product.category,
                        product.brand,
                        product.vehicle_model,
                        product.part_category,
                        product.year_range
                    ))

        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def delete_selected_product(self):
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning(
                "Warning", "Please select a product to delete!")
            return

        item = self.inventory_tree.item(selection[0])
        product_data = item['values']
        product_id = product_data[0]
        product_name = product_data[1]

        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{product_name}'?\nThis action cannot be undone!"
        )

        if not result:
            return

        try:
            success = self.app.inventory_manager.delete_product(product_id)

            if success:
                messagebox.showinfo(
                    "Success", f"Product '{product_name}' deleted successfully!")
                self.load_inventory()
                self.app.show_dashboard()
            else:
                messagebox.showerror(
                    "Error", "Failed to delete product from database.")

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not delete product: {str(e)}")

    def show_add_product(self):
        # Add product dialog implementation would go here
        pass

    def edit_inventory_item(self, event):
        # Edit product implementation would go here
        pass
