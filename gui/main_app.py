import customtkinter as ctk
from tkinter import messagebox
from database.db_init import init_db
from database.db_connection import get_db
from managers.inventory_manager import InventoryManager
from managers.sales_manager import SalesManager
from managers.receipt_manager import ReceiptManager
from models.cart import ShoppingCart
from models.sale import Sale
from utils.helpers import apply_theme, generate_invoice_number
from gui.login_screen import LoginScreen
from gui.dashboard import Dashboard
from gui.inventory_screen import InventoryScreen
from gui.pos_screen import POSScreen
from gui.sales_screen import SalesScreen
from gui.catalog_screen import CatalogScreen
from catalogs.catalog_manager import CatalogManager


class AutoPartsAdminSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Auto Parts Admin System")
        self.root.geometry("1200x800")
        apply_theme(self.root)

        init_db()

        self.current_user = None
        self.cart = []  # Legacy cart
        self.oop_cart = ShoppingCart()  # New OOP cart
        self.inventory_manager = InventoryManager(get_db())
        self.sales_manager = SalesManager(get_db())
        self.receipt_manager = ReceiptManager()
        self.catalog_manager = CatalogManager()

        self.setup_gui()

    def setup_gui(self):
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_login_screen()

    def show_login_screen(self):
        self.clear_screen()
        LoginScreen(self.main_container, self)

    def show_main_dashboard(self):
        self.clear_screen()
        self.create_sidebar()
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both",
                                expand=True, padx=10, pady=10)
        self.show_dashboard()

    def create_sidebar(self):
        from gui.components import create_sidebar
        create_sidebar(self.main_container, self)

    def show_dashboard(self):
        self.clear_content()
        Dashboard(self.content_frame, self)

    def show_inventory(self):
        self.clear_content()
        InventoryScreen(self.content_frame, self)

    def show_pos(self):
        self.clear_content()
        POSScreen(self.content_frame, self)

    def show_sales_history(self):
        self.clear_content()
        SalesScreen(self.content_frame, self)

    def show_parts_catalog(self):
        self.clear_content()
        CatalogScreen(self.content_frame, self)

    def show_settings(self):
        self.clear_content()
        # Settings screen implementation would go here
        self.show_settings_screen()

    def show_add_product(self):
        """Show add product dialog"""
        self.show_add_product_dialog()

    def show_add_product_dialog(self):
        """Show dialog to add new product"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add New Product", font=ctk.CTkFont(
            size=18, weight="bold")).pack(pady=10)

        fields = [
            ("Name", "entry"),
            ("Price", "entry"),
            ("Stock", "entry"),
            ("Category", "entry"),
            ("Brand", "entry"),
            ("Vehicle Model", "entry"),
            ("Part Category", "entry"),
            ("Part Subcategory", "entry"),
            ("Year Range", "entry")
        ]

        entries = {}

        for field, field_type in fields:
            ctk.CTkLabel(dialog, text=field).pack(pady=5)
            if field_type == "entry":
                entry = ctk.CTkEntry(dialog, width=300)
                entry.pack(pady=5)
                entries[field] = entry

        def save_product():
            try:
                from models.product import Product
                new_product = Product(
                    name=entries["Name"].get(),
                    price=float(entries["Price"].get()),
                    stock=int(entries["Stock"].get()),
                    category=entries["Category"].get(),
                    brand=entries["Brand"].get(),
                    vehicle_model=entries["Vehicle Model"].get(),
                    part_category=entries["Part Category"].get(),
                    part_subcategory=entries["Part Subcategory"].get(),
                    year_range=entries["Year Range"].get()
                )

                conn = get_db()
                cur = conn.cursor()
                cur.execute("""INSERT INTO inventory 
                            (name, price, stock, category, brand, vehicle_model, part_category, part_subcategory, year_range) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                new_product.name,
                                new_product.price,
                                new_product.stock,
                                new_product.category,
                                new_product.brand,
                                new_product.vehicle_model,
                                new_product.part_category,
                                new_product.part_subcategory,
                                new_product.year_range
                            ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Product added successfully!")
                dialog.destroy()

                # Refresh both inventory and dashboard
                if hasattr(self, 'inventory_tree'):
                    self.load_inventory()
                self.show_dashboard()

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Could not add product: {str(e)}")

        ctk.CTkButton(dialog, text="Save Product",
                      command=save_product).pack(pady=20)

    def show_settings_screen(self):
        """Show settings screen"""
        title_label = ctk.CTkLabel(self.content_frame, text="Settings",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(settings_frame, text="Database Management:",
                     font=ctk.CTkFont(size=16)).pack(pady=20)

        db_frame = ctk.CTkFrame(settings_frame)
        db_frame.pack(pady=10)

        ctk.CTkButton(db_frame, text="Populate Sample Data",
                      command=self.populate_sample_data).pack(pady=5)

        # Clear sales history button
        ctk.CTkButton(db_frame, text="Clear All Sales History",
                      command=self.clear_sales_history,
                      fg_color="#d9534f", hover_color="#c9302c").pack(pady=5)

    def clear_sales_history(self):
        """Clear all sales history from the database"""
        result = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to delete ALL sales history?\nThis action cannot be undone!"
        )

        if not result:
            return

        try:
            conn = get_db()
            cur = conn.cursor()

            # Delete all sales records
            cur.execute("DELETE FROM sales")

            # Reset auto-increment counter (optional)
            cur.execute("DELETE FROM sqlite_sequence WHERE name='sales'")

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success", "All sales history has been cleared successfully!")

            # Refresh the sales history display if it's currently open
            if hasattr(self, 'sales_tree'):
                self.load_sales_history()

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not clear sales history: {str(e)}")

    def load_inventory(self):
        """Load inventory - for compatibility"""
        if hasattr(self, 'inventory_tree'):
            # This would be called from inventory screen
            pass

    def load_sales_history(self):
        """Load sales history - for compatibility"""
        if hasattr(self, 'sales_tree'):
            # This would be called from sales screen
            pass

    def populate_sample_data(self):
        try:
            success_count = 0
            total_count = 0

            catalogs = [
                ("Toyota", self.catalog_manager.add_all_toyota_parts_to_inventory),
                ("Honda", self.catalog_manager.add_all_honda_parts_to_inventory),
                ("Mitsubishi", self.catalog_manager.add_all_mitsubishi_parts_to_inventory),
                ("Ford", self.catalog_manager.add_all_ford_parts_to_inventory),
                ("Nissan", self.catalog_manager.add_all_nissan_parts_to_inventory),
                ("Hyundai", self.catalog_manager.add_all_hyundai_parts_to_inventory)
            ]

            for brand_name, catalog_func in catalogs:
                if catalog_func():
                    success_count += 1
                total_count += 1

            messagebox.showinfo(
                "Success", f"Sample data populated successfully!\n{success_count}/{total_count} brands added.")

            # Refresh views
            if hasattr(self, 'inventory_tree'):
                self.load_inventory()

            self.show_dashboard()

        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not populate sample data: {str(e)}")

    def generate_report(self):
        """Generate sales report"""
        try:
            conn = get_db()
            inventory_manager = InventoryManager(conn)
            sales_manager = SalesManager(conn)

            report = "=== AUTO PARTS SALES REPORT ===\n\n"
            report += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            report += "SALES SUMMARY:\n"
            report += "=" * 50 + "\n"

            sales = sales_manager.get_sales_history()
            total_sales = sum(sale[4] for sale in sales)  # subtotal is index 4
            total_transactions = len(
                set(sale[1] for sale in sales))  # unique invoices

            report += f"Total Sales: ₱{total_sales:.2f}\n"
            report += f"Total Transactions: {total_transactions}\n"
            if total_transactions > 0:
                report += f"Average Sale: ₱{total_sales/total_transactions:.2f}\n\n"

            # Get top products
            product_sales = {}
            for sale in sales:
                product = sale[2]  # item name
                qty = sale[3]      # quantity
                if product in product_sales:
                    product_sales[product] += qty
                else:
                    product_sales[product] = qty

            top_products = sorted(product_sales.items(),
                                  key=lambda x: x[1], reverse=True)[:5]

            report += "TOP SELLING PRODUCTS:\n"
            for product, qty in top_products:
                report += f"  {product}: {qty} units\n"

            report += "\n" + "=" * 50 + "\n\n"

            report += "INVENTORY SUMMARY:\n"
            report += "=" * 50 + "\n"

            products = inventory_manager.get_all_products()
            total_products = len(products)
            low_stock = len([p for p in products if p.stock < 10])
            total_value = sum(p.price * p.stock for p in products)

            report += f"Total Products: {total_products}\n"
            report += f"Low Stock Items: {low_stock}\n"
            report += f"Total Inventory Value: ₱{total_value:.2f}\n"

            conn.close()

            report_dialog = ctk.CTkToplevel(self.root)
            report_dialog.title("Sales Report")
            report_dialog.geometry("600x500")

            report_text = ctk.CTkTextbox(report_dialog, width=580, height=450)
            report_text.pack(padx=10, pady=10)
            report_text.insert("1.0", report)
            report_text.configure(state="disabled")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Could not generate report: {str(e)}")

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def clear_content(self):
        if hasattr(self, 'content_frame'):
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    def logout(self):
        self.current_user = None
        self.show_login_screen()

    def run(self):
        self.root.mainloop()
