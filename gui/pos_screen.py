import customtkinter as ctk
from tkinter import ttk, messagebox
from models.sale import Sale
from utils.helpers import generate_invoice_number


class POSScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()
        self.load_products_pos()

    def create_widgets(self):
        # Main title
        title_label = ctk.CTkLabel(self.parent, text="🛒 POINT OF SALE",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(pady=20)

        # Main POS frame
        pos_frame = ctk.CTkFrame(self.parent, fg_color=("#f8f9fa", "#2d3047"),
                                 corner_radius=15, border_width=2, border_color="#FF6B35")
        pos_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left side - Products
        left_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both",
                        expand=True, padx=10, pady=10)

        # Products header
        products_header = ctk.CTkFrame(
            left_frame, fg_color="#FF6B35", corner_radius=10)
        products_header.pack(fill="x", pady=10)
        ctk.CTkLabel(products_header, text="📦 PRODUCTS", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)

        # Search section
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(
            weight="bold")).pack(side="left", padx=5)
        self.pos_search_entry = ctk.CTkEntry(search_frame, width=200, height=35,
                                             placeholder_text="Type to search products...",
                                             border_color="#FF6B35", corner_radius=8)
        self.pos_search_entry.pack(side="left", padx=5)
        self.pos_search_entry.bind("<KeyRelease>", self.search_products_pos)

        # Products treeview
        tree_frame = ctk.CTkFrame(left_frame, fg_color=(
            "#ffffff", "#4a4e69"), corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.pos_products_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Brand", "Model", "Years", "Price", "Stock"),
                                              show="headings", height=15)

        columns = {
            "ID": ("🔢 ID", 60),
            "Name": ("📛 Product Name", 180),
            "Brand": ("🏷️ Brand", 80),
            "Model": ("🚗 Model", 100),
            "Years": ("📅 Years", 80),
            "Price": ("💰 Price", 80),
            "Stock": ("📊 Stock", 60)
        }

        for col, (text, width) in columns.items():
            self.pos_products_tree.heading(col, text=text)
            self.pos_products_tree.column(col, width=width)

        self.pos_products_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.pos_products_tree.bind("<Double-1>", self.add_to_cart)

        # Right side - Shopping Cart
        right_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", padx=10, pady=10)

        # Cart header
        cart_header = ctk.CTkFrame(
            right_frame, fg_color="#00b894", corner_radius=10)
        cart_header.pack(fill="x", pady=10)
        ctk.CTkLabel(cart_header, text="🛒 SHOPPING CART", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)

        # Cart treeview
        cart_tree_frame = ctk.CTkFrame(right_frame, fg_color=(
            "#ffffff", "#4a4e69"), corner_radius=10)
        cart_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.cart_tree = ttk.Treeview(cart_tree_frame, columns=("Product", "Qty", "Price", "Subtotal"),
                                      show="headings", height=10)

        cart_columns = {
            "Product": ("📦 Product", 150),
            "Qty": ("🔢 Qty", 60),
            "Price": ("💰 Price", 80),
            "Subtotal": ("💵 Subtotal", 100)
        }

        for col, (text, width) in cart_columns.items():
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, width=width)

        self.cart_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Cart actions
        cart_actions = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_actions.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(cart_actions, text="🗑️ Remove Item", command=self.remove_from_cart,
                      fg_color="#e74c3c", hover_color="#c0392b", height=35).pack(side="left", padx=5)
        ctk.CTkButton(cart_actions, text="🧹 Clear Cart", command=self.clear_cart,
                      fg_color="#f39c12", hover_color="#e67e22", height=35).pack(side="left", padx=5)

        # Customer info
        info_frame = ctk.CTkFrame(right_frame, fg_color=(
            "#e8f4fd", "#2d3047"), corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(info_frame, text="👤 Customer Name:",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.customer_entry = ctk.CTkEntry(info_frame, placeholder_text="Enter customer name",
                                           border_color="#3498db", corner_radius=8)
        self.customer_entry.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(info_frame, text="📝 Notes:",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.notes_entry = ctk.CTkEntry(info_frame, placeholder_text="Additional notes",
                                        border_color="#3498db", corner_radius=8)
        self.notes_entry.pack(pady=5, padx=10, fill="x")

        # Total display
        total_frame = ctk.CTkFrame(
            info_frame, fg_color="#2d3047", corner_radius=8)
        total_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = ctk.CTkLabel(total_frame, text="💰 TOTAL: ₱0.00",
                                        font=ctk.CTkFont(
                                            size=18, weight="bold"),
                                        text_color="#FFD700")
        self.total_label.pack(pady=12)

        # Process sale button
        process_btn = ctk.CTkButton(right_frame, text="✅ PROCESS SALE",
                                    command=self.process_sale,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    height=45, fg_color="#00b894", hover_color="#00a085",
                                    corner_radius=10)
        process_btn.pack(pady=10, padx=10, fill="x")

        # Initialize cart
        self.app.cart = []
        self.app.oop_cart.clear()

    def load_products_pos(self):
        try:
            products = self.app.inventory_manager.get_all_products()

            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)

            for product in products:
                if product.stock > 0:
                    self.pos_products_tree.insert("", "end", values=(
                        product.id,
                        product.name,
                        product.brand,
                        product.vehicle_model,
                        product.year_range,
                        f"₱{product.price:.2f}",
                        product.stock
                    ))

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not load products: {str(e)}")

    def search_products_pos(self, event=None):
        search_term = self.pos_search_entry.get()

        try:
            products = self.app.inventory_manager.search_products(search_term)

            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)

            if not products:
                self.pos_products_tree.insert("", "end", values=(
                    "", "There's no product in the inventory", "", "", "", "", ""
                ))
            else:
                for product in products:
                    if product.stock > 0:
                        self.pos_products_tree.insert("", "end", values=(
                            product.id,
                            product.name,
                            product.brand,
                            product.vehicle_model,
                            product.year_range,
                            f"₱{product.price:.2f}",
                            product.stock
                        ))

        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def add_to_cart(self, event):
        selection = self.pos_products_tree.selection()
        if not selection:
            return

        item = self.pos_products_tree.item(selection[0])
        product_data = item['values']

        if product_data[1] == "There's no product in the inventory":
            return

        price_str = product_data[5]
        price = float(price_str.replace('₱', '').replace(',', ''))

        self.app.oop_cart.add_item(product_data[0], product_data[1], price, 1)
        self.app.cart = self.app.oop_cart.to_legacy_format()
        self.update_cart_display()

    def remove_from_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            return

        item_index = self.cart_tree.index(selection[0])
        if 0 <= item_index < len(self.app.cart):
            product_id = self.app.cart[item_index]['id']
            self.app.oop_cart.remove_item(product_id)
            self.app.cart = self.app.oop_cart.to_legacy_format()
            self.update_cart_display()

    def clear_cart(self):
        self.app.cart = []
        self.app.oop_cart.clear()
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0
        for i, item in enumerate(self.app.cart):
            self.cart_tree.insert("", "end", values=(
                item['name'], item['qty'], f"₱{item['price']:.2f}", f"₱{item['subtotal']:.2f}"
            ))
            total += item['subtotal']

        self.total_label.configure(text=f"Total: ₱{total:.2f}")

    def process_sale(self):
        if not self.app.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return

        try:
            invoice_number = generate_invoice_number()
            customer_name = self.customer_entry.get() or "Walk-in Customer"
            notes = self.notes_entry.get()

            # Create Sale object
            sale = Sale(invoice_number, customer_name, notes)

            # Add items to sale and update inventory
            for cart_item in self.app.cart:
                sale.add_item(cart_item['name'],
                              cart_item['qty'], cart_item['subtotal'])
                self.app.inventory_manager.update_product_stock(
                    cart_item['id'], cart_item['qty'])

            # Record sale
            self.app.sales_manager.record_sale(sale)

            # Generate receipt
            self.generate_receipt(sale)

            messagebox.showinfo("Sale Completed",
                                f"Sale processed successfully!\nInvoice: {invoice_number}\nTotal: ₱{sale.total_amount:.2f}")

            # Clear cart and reload products
            self.clear_cart()
            self.customer_entry.delete(0, 'end')
            self.notes_entry.delete(0, 'end')
            self.load_products_pos()
            self.app.show_dashboard()

        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Could not process sale: {str(e)}")

    def generate_receipt(self, sale):
        # Receipt generation implementation would go here
        pass
