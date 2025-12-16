from utils import *
from database import Database
from gui_manager import GUIManager
from inventory_manager import InventoryManager
from sales_manager import SalesManager
from catalog_manager import CatalogManager
from pos_manager import ShoppingCart
from returns_manager import ReturnsManager
from trash_manager import TrashManager
# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================
class AutoPartsAdminSystem(AutoParts):
    """Main application class inheriting from AutoParts"""
    
    def __init__(self):
        super().__init__()
        self.root = ctk.CTk()
        self.root.title(APP_TITLE)
        self.root.geometry("1200x800")
        self.apply_theme(self.root)
        self.current_user = None
        self.cart = []
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.content_frame = None
        self.sidebar = None
        
        # Initialize managers
        self.gui = GUIManager(self)
        self.inventory = InventoryManager(self)
        self.sales = SalesManager(self)
        self.database = Database()
        self.catalog = CatalogManager(self.database)
        self.returns = ReturnsManager(self) 
        self.trash = TrashManager(self)
        # Auto-load catalogs into inventory if DB empty
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM inventory")
            count = cur.fetchone()[0]
            if count == 0:
                self.catalog.add_all_catalogs_to_inventory()
        except:
            pass

        
        self.setup_gui()
    
    def setup_gui(self):
        self.show_login_screen()
    
    def show_login_screen(self):
        self.clear_screen()
        
        # Create main container for login
        login_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        login_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Login box
        login_box = ctk.CTkFrame(login_frame, corner_radius=15, border_width=2, border_color="#FF6B35")
        login_box.pack(expand=True, padx=100, pady=100)
        
        # Title
        title_label = ctk.CTkLabel(
            login_box, 
            text="Auto Parts System", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FF6B35"
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            login_box,
            text="Login to continue",
            font=ctk.CTkFont(size=14),
            text_color="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username field
        username_frame = ctk.CTkFrame(login_box, fg_color="transparent")
        username_frame.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(
            username_frame, 
            text="Username:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.login_username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="Enter username",
            height=35,
            width=250
        )
        self.login_username_entry.pack(fill="x", pady=(0, 15))
        
        # Password field with show/hide toggle
        password_frame = ctk.CTkFrame(login_box, fg_color="transparent")
        password_frame.pack(fill="x", padx=40, pady=5)
        
        # Password label and show/hide button
        password_label_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        password_label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            password_label_frame, 
            text="Password:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left")
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        
        def toggle_password():
            if self.show_password_var.get():
                self.login_password_entry.configure(show="")
            else:
                self.login_password_entry.configure(show="•")
        
        show_password_check = ctk.CTkCheckBox(
            password_label_frame,
            text="Show",
            variable=self.show_password_var,
            command=toggle_password,
            width=60,
            font=ctk.CTkFont(size=11)
        )
        show_password_check.pack(side="right", padx=(0, 5))
        
        self.login_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter password",
            show="•",
            height=35,
            width=250
        )
        self.login_password_entry.pack(fill="x", pady=(5, 15))
        
        # Login button
        login_btn = ctk.CTkButton(
            login_box,
            text="Login",
            command=lambda: self.login(self.login_username_entry, self.login_password_entry),
            height=40,
            fg_color="#FF6B35",
            hover_color="#E55A30",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_btn.pack(pady=20, padx=40, fill="x")
        
        # Error message placeholder
        self.login_error_label = ctk.CTkLabel(
            login_box,
            text="",
            text_color="#e74c3c",
            font=ctk.CTkFont(size=11)
        )
        self.login_error_label.pack(pady=(5, 20))
        
        # Focus on username field
        self.login_username_entry.focus_set()
        
        # Bind Enter key to login
        def on_enter_key(event):
            self.login(self.login_username_entry, self.login_password_entry)
        
        self.login_password_entry.bind("<Return>", on_enter_key)
    
    def login(self, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()
        
        # Clear previous error
        self.login_error_label.configure(text="")
        
        # Simple validation
        if not username or not password:
            self.login_error_label.configure(text="Please enter both username and password")
            return
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ? AND password = ?",
                        (username, password))
            user = cur.fetchone()
            conn.close()
            if user:
                self.current_user = user
                self.show_main_dashboard()
            else:
                self.login_error_label.configure(text="Invalid username or password")
        except Exception as e:
            self.login_error_label.configure(text=f"Login failed: {str(e)}")
    def show_trash_bin(self):
        """Display trash bin with deleted products"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="TRASH BIN",
                                font=ctk.CTkFont(size=26, weight="bold"),
                                text_color="#FF6B35")
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(self.content_frame, 
                                text="Products moved here can be restored or permanently deleted.",
                                font=ctk.CTkFont(size=12),
                                text_color="#7f8c8d")
        info_label.pack(pady=5)
        
        trash_frame = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                corner_radius=15, border_width=2, border_color="#FF6B35")
        trash_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(trash_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(action_frame, text="Refresh", 
                                command=lambda: self.load_trash_items(),
                                width=100, height=35,
                                fg_color="#0984e3", hover_color="#0971c2",
                                font=ctk.CTkFont(size=12, weight="bold"))
        refresh_btn.pack(side="left", padx=5)
        
        # Restore selected button
        restore_btn = ctk.CTkButton(action_frame, text="Restore Selected", 
                                command=self.restore_from_trash,
                                width=120, height=35,
                                fg_color="#00b894", hover_color="#00a085",
                                font=ctk.CTkFont(size=12, weight="bold"))
        restore_btn.pack(side="left", padx=5)
        
        # Permanent delete button
        perm_delete_btn = ctk.CTkButton(action_frame, text="Delete Permanently", 
                                    command=self.permanent_delete_from_trash,
                                    width=120, height=35,
                                    fg_color="#e74c3c", hover_color="#c0392b",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        perm_delete_btn.pack(side="left", padx=5)
        
        # Empty trash button
        empty_trash_btn = ctk.CTkButton(action_frame, text="Empty Trash", 
                                    command=self.empty_trash_bin,
                                    width=100, height=35,
                                    fg_color="#f39c12", hover_color="#e67e22",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        empty_trash_btn.pack(side="left", padx=5)
        
        # Tree frame
        tree_frame = ctk.CTkFrame(trash_frame, fg_color=("#ffffff", "#4a4e69"),
                                corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("Trash ID", "Original ID", "Product Name", "Brand", "Price", 
                "Stock", "Category", "Deleted At", "Deleted By")
        
        self.trash_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
        
        column_config = {
            "Trash ID": ("Trash ID", 80),
            "Original ID": ("Orig ID", 70),
            "Product Name": ("Product Name", 200),
            "Brand": ("Brand", 100),
            "Price": ("Price", 80),
            "Stock": ("Stock", 60),
            "Category": ("Category", 120),
            "Deleted At": ("Deleted At", 150),
            "Deleted By": ("Deleted By", 100)
        }
        
        for col in columns:
            heading_text, width = column_config[col]
            self.trash_tree.heading(col, text=heading_text)
            self.trash_tree.column(col, width=width)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.trash_tree.yview)
        self.trash_tree.configure(yscrollcommand=scrollbar.set)
        self.trash_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Load trash items
        self.load_trash_items()

    def load_trash_items(self):
        """Load items from trash bin"""
        try:
            if not hasattr(self, 'trash_tree') or not self.trash_tree.winfo_exists():
                return
            
            # Clear existing items
            for item in self.trash_tree.get_children():
                self.trash_tree.delete(item)
            
            # Get items from trash
            trash_items = self.trash.get_trash_items()
            
            if not trash_items:
                self.trash_tree.insert("", "end", values=(
                    "", "", "Trash bin is empty", "", "", "", "", "", ""
                ))
            else:
                for item in trash_items:
                    self.trash_tree.insert("", "end", values=(
                        item[0],  # trash_id
                        item[1],  # original_id
                        item[2],  # name
                        item[7] or "Generic",  # brand
                        f"₱{item[3]:.2f}",  # price
                        item[4],  # stock
                        item[5] or "Auto Parts",  # category
                        item[12],  # deleted_at
                        item[13] or "System"  # deleted_by
                    ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not load trash items: {str(e)}")

    def restore_from_trash(self):
        """Restore selected item from trash"""
        if not hasattr(self, 'trash_tree') or not self.trash_tree.winfo_exists():
            return
        
        selection = self.trash_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to restore!")
            return
        
        item = self.trash_tree.item(selection[0])
        trash_id = item['values'][0]
        product_name = item['values'][2]
        
        if not trash_id:
            return
        
        result = messagebox.askyesno(
            "Confirm Restore",
            f"Are you sure you want to restore '{product_name}'?\n\n"
            f"The product will be moved back to inventory."
        )
        
        if not result:
            return
        
        try:
            success, message = self.trash.restore_item(trash_id)
            
            if success:
                messagebox.showinfo("Restored", message)
                self.load_trash_items()
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not restore item: {str(e)}")

    def permanent_delete_from_trash(self):
        """Permanently delete selected item from trash"""
        if not hasattr(self, 'trash_tree') or not self.trash_tree.winfo_exists():
            return
        
        selection = self.trash_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete permanently!")
            return
        
        item = self.trash_tree.item(selection[0])
        trash_id = item['values'][0]
        product_name = item['values'][2]
        
        if not trash_id:
            return
        
        result = messagebox.askyesno(
            "Confirm Permanent Delete",
            f"WARNING: This action cannot be undone!\n\n"
            f"Are you sure you want to permanently delete '{product_name}'?"
        )
        
        if not result:
            return
        
        try:
            success, message = self.trash.permanent_delete(trash_id)
            
            if success:
                messagebox.showinfo("Deleted", message)
                self.load_trash_items()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete item: {str(e)}")

    def empty_trash_bin(self):
        """Empty all items from trash bin"""
        result = messagebox.askyesno(
            "Empty Trash Bin",
            "WARNING: This will permanently delete ALL items in trash!\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?"
        )
        
        if not result:
            return
        
        try:
            success, message = self.trash.empty_trash()
            
            if success:
                messagebox.showinfo("Trash Emptied", message)
                self.load_trash_items()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not empty trash: {str(e)}")
    def show_main_dashboard(self):
        self.clear_screen()
        self.sidebar = self.gui.create_sidebar()
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.show_dashboard()
    
    def show_dashboard(self):
        """Display the main dashboard"""
        self.clear_content()
        # Header
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=20)
        title_label = ctk.CTkLabel(header_frame, text="DASHBOARD OVERVIEW",
                                   font=ctk.CTkFont(size=28, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(side="left")
        refresh_btn = ctk.CTkButton(header_frame, text="Refresh",
                                    command=self.show_dashboard,
                                    width=120, height=35,
                                    fg_color="#2d3047", hover_color="#FF6B35",
                                    corner_radius=8)
        refresh_btn.pack(side="right", padx=10)
        # Load dashboard data
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load and display dashboard data"""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get inventory counts
            cur.execute("SELECT COUNT(*) FROM inventory")
            total_products = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM inventory WHERE stock < 10")
            low_stock = cur.fetchone()[0]
            
            # Get today's sales (excluding returns)
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            cur.execute(
                "SELECT COUNT(DISTINCT invoice), SUM(subtotal) FROM sales WHERE date LIKE ? AND status != 'RETURNED' AND subtotal > 0", 
                (f"{today}%",))
            today_sales_data = cur.fetchone()
            today_sales_count = today_sales_data[0] or 0
            today_sales_total = today_sales_data[1] or 0.0
            
            # Get today's returns
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT invoice) as return_count,
                    ABS(SUM(subtotal)) as return_amount
                FROM sales 
                WHERE status = 'RETURNED' 
                AND date LIKE ?
                AND subtotal < 0
            """, (f"{today}%",))
            
            today_returns_data = cur.fetchone()
            today_returns_count = today_returns_data[0] or 0
            today_returns_total = today_returns_data[1] or 0.0
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load dashboard data: {str(e)}")
            return
        
        # Metrics Cards
        metrics_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=20, pady=20)
        
        metrics_data = [
            {"title": "TOTAL PRODUCTS", "value": total_products, "color": "#0984e3"},
            {"title": "LOW STOCK ITEMS", "value": low_stock, "color": "#e74c3c"},
            {"title": "TODAY'S SALES", "value": today_sales_count, "color": "#00b894"},
            {"title": "TODAY'S REVENUE", "value": f"₱{today_sales_total:,.2f}", "color": "#f39c12"},
            {"title": "TODAY'S RETURNS", "value": today_returns_count, "color": "#6c5ce7"},
            {"title": "RETURN AMOUNT", "value": f"₱{today_returns_total:,.2f}", "color": "#e17055"}
        ]
        
        for i, metric in enumerate(metrics_data):
            metric_card = ctk.CTkFrame(
                metrics_frame, fg_color=metric["color"], corner_radius=15)
            metric_card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            icon_frame = ctk.CTkFrame(metric_card, fg_color="transparent")
            icon_frame.pack(pady=(15, 5))
            
            ctk.CTkLabel(icon_frame, text="", font=ctk.CTkFont(
                size=20)).pack(side="left", padx=(0, 5))
            
            ctk.CTkLabel(icon_frame, text=metric["title"], font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="white").pack(side="left")
            
            ctk.CTkLabel(metric_card, text=str(metric["value"]),
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color="white").pack(pady=(5, 15))
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                     corner_radius=15, border_width=2, border_color="#FF6B35")
        actions_frame.pack(fill="x", padx=20, pady=20)
        
        actions_header = ctk.CTkFrame(
            actions_frame, fg_color="#FF6B35", corner_radius=10)
        actions_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(actions_header, text="QUICK ACTIONS",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(pady=8)
        
        action_buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        action_buttons_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        action_buttons = [
            {"text": "ADD NEW PRODUCT", "command": self.show_add_product_dialog, "color": "#00b894"},
            {"text": "PROCESS SALE", "command": self.show_pos, "color": "#0984e3"},
            {"text": "PROCESS RETURN", "command": self.show_returns, "color": "#6c5ce7"},
            {"text": "GENERATE REPORT", "command": self.generate_report, "color": "#f39c12"}
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
    
    def show_add_product_dialog(self):
        """Show dialog to add new product"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Product")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="#FF6B35", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="ADD NEW PRODUCT", 
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(pady=15)
        
        form_container = ctk.CTkScrollableFrame(main_frame, height=400)
        form_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        fields = [
            ("Product Name", "entry", True),
            ("Price (₱)", "entry", True),
            ("Stock Quantity", "entry", True),
            ("Category", "entry", False),
            ("Brand", "entry", False),
            ("Vehicle Model", "entry", False),
            ("Year Range", "entry", False),
            ("Part Category", "entry", False),
            ("Part Subcategory", "entry", False)
        ]
        
        entries = {}
        for label_text, field_type, required in fields:
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)
            
            label_text_display = label_text
            if required:
                label_text_display += " *"
            
            ctk.CTkLabel(field_frame, text=label_text_display,
                         font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
            
            if field_type == "entry":
                entry = ctk.CTkEntry(field_frame, height=40, 
                                    placeholder_text=f"Enter {label_text.lower()}",
                                    font=ctk.CTkFont(size=13))
                entry.pack(fill="x", pady=(0, 5))
                
                # Set default values
                if label_text == "Category":
                    entry.insert(0, "Auto Parts")
                elif label_text == "Brand":
                    entry.insert(0, "Generic")
                elif label_text == "Vehicle Model":
                    entry.insert(0, "Universal")
                elif label_text == "Year Range":
                    entry.insert(0, "2020-2024")
                elif label_text == "Part Category":
                    entry.insert(0, "General")
                elif label_text == "Part Subcategory":
                    entry.insert(0, "General")
                
                entries[label_text] = entry
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        def save_product():
            try:
                # Validate required fields
                required_fields = {
                    "Product Name": "Product name",
                    "Price (₱)": "Price",
                    "Stock Quantity": "Stock quantity"
                }
                
                for field_label, field_name in required_fields.items():
                    if not entries[field_label].get().strip():
                        messagebox.showerror("Error", f"{field_name} is required!")
                        return
                
                # Validate numeric fields
                try:
                    price = float(entries["Price (₱)"].get())
                    if price <= 0:
                        messagebox.showerror("Error", "Price must be greater than 0!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid price!")
                    return
                
                try:
                    stock = int(entries["Stock Quantity"].get())
                    if stock < 0:
                        messagebox.showerror("Error", "Stock cannot be negative!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid stock quantity!")
                    return
                
                conn = self.database.get_db()
                cur = conn.cursor()
                
                cur.execute("""INSERT INTO inventory 
                            (name, price, stock, category, brand, vehicle_model, 
                             year_range, part_category, part_subcategory) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                entries["Product Name"].get(),
                                price,
                                stock,
                                entries["Category"].get(),
                                entries["Brand"].get(),
                                entries["Vehicle Model"].get(),
                                entries["Year Range"].get(),
                                entries["Part Category"].get(),
                                entries["Part Subcategory"].get()
                            ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Product added successfully!")
                dialog.destroy()
                
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not add product: {str(e)}")
        
        def cancel():
            dialog.destroy()
        
        ctk.CTkButton(button_frame, text="Save Product", 
                      command=save_product,
                      height=45, fg_color="#00b894", hover_color="#00a085",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(button_frame, text="Cancel", 
                      command=cancel,
                      height=45, fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="right", padx=5, fill="x", expand=True)
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def generate_report(self):
        """Generate sales report"""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            report = "=== AUTO PARTS SALES REPORT ===\n\n"
            report += f"Generated on: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            report += "SALES SUMMARY:\n"
            report += "=" * 50 + "\n"
            
            # Get all sales excluding returns
            cur.execute("SELECT * FROM sales WHERE status != 'RETURNED' AND subtotal > 0 ORDER BY date DESC")
            sales = cur.fetchall()
            
            # Get distinct invoices for sales
            cur.execute("SELECT COUNT(DISTINCT invoice), SUM(subtotal) FROM sales WHERE status != 'RETURNED' AND subtotal > 0")
            sales_summary = cur.fetchone()
            total_sales_transactions = sales_summary[0] or 0
            total_sales_amount = sales_summary[1] or 0.0
            
            # Get returns summary
            cur.execute("SELECT COUNT(DISTINCT invoice), ABS(SUM(subtotal)) FROM sales WHERE status = 'RETURNED' AND subtotal < 0")
            returns_summary = cur.fetchone()
            total_returns = returns_summary[0] or 0
            total_returns_amount = returns_summary[1] or 0.0
            
            report += f"Total Sales Transactions: {total_sales_transactions}\n"
            report += f"Total Sales Amount: ₱{total_sales_amount:.2f}\n"
            
            if total_sales_transactions > 0:
                avg_sale = total_sales_amount / total_sales_transactions
                report += f"Average Sale: ₱{avg_sale:.2f}\n\n"
            
            report += f"Total Return Transactions: {total_returns}\n"
            report += f"Total Return Amount: ₱{total_returns_amount:.2f}\n"
            report += f"Net Revenue: ₱{total_sales_amount - total_returns_amount:.2f}\n\n"
            
            # Get top products
            product_sales = {}
            for sale in sales:
                product = sale[2]
                qty = sale[3]
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
            
            cur.execute("SELECT COUNT(*) FROM inventory")
            total_products = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM inventory WHERE stock < 10")
            low_stock = cur.fetchone()[0]
            
            cur.execute("SELECT price, stock FROM inventory")
            inventory_data = cur.fetchall()
            total_value = sum(price * stock for price, stock in inventory_data)
            
            report += f"Total Products: {total_products}\n"
            report += f"Low Stock Items: {low_stock}\n"
            report += f"Total Inventory Value: ₱{total_value:.2f}\n"
            
            conn.close()
            
            report_dialog = ctk.CTkToplevel(self.root)
            report_dialog.title("Sales Report")
            report_dialog.geometry("600x500")
            report_dialog.transient(self.root)
            report_dialog.grab_set()
            
            report_text = ctk.CTkTextbox(report_dialog, width=580, height=450)
            report_text.pack(padx=10, pady=10)
            report_text.insert("1.0", report)
            report_text.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate report: {str(e)}")
    
    def show_inventory(self):
        """Display inventory management screen"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="Inventory Management",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color=("#FF6B35", "#FF6B35"))
        title_label.pack(pady=20)
        
        search_frame = ctk.CTkFrame(
            self.content_frame, corner_radius=15, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(
            weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(search_frame, width=200, height=35, placeholder_text="Search products...",
                                         border_color=("#FF6B35", "#FF9A3D"))
        self.search_entry.grid(row=0, column=1, padx=5, pady=10)
        
        buttons = [
            ("Search", lambda: self.inventory.search_inventory(), 2, "#FF6B35", "#E55A30"),
            ("Refresh", lambda: self.inventory.load_inventory(), 3, "#0984e3", "#0971c2"),
            ("Add Product", self.show_add_product_dialog, 4, "#00b894", "#00a085"),
            ("Delete", lambda: self.inventory.delete_selected_product(), 5, "#e74c3c", "#c0392b"),
        ]
        
        for text, command, col, fg_color, hover_color in buttons:
            btn = ctk.CTkButton(search_frame, text=text, command=command, height=35,
                                fg_color=fg_color, hover_color=hover_color,
                                font=ctk.CTkFont(size=12, weight="bold"))
            btn.grid(row=0, column=col, padx=5, pady=10)
        
        table_frame = ctk.CTkFrame(
            self.content_frame, corner_radius=15, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ID", "Name", "Price", "Stock", "Category",
                   "Brand", "Vehicle Model", "Year Range")
        self.inventory_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=20)
        
        column_config = {
            "ID": ("ID", 60),
            "Name": ("Name", 150),
            "Price": ("Price", 80),
            "Stock": ("Stock", 60),
            "Category": ("Category", 120),
            "Brand": ("Brand", 100),
            "Vehicle Model": ("Model", 120),
            "Year Range": ("Years", 100)
        }
        
        for col in columns:
            heading_text, width = column_config[col]
            self.inventory_tree.heading(col, text=heading_text)
            self.inventory_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        self.inventory_tree.pack(
            side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.inventory.load_inventory()
        self.inventory_tree.bind("<Double-1>", lambda e: self.edit_inventory_item(e))
    
    def edit_inventory_item(self, event):
        """Edit selected inventory item"""
        if not hasattr(self, 'inventory_tree') or not self.inventory_tree.winfo_exists():
            return
        
        selection = self.inventory_tree.selection()
        if not selection:
            return
        
        item = self.inventory_tree.item(selection[0])
        item_data = item['values']
        
        if not item_data[0]:
            return
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory WHERE id = ?", (item_data[0],))
            product_data = cur.fetchone()
            conn.close()
            
            if not product_data:
                messagebox.showerror("Error", "Product not found in database!")
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load product details: {str(e)}")
            return
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Product")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="#0984e3", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="EDIT PRODUCT", 
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").pack(pady=15)
        
        ctk.CTkLabel(header_frame, text=f"ID: {product_data[0]}",
                     font=ctk.CTkFont(size=12),
                     text_color="white").pack(pady=(0, 10))
        
        form_container = ctk.CTkScrollableFrame(main_frame, height=350)
        form_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        fields = [
            ("Product Name", "entry", product_data[1]),
            ("Price (₱)", "entry", f"{product_data[2]:.2f}"),
            ("Stock Quantity", "entry", str(product_data[3])),
            ("Category", "entry", product_data[4] or "Auto Parts"),
            ("Brand", "entry", product_data[6] or "Generic"),
            ("Vehicle Model", "entry", product_data[7] or "Universal"),
            ("Year Range", "entry", product_data[8] or "2020-2024"),
            ("Part Category", "entry", product_data[9] or "General"),
            ("Part Subcategory", "entry", product_data[10] or "General")
        ]
        
        entries = {}
        for label_text, field_type, default_value in fields:
            field_frame = ctk.CTkFrame(form_container, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(field_frame, text=label_text,
                         font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 5))
            
            if field_type == "entry":
                entry = ctk.CTkEntry(field_frame, height=40, 
                                    font=ctk.CTkFont(size=13))
                entry.insert(0, str(default_value))
                entry.pack(fill="x", pady=(0, 5))
                entries[label_text] = entry
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        def update_product():
            try:
                required_fields = {
                    "Product Name": "Product name",
                    "Price (₱)": "Price",
                    "Stock Quantity": "Stock quantity"
                }
                
                for field_label, field_name in required_fields.items():
                    if not entries[field_label].get().strip():
                        messagebox.showerror("Error", f"{field_name} is required!")
                        return
                
                try:
                    price = float(entries["Price (₱)"].get())
                    if price <= 0:
                        messagebox.showerror("Error", "Price must be greater than 0!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid price!")
                    return
                
                try:
                    stock = int(entries["Stock Quantity"].get())
                    if stock < 0:
                        messagebox.showerror("Error", "Stock cannot be negative!")
                        return
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid stock quantity!")
                    return
                
                conn = self.database.get_db()
                cur = conn.cursor()
                
                cur.execute("""UPDATE inventory 
                            SET name=?, price=?, stock=?, category=?, brand=?, 
                                vehicle_model=?, year_range=?, part_category=?, part_subcategory=?
                            WHERE id=?""",
                            (
                                entries["Product Name"].get(),
                                price,
                                stock,
                                entries["Category"].get(),
                                entries["Brand"].get(),
                                entries["Vehicle Model"].get(),
                                entries["Year Range"].get(),
                                entries["Part Category"].get(),
                                entries["Part Subcategory"].get(),
                                product_data[0]
                            ))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Product updated successfully!")
                dialog.destroy()
                
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not update product: {str(e)}")
        
        def delete_product():
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete '{product_data[1]}'?\nThis action cannot be undone!"
            )
            
            if result:
                try:
                    conn = self.database.get_db()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM inventory WHERE id = ?", (product_data[0],))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", "Product deleted successfully!")
                    dialog.destroy()
                    
                    if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                        self.inventory.load_inventory()
                    
                    if hasattr(self, 'content_frame'):
                        self.show_dashboard()
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete product: {str(e)}")
        
        ctk.CTkButton(button_frame, text="Save Changes", 
                      command=update_product,
                      height=45, fg_color="#00b894", hover_color="#00a085",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(button_frame, text="Delete", 
                      command=delete_product,
                      height=45, fg_color="#e74c3c", hover_color="#c0392b",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(button_frame, text="Cancel", 
                      command=dialog.destroy,
                      height=45, fg_color="#95a5a6", hover_color="#7f8c8d",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="right", padx=5, fill="x", expand=True)
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_pos(self):
        """Display Point of Sale screen"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="POINT OF SALE",
                                font=ctk.CTkFont(size=26, weight="bold"),
                                text_color="#FF6B35")
        title_label.pack(pady=20)
        
        pos_frame = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                corner_radius=15, border_width=2, border_color="#FF6B35")
        pos_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        products_header = ctk.CTkFrame(
            left_frame, fg_color="#FF6B35", corner_radius=10)
        products_header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(products_header, text="PRODUCT CATALOG", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white").pack(pady=8)
        
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        # Create a sub-frame for search controls to ensure proper layout
        search_controls_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_controls_frame.pack(fill="x")
        
        # Create a grid layout for better control
        search_controls_frame.grid_columnconfigure(0, weight=1)  # Search field column
        search_controls_frame.grid_columnconfigure(1, weight=0)  # Filter button column
        
        # Search label and entry - using grid
        search_label_frame = ctk.CTkFrame(search_controls_frame, fg_color="transparent")
        search_label_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_label_frame.grid_columnconfigure(0, weight=0)  # Label
        search_label_frame.grid_columnconfigure(1, weight=1)  # Entry
        
        ctk.CTkLabel(search_label_frame, text="Search:", font=ctk.CTkFont(
            weight="bold")).grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        self.pos_search_entry = ctk.CTkEntry(search_label_frame, height=35,
                                            placeholder_text="Type to search products...",
                                            border_color="#FF6B35", corner_radius=8)
        self.pos_search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.pos_search_entry.bind("<KeyRelease>", lambda e: self.search_products_pos(e))
        
        # Catalog filter button - FIXED: Using grid layout for proper positioning
        self.catalog_filter_btn = ctk.CTkButton(search_controls_frame, text="Filter by Brand",
                                            command=self.show_catalog_filter,
                                            width=150, height=35,
                                            fg_color="#0984e3", hover_color="#0971c2",
                                            font=ctk.CTkFont(size=12, weight="bold"))
        self.catalog_filter_btn.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        
        tree_frame = ctk.CTkFrame(left_frame, fg_color=(
            "#ffffff", "#4a4e69"), corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.pos_products_tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Brand", "Model", "Years", "Price", "Stock"),
                                            show="headings", height=15)
        
        columns = {
            "ID": ("ID", 60),
            "Name": ("Product Name", 180),
            "Brand": ("Brand", 80),
            "Model": ("Model", 100),
            "Years": ("Years", 80),
            "Price": ("Price", 80),
            "Stock": ("Stock", 60)
        }
        
        for col, (text, width) in columns.items():
            self.pos_products_tree.heading(col, text=text)
            self.pos_products_tree.column(col, width=width)
        
        self.pos_products_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.pos_products_tree.bind("<Double-1>", lambda e: self.add_to_cart(e))
        
        right_frame = ctk.CTkFrame(pos_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", padx=10, pady=10)
        
        cart_header = ctk.CTkFrame(
            right_frame, fg_color="#00b894", corner_radius=10)
        cart_header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(cart_header, text="SHOPPING CART", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="white").pack(pady=8)
        
        cart_tree_frame = ctk.CTkFrame(right_frame, fg_color=(
            "#ffffff", "#4a4e69"), corner_radius=10)
        cart_tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.cart_tree = ttk.Treeview(cart_tree_frame, columns=("Product", "Qty", "Price", "Subtotal"),
                                    show="headings", height=10)
        
        cart_columns = {
            "Product": ("Product", 150),
            "Qty": ("Qty", 60),
            "Price": ("Price", 80),
            "Subtotal": ("Subtotal", 100)
        }
        
        for col, (text, width) in cart_columns.items():
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, width=width)
        
        self.cart_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        cart_actions = ctk.CTkFrame(right_frame, fg_color="transparent")
        cart_actions.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(cart_actions, text="Remove Item", command=self.remove_from_cart,
                    fg_color="#e74c3c", hover_color="#c0392b", height=35).pack(side="left", padx=5)
        ctk.CTkButton(cart_actions, text="Clear Cart", command=self.clear_cart,
                    fg_color="#f39c12", hover_color="#e67e22", height=35).pack(side="left", padx=5)
        
        info_frame = ctk.CTkFrame(right_frame, fg_color=(
            "#e8f4fd", "#2d3047"), corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_frame, text="Customer Name:",
                    font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.customer_entry = ctk.CTkEntry(info_frame, placeholder_text="Enter customer name",
                                        border_color="#3498db", corner_radius=8)
        self.customer_entry.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(info_frame, text="Notes:",
                    font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.notes_entry = ctk.CTkEntry(info_frame, placeholder_text="Additional notes",
                                        border_color="#3498db", corner_radius=8)
        self.notes_entry.pack(pady=5, padx=10, fill="x")
        
        total_frame = ctk.CTkFrame(
            info_frame, fg_color="#2d3047", corner_radius=8)
        total_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_label = ctk.CTkLabel(total_frame, text="TOTAL: ₱0.00",
                                        font=ctk.CTkFont(size=18, weight="bold"),
                                        text_color="#FFD700")
        self.total_label.pack(pady=12)
        
        process_btn = ctk.CTkButton(right_frame, text="PROCESS SALE",
                                    command=self.sales.process_sale,
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                    height=45, fg_color="#00b894", hover_color="#00a085",
                                    corner_radius=10)
        process_btn.pack(pady=10, padx=10, fill="x")
        
        self.cart = []
        self.current_filter = {"brand": None}
        self.load_products_pos()
    
    def load_products_pos(self):
        """Load products for POS with optional filter"""
        try:
            if not hasattr(self, 'pos_products_tree') or not self.pos_products_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            query = "SELECT * FROM inventory WHERE stock > 0"
            params = []
            
            if self.current_filter["brand"]:
                query += " AND brand = ?"
                params.append(self.current_filter["brand"])
            
            cur.execute(query, params)
            products = cur.fetchall()
            
            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)
            
            if not products:
                self.pos_products_tree.insert("", "end", values=(
                    "", "No products found with current filter", "", "", "", "", ""
                ))
            else:
                for product in products:
                    if product[3] > 0:
                        self.pos_products_tree.insert("", "end", values=(
                            product[0],
                            product[1],
                            product[6] or "Generic",
                            product[7] or "Universal",
                            product[8] or "Not Specified",
                            f"₱{product[2]:.2f}",
                            product[3]
                        ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load products: {str(e)}")
    
    def search_products_pos(self, event=None):
        """Search products in POS with current filter applied"""
        search_term = self.pos_search_entry.get()
        
        try:
            if not hasattr(self, 'pos_products_tree') or not self.pos_products_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            query = "SELECT * FROM inventory WHERE stock > 0"
            params = []
            
            if self.current_filter["brand"]:
                query += " AND brand = ?"
                params.append(self.current_filter["brand"])
            
            if search_term:
                query += " AND (name LIKE ? OR brand LIKE ? OR vehicle_model LIKE ?)"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param])
            
            cur.execute(query, params)
            products = cur.fetchall()
            
            for item in self.pos_products_tree.get_children():
                self.pos_products_tree.delete(item)
            
            if not products:
                self.pos_products_tree.insert("", "end", values=(
                    "", "No products found", "", "", "", "", ""
                ))
            else:
                for product in products:
                    if product[3] > 0:
                        self.pos_products_tree.insert("", "end", values=(
                            product[0],
                            product[1],
                            product[6] or "Generic",
                            product[7] or "Universal",
                            product[8] or "Not Specified",
                            f"₱{product[2]:.2f}",
                            product[3]
                        ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")
    
    def show_catalog_filter(self):
        """Show catalog filter dialog with instant filtering"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Filter by Brand")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        main_frame = ctk.CTkFrame(dialog, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="#0984e3", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="FILTER BY BRAND", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="white").pack(pady=15)
        
        form_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get all brands that have products in stock
            cur.execute("""
                SELECT DISTINCT brand 
                FROM inventory 
                WHERE brand IS NOT NULL 
                AND brand != '' 
                AND stock > 0
                ORDER BY brand
            """)
            
            brand_rows = cur.fetchall()
            brands = [row[0] for row in brand_rows]
            
            conn.close()
            
            if not brands:
                # If no brands found, show a message
                no_brands_label = ctk.CTkLabel(
                    form_container, 
                    text="No brands found in inventory.\nAdd products first.",
                    font=ctk.CTkFont(size=12),
                    text_color="#e74c3c"
                )
                no_brands_label.pack(pady=20)
                
                # Add a close button
                close_btn = ctk.CTkButton(
                    form_container,
                    text="Close",
                    command=dialog.destroy,
                    height=40,
                    fg_color="#95a5a6",
                    hover_color="#7f8c8d"
                )
                close_btn.pack(pady=10)
                
                # Center and return
                dialog.update_idletasks()
                width = dialog.winfo_width()
                height = dialog.winfo_height()
                x = (dialog.winfo_screenwidth() // 2) - (width // 2)
                y = (dialog.winfo_screenheight() // 2) - (height // 2)
                dialog.geometry(f'{width}x{height}+{x}+{y}')
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not load brands: {str(e)}")
            dialog.destroy()
            return
        
        brand_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        brand_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(brand_frame, text="Select Brand:",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))
        
        # Create a variable to hold the selected brand
        brand_var = ctk.StringVar(value="All Brands")
        
        def on_brand_selected(choice):
            """Apply filter immediately when brand is selected"""
            brand = brand_var.get()
            
            # Apply the filter immediately
            if brand == "All Brands":
                self.current_filter["brand"] = None
                self.catalog_filter_btn.configure(text="Filter by Brand")
            else:
                self.current_filter["brand"] = brand
                self.catalog_filter_btn.configure(text=f"Brand: {brand}")
            
            # Apply the filter
            self.load_products_pos()
            
            # Optionally close the dialog after selection
            dialog.destroy()
        
        # Create combobox with command that triggers on selection
        brand_combo = ctk.CTkComboBox(brand_frame, 
                                    values=["All Brands"] + brands,
                                    variable=brand_var,
                                    width=300, height=40,
                                    font=ctk.CTkFont(size=13),
                                    border_color="#3498db",
                                    corner_radius=8,
                                    command=on_brand_selected)  # This will call the function when selection changes
        
        brand_combo.pack(fill="x", pady=(0, 10))
        
        # Info label
        info_label = ctk.CTkLabel(
            form_container,
            text="Select a brand to filter products immediately",
            font=ctk.CTkFont(size=11),
            text_color="#7f8c8d"
        )
        info_label.pack(pady=5)
        
        # Clear filter button (optional)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)
        
        def clear_filter():
            self.current_filter["brand"] = None
            self.catalog_filter_btn.configure(text="Filter by Brand")
            self.load_products_pos()
            dialog.destroy()
        
        def apply_current_filter():
            """Manually apply the current selection"""
            brand = brand_var.get()
            if brand == "All Brands":
                clear_filter()
            else:
                on_brand_selected(brand)
        
        # Use a grid for buttons to make them side by side
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        ctk.CTkButton(button_frame, text="Clear Filter", 
                    command=clear_filter,
                    height=40, fg_color="#f39c12", hover_color="#e67e22",
                    font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, padx=5, sticky="ew")
        
        ctk.CTkButton(button_frame, text="Apply", 
                    command=apply_current_filter,
                    height=40, fg_color="#00b894", hover_color="#00a085",
                    font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, padx=5, sticky="ew")
        
        ctk.CTkButton(button_frame, text="Cancel", 
                    command=dialog.destroy,
                    height=40, fg_color="#95a5a6", hover_color="#7f8c8d",
                    font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=2, padx=5, sticky="ew")
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Focus on the combobox
        brand_combo.focus()
    
    def add_to_cart(self, event=None):
        """Add product to cart"""
        if not hasattr(self, 'pos_products_tree') or not self.pos_products_tree.winfo_exists():
            return
        
        selection = self.pos_products_tree.selection()
        if not selection:
            return
        
        item = self.pos_products_tree.item(selection[0])
        product_data = item['values']
        
        if not product_data[0] or product_data[1] == "No products found" or product_data[1] == "No products found with current filter":
            return
        
        price_str = product_data[5]
        price = float(price_str.replace('₱', '').replace(',', ''))
        
        # Simple cart addition
        found = False
        for cart_item in self.cart:
            if cart_item['id'] == product_data[0]:
                cart_item['qty'] += 1
                cart_item['subtotal'] = cart_item['price'] * cart_item['qty']
                found = True
                break
        
        if not found:
            self.cart.append({
                'id': product_data[0],
                'name': product_data[1],
                'price': price,
                'qty': 1,
                'subtotal': price
            })
        
        self.update_cart_display()
    
    def remove_from_cart(self):
        """Remove item from cart"""
        if not hasattr(self, 'cart_tree') or not self.cart_tree.winfo_exists():
            return
        
        selection = self.cart_tree.selection()
        if not selection:
            return
        
        item_index = self.cart_tree.index(selection[0])
        if 0 <= item_index < len(self.cart):
            del self.cart[item_index]
            self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart = []
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display"""
        if not hasattr(self, 'cart_tree') or not self.cart_tree.winfo_exists():
            return
        
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        total = 0
        for i, item in enumerate(self.cart):
            self.cart_tree.insert("", "end", values=(
                item['name'], item['qty'], f"₱{item['price']:.2f}", f"₱{item['subtotal']:.2f}"
            ))
            total += item['subtotal']
        
        self.total_label.configure(text=f"Total: ₱{total:.2f}")
    
    def show_sales_history(self):
        """Display sales history screen - FIXED for return reasons"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="SALES HISTORY",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(pady=20)
        
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                    corner_radius=15, border_width=2, border_color="#FF6B35")
        filter_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=12)
        
        self.sales_status_var = ctk.StringVar(value="All")
        status_combo = ctk.CTkComboBox(filter_frame, 
                                       values=["All", "COMPLETED", "RETURNED"],
                                       variable=self.sales_status_var,
                                       width=120, height=35,
                                       border_color="#3498db", corner_radius=8)
        status_combo.grid(row=0, column=1, padx=5, pady=12)
        
        ctk.CTkLabel(filter_frame, text="Date:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=2, padx=10, pady=12)
        
        self.sales_date_entry = ctk.CTkEntry(
            filter_frame, placeholder_text="YYYY-MM-DD", width=120, height=35,
            border_color="#3498db", corner_radius=8)
        self.sales_date_entry.grid(row=0, column=3, padx=5, pady=12)
        
        ctk.CTkLabel(filter_frame, text="Invoice:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=4, padx=10, pady=12)
        
        self.invoice_entry = ctk.CTkEntry(filter_frame, width=150, height=35,
                                          border_color="#3498db", corner_radius=8)
        self.invoice_entry.grid(row=0, column=5, padx=5, pady=12)
        
        search_btn = ctk.CTkButton(
            filter_frame, text="Search", command=self.search_sales,
            fg_color="#0984e3", hover_color="#0971c2", height=35, width=100)
        search_btn.grid(row=0, column=6, padx=8, pady=12)
        
        refresh_btn = ctk.CTkButton(
            filter_frame, text="Refresh", command=self.load_sales_history,
            fg_color="#00b894", hover_color="#00a085", height=35, width=100)
        refresh_btn.grid(row=0, column=7, padx=8, pady=12)
        
        clear_btn = ctk.CTkButton(
            filter_frame, text="Clear History",
            command=self.clear_sales_history,
            fg_color="#e74c3c", hover_color="#c0392b", height=35, width=120
        )
        clear_btn.grid(row=0, column=8, padx=8, pady=12)
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color=("#ffffff", "#4a4e69"),
                                   corner_radius=15, border_width=2, border_color="#FF6B35")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        columns = {
            "ID": ("ID", 60),
            "Invoice": ("Invoice", 120),
            "Item": ("Item", 150),
            "Qty": ("Qty", 100),
            "Subtotal": ("Subtotal", 100),
            "Date": ("Date", 120),
            "Customer": ("Customer", 120),
            "Status": ("Status", 120),
            "Return Reason": ("Return Reason", 150)
        }
        
        self.sales_tree = ttk.Treeview(
            table_frame, columns=list(columns.keys()), show="headings", height=20)
        
        for col, (heading, width) in columns.items():
            self.sales_tree.heading(col, text=heading)
            self.sales_tree.column(col, width=width)
        
        # Configure tags for different statuses
        self.sales_tree.tag_configure('returned', background='#ffebee', foreground='#c62828')
        self.sales_tree.tag_configure('completed', background='#e8f5e9', foreground='#2e7d32')
        self.sales_tree.tag_configure('partial', background='#fff3cd', foreground='#856404')
        
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        self.sales_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.load_sales_history()
    
    def load_sales_history(self):
        """Load sales history data - FIXED to show return reasons"""
        try:
            if not hasattr(self, 'sales_tree') or not self.sales_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Query to get all sales but exclude return entries that are linked to original sales
            # Also get return reason from the return records if exists
            cur.execute("""
                SELECT 
                    s.id,
                    s.invoice,
                    s.item,
                    s.qty,
                    s.subtotal,
                    s.date,
                    s.customer_name,
                    s.status,
                    s.returned_qty,
                    COALESCE(
                        (SELECT r.return_reason 
                         FROM sales r 
                         WHERE r.original_sale_id = s.id 
                         AND r.status = 'RETURNED'
                         AND r.return_reason IS NOT NULL
                         AND r.return_reason != ''
                         LIMIT 1),
                        s.return_reason,
                        'N/A'
                    ) as display_return_reason
                FROM sales s 
                WHERE (s.original_sale_id IS NULL OR s.original_sale_id = '')
                ORDER BY s.date DESC
            """)
            
            sales = cur.fetchall()
            
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            for sale in sales:
                status = sale[7] if sale[7] else "COMPLETED"
                returned_qty = sale[8] or 0
                return_reason = sale[9] or "N/A"
                
                # Determine status text
                if status == "RETURNED":
                    status_text = "FULLY RETURNED"
                elif returned_qty > 0:
                    status_text = f"PARTIALLY RETURNED ({returned_qty} of {sale[3]})"
                else:
                    status_text = "COMPLETED"
                
                tag = 'returned' if status == "RETURNED" else ('completed' if returned_qty == 0 else 'partial')
                
                self.sales_tree.insert("", "end", values=(
                    sale[0],
                    sale[1],
                    sale[2],
                    f"{sale[3]} (Returned: {returned_qty})",
                    f"₱{sale[4]:.2f}",
                    sale[5],
                    sale[6] or "Walk-in",
                    status_text,
                    return_reason  # This shows the return reason
                ), tags=(tag,))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load sales history: {str(e)}")
    
    def search_sales(self):
        """Search sales history - FIXED to handle return reasons"""
        date = self.sales_date_entry.get()
        invoice = self.invoice_entry.get()
        status_filter = self.sales_status_var.get()
        
        try:
            if not hasattr(self, 'sales_tree') or not self.sales_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    s.id,
                    s.invoice,
                    s.item,
                    s.qty,
                    s.subtotal,
                    s.date,
                    s.customer_name,
                    s.status,
                    s.returned_qty,
                    COALESCE(
                        (SELECT r.return_reason 
                         FROM sales r 
                         WHERE r.original_sale_id = s.id 
                         AND r.status = 'RETURNED'
                         AND r.return_reason IS NOT NULL
                         AND r.return_reason != ''
                         LIMIT 1),
                        s.return_reason,
                        'N/A'
                    ) as display_return_reason
                FROM sales s 
                WHERE (s.original_sale_id IS NULL OR s.original_sale_id = '')
            """
            
            params = []
            
            if status_filter != "All":
                if status_filter == "RETURNED":
                    query += " AND s.status = 'RETURNED'"
                elif status_filter == "COMPLETED":
                    query += " AND (s.status != 'RETURNED' OR s.status IS NULL)"
            
            if date:
                query += " AND s.date LIKE ?"
                params.append(f"{date}%")
                
            if invoice:
                query += " AND s.invoice LIKE ?"
                params.append(f"%{invoice}%")
                
            query += " ORDER BY s.date DESC"
            
            cur.execute(query, params)
            sales = cur.fetchall()
            
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            for sale in sales:
                status = sale[7] if sale[7] else "COMPLETED"
                returned_qty = sale[8] or 0
                return_reason = sale[9] or "N/A"
                
                # Determine status text
                if status == "RETURNED":
                    status_text = "FULLY RETURNED"
                elif returned_qty > 0:
                    status_text = f"PARTIALLY RETURNED ({returned_qty} of {sale[3]})"
                else:
                    status_text = "COMPLETED"
                
                tag = 'returned' if status == "RETURNED" else ('completed' if returned_qty == 0 else 'partial')
                
                self.sales_tree.insert("", "end", values=(
                    sale[0],
                    sale[1],
                    sale[2],
                    f"{sale[3]} (Returned: {returned_qty})",
                    f"₱{sale[4]:.2f}",
                    sale[5],
                    sale[6] or "Walk-in",
                    status_text,
                    return_reason
                ), tags=(tag,))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")
    
    def show_returns(self):
        """Display returns management screen - FIXED"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="RETURNS MANAGEMENT",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(pady=20)
        
        returns_frame = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                     corner_radius=15, border_width=2, border_color="#FF6B35")
        returns_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_frame = ctk.CTkFrame(returns_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        sales_header = ctk.CTkFrame(left_frame, fg_color="#0984e3", corner_radius=10)
        sales_header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(sales_header, text="RECENT SALES (Eligible for Return)", 
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)
        
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_frame, text="Search Invoice:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        self.return_invoice_entry = ctk.CTkEntry(search_frame, width=200, height=35,
                                                placeholder_text="Enter invoice number...",
                                                border_color="#FF6B35", corner_radius=8)
        self.return_invoice_entry.pack(side="left", padx=5)
        self.return_invoice_entry.bind("<KeyRelease>", lambda e: self.search_sales_for_return(e))
        
        tree_frame = ctk.CTkFrame(left_frame, fg_color=("#ffffff", "#4a4e69"), corner_radius=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.returns_sales_tree = ttk.Treeview(tree_frame, 
                                              columns=("ID", "Invoice", "Item", "Qty", "Date", "Customer"),
                                              show="headings", height=15)
        
        columns_config = {
            "ID": ("ID", 60),
            "Invoice": ("Invoice", 120),
            "Item": ("Item", 180),
            "Qty": ("Qty", 60),
            "Date": ("Date", 120),
            "Customer": ("Customer", 120)
        }
        
        for col, (text, width) in columns_config.items():
            self.returns_sales_tree.heading(col, text=text)
            self.returns_sales_tree.column(col, width=width)
        
        self.returns_sales_tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.returns_sales_tree.bind("<Double-1>", lambda e: self.select_sale_for_return(e))
        
        right_frame = ctk.CTkFrame(returns_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", padx=10, pady=10)
        
        return_header = ctk.CTkFrame(right_frame, fg_color="#00b894", corner_radius=10)
        return_header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(return_header, text="PROCESS RETURN", 
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)
        
        form_frame = ctk.CTkFrame(right_frame, fg_color=("#e8f4fd", "#2d3047"),
                                  corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_frame = ctk.CTkFrame(form_frame, fg_color=("#ffffff", "#4a4e69"),
                                  corner_radius=8)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        self.selected_sale_label = ctk.CTkLabel(info_frame, 
                                               text="No sale selected",
                                               font=ctk.CTkFont(size=12),
                                               text_color="#7f8c8d")
        self.selected_sale_label.pack(pady=10)
        
        qty_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        qty_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(qty_frame, text="Return Quantity:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.return_qty_entry = ctk.CTkEntry(qty_frame, placeholder_text="Enter quantity to return",
                                             border_color="#3498db", corner_radius=8)
        self.return_qty_entry.pack(fill="x", pady=(0, 5))
        
        reason_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        reason_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(reason_frame, text="Return Reason:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.return_reason_combo = ctk.CTkComboBox(reason_frame,
                                                   values=["Defective Product", "Wrong Item", "Damaged on Delivery",
                                                           "Changed Mind", "No Longer Needed", "Other"],
                                                   width=300, height=35,
                                                   border_color="#3498db", corner_radius=8)
        self.return_reason_combo.pack(fill="x", pady=(0, 5))
        
        self.other_reason_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        
        def show_other_reason(*args):
            if self.return_reason_combo.get() == "Other":
                self.other_reason_frame.pack(fill="x", padx=10, pady=10)
            else:
                self.other_reason_frame.pack_forget()
        
        self.return_reason_combo.configure(command=show_other_reason)
        
        ctk.CTkLabel(self.other_reason_frame, text="Specify Reason:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.other_reason_entry = ctk.CTkEntry(self.other_reason_frame,
                                               placeholder_text="Enter specific reason...",
                                               border_color="#3498db", corner_radius=8)
        self.other_reason_entry.pack(fill="x", pady=(0, 5))
        
        notes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        notes_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(notes_frame, text="Additional Notes:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.return_notes_entry = ctk.CTkEntry(notes_frame,
                                               placeholder_text="Any additional notes...",
                                               border_color="#3498db", corner_radius=8)
        self.return_notes_entry.pack(fill="x", pady=(0, 5))
        
        process_return_btn = ctk.CTkButton(form_frame, text="PROCESS RETURN",
                                           command=self.process_return,
                                           font=ctk.CTkFont(size=14, weight="bold"),
                                           height=45, fg_color="#00b894", hover_color="#00a085",
                                           corner_radius=10)
        process_return_btn.pack(pady=20, padx=10, fill="x")
        
        clear_selection_btn = ctk.CTkButton(form_frame, text="Clear Selection",
                                            command=self.clear_return_selection,
                                            height=35, fg_color="#f39c12", hover_color="#e67e22",
                                            corner_radius=8)
        clear_selection_btn.pack(pady=10, padx=10, fill="x")
        
        self.selected_sale_id = None
        self.selected_sale_qty = 0
        self.selected_sale_item = ""
        self.selected_invoice = ""
        
        self.load_recent_sales()
    
    def load_recent_sales(self):
        """Load recent sales eligible for return - FIXED"""
        try:
            if not hasattr(self, 'returns_sales_tree') or not self.returns_sales_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            cur.execute("""
                SELECT 
                    s.id,
                    s.invoice,
                    s.item,
                    s.qty,
                    s.date,
                    s.customer_name,
                    COALESCE(SUM(r.qty), 0) as already_returned,
                    s.qty - COALESCE(SUM(r.qty), 0) as remaining_qty
                FROM sales s
                LEFT JOIN sales r ON s.id = r.original_sale_id AND r.status = 'RETURNED'
                WHERE s.date >= ? 
                AND s.status != 'RETURNED'
                AND (s.original_sale_id IS NULL OR s.original_sale_id = '')
                GROUP BY s.id, s.invoice, s.item, s.qty, s.date, s.customer_name
                HAVING remaining_qty > 0
                ORDER BY s.date DESC
                LIMIT 50
            """, (thirty_days_ago,))
            
            sales = cur.fetchall()
            
            for item in self.returns_sales_tree.get_children():
                self.returns_sales_tree.delete(item)
            
            for sale in sales:
                original_qty = sale[3]
                already_returned = sale[6]
                remaining_qty = sale[7]
                
                display_text = f"{sale[2]}"
                
                self.returns_sales_tree.insert("", "end", values=(
                    sale[0],
                    sale[1],
                    display_text,
                    f"{remaining_qty}/{original_qty}",
                    sale[4],
                    sale[5]
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load recent sales: {str(e)}")
    
    def search_sales_for_return(self, event=None):
        """Search sales for return processing - FIXED"""
        search_term = self.return_invoice_entry.get()
        
        try:
            if not hasattr(self, 'returns_sales_tree') or not self.returns_sales_tree.winfo_exists():
                return
            
            conn = self.database.get_db()
            cur = conn.cursor()
            
            if search_term:
                cur.execute("""
                    SELECT 
                        s.id,
                        s.invoice,
                        s.item,
                        s.qty,
                        s.date,
                        s.customer_name,
                        COALESCE(SUM(r.qty), 0) as already_returned,
                        s.qty - COALESCE(SUM(r.qty), 0) as remaining_qty
                    FROM sales s
                    LEFT JOIN sales r ON s.id = r.original_sale_id AND r.status = 'RETURNED'
                    WHERE s.invoice LIKE ? 
                    AND s.status != 'RETURNED'
                    AND (s.original_sale_id IS NULL OR s.original_sale_id = '')
                    GROUP BY s.id, s.invoice, s.item, s.qty, s.date, s.customer_name
                    HAVING remaining_qty > 0
                    ORDER BY s.date DESC
                    LIMIT 50
                """, (f"%{search_term}%",))
            else:
                self.load_recent_sales()
                return
                
            sales = cur.fetchall()
            
            for item in self.returns_sales_tree.get_children():
                self.returns_sales_tree.delete(item)
            
            for sale in sales:
                original_qty = sale[3]
                already_returned = sale[6]
                remaining_qty = sale[7]
                
                display_text = f"{sale[2]}"
                
                self.returns_sales_tree.insert("", "end", values=(
                    sale[0],
                    sale[1],
                    display_text,
                    f"{remaining_qty}/{original_qty}",
                    sale[4],
                    sale[5]
                ))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")
    
    def select_sale_for_return(self, event=None):
        """Select a sale for return processing - FIXED"""
        if not hasattr(self, 'returns_sales_tree') or not self.returns_sales_tree.winfo_exists():
            return
        
        selection = self.returns_sales_tree.selection()
        if not selection:
            return
        
        item = self.returns_sales_tree.item(selection[0])
        sale_data = item['values']
        
        # Parse the quantity string "remaining/original"
        qty_parts = sale_data[3].split('/')
        if len(qty_parts) == 2:
            remaining_qty = int(qty_parts[0])
            original_qty = int(qty_parts[1])
        else:
            remaining_qty = original_qty = int(sale_data[3])
        
        self.selected_sale_id = sale_data[0]
        self.selected_sale_qty = original_qty
        self.remaining_qty = remaining_qty
        self.selected_sale_item = sale_data[2]
        self.selected_invoice = sale_data[1]
        
        # Calculate already returned
        already_returned = original_qty - remaining_qty
        
        self.selected_sale_label.configure(
            text=f"Invoice: {sale_data[1]}\n"
                 f"Item: {self.selected_sale_item}\n"
                 f"Original Qty: {original_qty}\n"
                 f"Already Returned: {already_returned}\n"
                 f"Remaining Qty: {remaining_qty}\n"
                 f"Customer: {sale_data[5]}",
            text_color="#2c3e50"
        )
        
        self.return_qty_entry.delete(0, 'end')
        self.return_qty_entry.insert(0, str(remaining_qty))
    
    def clear_return_selection(self):
        """Clear the current return selection"""
        self.selected_sale_id = None
        self.selected_sale_qty = 0
        self.selected_sale_item = ""
        self.selected_invoice = ""
        
        if hasattr(self, 'selected_sale_label'):
            self.selected_sale_label.configure(text="No sale selected", text_color="#7f8c8d")
        if hasattr(self, 'return_qty_entry'):
            self.return_qty_entry.delete(0, 'end')
        if hasattr(self, 'return_reason_combo'):
            self.return_reason_combo.set("")
        if hasattr(self, 'other_reason_entry'):
            self.other_reason_entry.delete(0, 'end')
        if hasattr(self, 'return_notes_entry'):
            self.return_notes_entry.delete(0, 'end')
        if hasattr(self, 'other_reason_frame'):
            self.other_reason_frame.pack_forget()
    
    def process_return(self):
        """Process the return and update inventory stock - FIXED for return reason"""
        if not self.selected_sale_id:
            messagebox.showwarning("Warning", "Please select a sale to return!")
            return
        
        try:
            return_qty = int(self.return_qty_entry.get())
            if return_qty <= 0:
                messagebox.showerror("Error", "Return quantity must be greater than 0!")
                return
            if return_qty > self.remaining_qty:
                messagebox.showerror("Error", f"Cannot return more than remaining quantity ({self.remaining_qty})!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity!")
            return
        
        reason = self.return_reason_combo.get()
        if not reason:
            messagebox.showerror("Error", "Please select a return reason!")
            return
        
        if reason == "Other":
            other_reason = self.other_reason_entry.get()
            if not other_reason:
                messagebox.showerror("Error", "Please specify the return reason!")
                return
            reason = other_reason
        
        notes = self.return_notes_entry.get()
        
        # Check how much has already been returned for this sale
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get total already returned for this sale
            cur.execute("""
                SELECT COALESCE(SUM(qty), 0) 
                FROM sales 
                WHERE original_sale_id = ? 
                AND status = 'RETURNED'
            """, (self.selected_sale_id,))
            
            already_returned = cur.fetchone()[0] or 0
            remaining_qty = self.selected_sale_qty - already_returned
            
            if return_qty > remaining_qty:
                messagebox.showerror("Error", 
                    f"Cannot return {return_qty}. Only {remaining_qty} remaining to return.\n"
                    f"(Original: {self.selected_sale_qty}, Already returned: {already_returned})")
                conn.close()
                return
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not check return status: {str(e)}")
            return
        
        # Confirm with user
        confirmation_message = f"Process return for:\n\n"
        confirmation_message += f"Invoice: {self.selected_invoice}\n"
        confirmation_message += f"Item: {self.selected_sale_item}\n"
        confirmation_message += f"Quantity: {return_qty} of {self.selected_sale_qty} (Already returned: {already_returned})\n"
        confirmation_message += f"Reason: {reason}\n\n"
        
        if return_qty < self.selected_sale_qty:
            confirmation_message += f"Note: This is a partial return. {self.selected_sale_qty - return_qty - already_returned} items will remain in the sale.\n\n"
        
        confirmation_message += "Are you sure?"
        
        result = messagebox.askyesno("Confirm Return", confirmation_message)
        
        if not result:
            return
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get the original sale details
            cur.execute("SELECT * FROM sales WHERE id = ?", (self.selected_sale_id,))
            sale = cur.fetchone()
            
            if not sale:
                messagebox.showerror("Error", "Sale not found!")
                return
            
            # Get product details
            cur.execute("SELECT id, price, stock FROM inventory WHERE name = ?", (sale[2],))
            product = cur.fetchone()
            
            if not product:
                messagebox.showerror("Error", f"Product '{sale[2]}' not found in inventory!")
                return
            
            product_id, product_price, current_stock = product
            
            # Calculate return amount
            unit_price = sale[4] / sale[3] if sale[3] > 0 else product_price
            return_amount = unit_price * return_qty
            
            # Create return invoice number
            today = datetime.datetime.now().strftime('%Y%m%d')
            
            # Check if we have returns today to increment the counter
            cur.execute("SELECT COUNT(*) FROM sales WHERE invoice LIKE ? AND status = 'RETURNED'", 
                       (f"RET{today}%",))
            today_return_count = cur.fetchone()[0] or 0
            
            return_invoice = f"RET{today}{today_return_count + 1:04d}"
            
            # Create the return record - FIXED: Save return_reason properly
            cur.execute("""INSERT INTO sales 
                        (invoice, item, qty, subtotal, date, notes, customer_name, status, 
                         return_reason, return_date, returned_qty, original_sale_id, original_invoice) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (return_invoice,
                         sale[2],
                         return_qty,
                         -return_amount,  # Negative amount for returns
                         self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                         notes or "",
                         sale[7] or "Walk-in",
                         "RETURNED",
                         reason,  # This is the return reason - FIXED
                         self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                         return_qty,
                         self.selected_sale_id,
                         self.selected_invoice))
            
            # Also update the original sale with the return reason if it's fully returned
            total_returned_qty = already_returned + return_qty
            
            # Update inventory stock
            new_stock = current_stock + return_qty
            cur.execute("UPDATE inventory SET stock = ? WHERE id = ?",
                        (new_stock, product_id))
            
            # Update the original sale's returned_qty field
            cur.execute("UPDATE sales SET returned_qty = ? WHERE id = ?",
                        (total_returned_qty, self.selected_sale_id))
            
            # If fully returned, also update the return_reason on the original sale
            if total_returned_qty >= sale[3]:
                cur.execute("UPDATE sales SET status = 'RETURNED', return_reason = ? WHERE id = ?", 
                           (reason, self.selected_sale_id))
            
            conn.commit()
            conn.close()
            
            success_message = f"Return processed successfully!\n\n"
            success_message += f"Return Invoice #: {return_invoice}\n"
            success_message += f"Original Invoice: {self.selected_invoice}\n"
            success_message += f"Item: {self.selected_sale_item}\n"
            success_message += f"Returned Quantity: {return_qty}\n"
            success_message += f"Return Reason: {reason}\n"
            success_message += f"Amount Refunded: ₱{return_amount:.2f}\n"
            success_message += f"Stock updated: {current_stock} → {new_stock}\n"
            
            if total_returned_qty < sale[3]:
                remaining = sale[3] - total_returned_qty
                success_message += f"\nRemaining items in sale: {remaining}"
            
            messagebox.showinfo("Success", success_message)
            
            self.clear_return_selection()
            
            if hasattr(self, 'returns_sales_tree') and self.returns_sales_tree.winfo_exists():
                self.load_recent_sales()
            
            if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                self.inventory.load_inventory()
            
            if hasattr(self, 'sales_tree') and self.sales_tree.winfo_exists():
                self.load_sales_history()
            
            if hasattr(self, 'content_frame'):
                self.show_dashboard()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not process return: {str(e)}")
    
    def show_settings(self):
        """Display settings screen"""
        self.clear_content()
        
        title_label = ctk.CTkLabel(self.content_frame, text="SETTINGS",
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(pady=20)
        
        settings_container = ctk.CTkFrame(self.content_frame, fg_color=("#f8f9fa", "#2d3047"),
                                          corner_radius=15, border_width=2, border_color="#FF6B35")
        settings_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # CATALOG MANAGEMENT SECTION
        catalog_section = ctk.CTkFrame(settings_container, fg_color=("#ffffff", "#4a4e69"),
                                       corner_radius=10)
        catalog_section.pack(fill="x", padx=20, pady=20)
        
        catalog_header = ctk.CTkFrame(catalog_section, fg_color="#00b894", corner_radius=8)
        catalog_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(catalog_header, text="AUTO PARTS CATALOG",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)
        
        catalog_buttons_frame = ctk.CTkFrame(catalog_section, fg_color="transparent")
        catalog_buttons_frame.pack(pady=20, padx=20, fill="x")
        
        # Import all catalogs button
        import_all_btn = ctk.CTkButton(catalog_buttons_frame,
                                      text="IMPORT ALL CATALOGS",
                                      command=self.import_all_catalogs,
                                      width=250, height=45,
                                      fg_color="#0984e3",
                                      hover_color="#0971c2",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      corner_radius=8)
        import_all_btn.pack(pady=15)
        
        # Individual brand buttons
        brand_frame = ctk.CTkFrame(catalog_buttons_frame, fg_color="transparent")
        brand_frame.pack(fill="x", pady=10)
        
        brands = [
            ("Toyota", "#e74c3c", self.import_toyota_catalog),
            ("Honda", "#3498db", self.import_honda_catalog),
            ("Mitsubishi", "#9b59b6", self.import_mitsubishi_catalog),
            ("Ford", "#e67e22", self.import_ford_catalog),
            ("Nissan", "#1abc9c", self.import_nissan_catalog),
            ("Hyundai", "#f39c12", self.import_hyundai_catalog)
        ]
        
        for i, (brand, color, command) in enumerate(brands):
            btn = ctk.CTkButton(brand_frame,
                               text=f"{brand}",
                               command=command,
                               width=120, height=35,
                               fg_color=color,
                               hover_color=self.darken_color(color),
                               font=ctk.CTkFont(size=12, weight="bold"),
                               corner_radius=6)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            brand_frame.grid_columnconfigure(i%3, weight=1)
        
        # Clear catalog button
        clear_catalog_btn = ctk.CTkButton(catalog_buttons_frame,
                                         text="CLEAR ALL CATALOGS",
                                         command=self.clear_all_catalogs,
                                         width=250, height=45,
                                         fg_color="#e74c3c",
                                         hover_color="#c0392b",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         corner_radius=8)
        clear_catalog_btn.pack(pady=15)
        
        # DATABASE MANAGEMENT SECTION
        db_section = ctk.CTkFrame(settings_container, fg_color=("#ffffff", "#4a4e69"),
                                  corner_radius=10)
        db_section.pack(fill="x", padx=20, pady=20)
        
        db_header = ctk.CTkFrame(db_section, fg_color="#FF6B35", corner_radius=8)
        db_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(db_header, text="DATABASE MANAGEMENT",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)
        
        db_buttons_frame = ctk.CTkFrame(db_section, fg_color="transparent")
        db_buttons_frame.pack(pady=20, padx=20, fill="x")
        
        clear_history_btn = ctk.CTkButton(db_buttons_frame, 
                                          text="CLEAR SALES HISTORY",
                                          command=self.clear_sales_history,
                                          width=250, height=45,
                                          fg_color="#f39c12",
                                          hover_color="#e67e22",
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          corner_radius=8)
        clear_history_btn.pack(pady=15)
        
        clear_inventory_btn = ctk.CTkButton(db_buttons_frame,
                                            text="CLEAR ALL INVENTORY",
                                            command=self.clear_all_inventory,
                                            width=250, height=45,
                                            fg_color="#e74c3c",
                                            hover_color="#c0392b",
                                            font=ctk.CTkFont(size=14, weight="bold"),
                                            corner_radius=8)
        clear_inventory_btn.pack(pady=15)
        
        # SYSTEM INFORMATION SECTION
        info_section = ctk.CTkFrame(settings_container, fg_color=("#ffffff", "#4a4e69"),
                                    corner_radius=10)
        info_section.pack(fill="x", padx=20, pady=20)
        
        info_header = ctk.CTkFrame(info_section, fg_color="#6c5ce7", corner_radius=8)
        info_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(info_header, text="SYSTEM INFORMATION",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="white").pack(pady=8)
        
        info_content = ctk.CTkFrame(info_section, fg_color="transparent")
        info_content.pack(pady=20, padx=20, fill="x")
        
        db_file = "autoparts.db"
        db_exists = os.path.exists(db_file)
        db_size = "N/A"
        if db_exists:
            size_bytes = os.path.getsize(db_file)
            db_size = f"{size_bytes / 1024 / 1024:.2f} MB"
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM inventory")
            product_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT invoice) FROM sales WHERE status != 'RETURNED' AND subtotal > 0")
            sales_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT invoice) FROM sales WHERE status = 'RETURNED' AND subtotal < 0")
            returns_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(DISTINCT invoice) FROM sales WHERE status != 'RETURNED' AND subtotal > 0")
            transaction_count = cur.fetchone()[0]
            
            conn.close()
        except:
            product_count = sales_count = returns_count = transaction_count = "N/A"
        
        info_items = [
            ("Product Count:", str(product_count)),
            ("Total Sales Transactions:", str(sales_count)),
            ("Total Return Transactions:", str(returns_count)),
            ("Database Size:", db_size),
            ("Last Updated:", datetime.datetime.now().strftime("%Y-%m-%d")),
            ("Version:", "Auto Parts Pro v2.0")
        ]
        
        for label, value in info_items:
            row_frame = ctk.CTkFrame(info_content, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(row_frame, text=label,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         width=180, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkLabel(row_frame, text=value,
                         font=ctk.CTkFont(size=13),
                         text_color="#3498db").pack(side="left", padx=5)
        
        # WARNING SECTION
        warning_frame = ctk.CTkFrame(settings_container, fg_color=("#ffebee", "#2d3047"),
                                     corner_radius=10, border_width=2, border_color="#e74c3c")
        warning_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(warning_frame, text="WARNING",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e74c3c").pack(pady=(15, 5))
        
        ctk.CTkLabel(warning_frame, text="Clearing database records cannot be undone!",
                     font=ctk.CTkFont(size=12),
                     text_color=("#7f8c8d", "#bdc3c7")).pack(pady=(0, 15))
        ctk.CTkLabel(warning_frame, text="Make sure to backup your data before proceeding.",
                     font=ctk.CTkFont(size=12),
                     text_color=("#7f8c8d", "#bdc3c7")).pack(pady=(0, 15))
    
    def import_all_catalogs(self):
        """Import all auto parts catalogs"""
        result = messagebox.askyesno(
            "Import All Catalogs",
            "This will import all 6 auto parts catalogs (Toyota, Honda, Mitsubishi, Ford, Nissan, Hyundai).\n\n"
            "Continue?"
        )
        
        if not result:
            return
        
        try:
            # Show progress dialog
            progress_dialog = ctk.CTkToplevel(self.root)
            progress_dialog.title("Importing Catalogs...")
            progress_dialog.geometry("400x200")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            progress_dialog.resizable(False, False)
            
            main_frame = ctk.CTkFrame(progress_dialog, corner_radius=15)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(main_frame, text="Importing Auto Parts Catalogs",
                         font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
            
            progress_label = ctk.CTkLabel(main_frame, text="Starting import...",
                                         font=ctk.CTkFont(size=12))
            progress_label.pack(pady=10)
            
            progress_bar = ctk.CTkProgressBar(main_frame, width=300)
            progress_bar.pack(pady=20)
            progress_bar.set(0)
            
            self.root.update()
            
            # Import all catalogs
            total_added, success_count, total_count = self.catalog.populate_all_catalogs()
            
            progress_bar.set(1.0)
            progress_label.configure(text=f"Import completed! Added {total_added} parts.")
            
            self.root.after(1500, progress_dialog.destroy)
            
            messagebox.showinfo(
                "Import Complete",
                f"Successfully imported {success_count}/{total_count} catalogs!\n"
                f"Added {total_added} auto parts to inventory.\n\n"
                "Your inventory has been populated with genuine auto parts from:\n"
                "• Toyota\n• Honda\n• Mitsubishi\n• Ford\n• Nissan\n• Hyundai"
            )
            
            # Refresh inventory if open
            if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                self.inventory.load_inventory()
            
            # Refresh dashboard
            if hasattr(self, 'content_frame'):
                self.show_dashboard()
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import catalogs: {str(e)}")
    
    def import_toyota_catalog(self):
        """Import Toyota parts catalog"""
        result = messagebox.askyesno(
            "Import Toyota Catalog",
            "This will import Toyota auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_toyota_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Toyota catalog!\n"
                    f"Added {added_count} Toyota parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Toyota catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Toyota catalog: {str(e)}")
    
    def import_honda_catalog(self):
        """Import Honda parts catalog"""
        result = messagebox.askyesno(
            "Import Honda Catalog",
            "This will import Honda auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_honda_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Honda catalog!\n"
                    f"Added {added_count} Honda parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Honda catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Honda catalog: {str(e)}")
    
    def import_mitsubishi_catalog(self):
        """Import Mitsubishi parts catalog"""
        result = messagebox.askyesno(
            "Import Mitsubishi Catalog",
            "This will import Mitsubishi auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_mitsubishi_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Mitsubishi catalog!\n"
                    f"Added {added_count} Mitsubishi parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Mitsubishi catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Mitsubishi catalog: {str(e)}")
    
    def import_ford_catalog(self):
        """Import Ford parts catalog"""
        result = messagebox.askyesno(
            "Import Ford Catalog",
            "This will import Ford auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_ford_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Ford catalog!\n"
                    f"Added {added_count} Ford parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Ford catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Ford catalog: {str(e)}")
    
    def import_nissan_catalog(self):
        """Import Nissan parts catalog"""
        result = messagebox.askyesno(
            "Import Nissan Catalog",
            "This will import Nissan auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_nissan_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Nissan catalog!\n"
                    f"Added {added_count} Nissan parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Nissan catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Nissan catalog: {str(e)}")
    
    def import_hyundai_catalog(self):
        """Import Hyundai parts catalog"""
        result = messagebox.askyesno(
            "Import Hyundai Catalog",
            "This will import Hyundai auto parts catalog.\n\nContinue?"
        )
        
        if not result:
            return
        
        try:
            added_count, success = self.catalog.add_hyundai_parts_to_inventory()
            
            if success:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported Hyundai catalog!\n"
                    f"Added {added_count} Hyundai parts to inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Import Error", "Failed to import Hyundai catalog.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not import Hyundai catalog: {str(e)}")
    
    def clear_all_catalogs(self):
        """Clear all catalog items from inventory"""
        result = messagebox.askyesno(
            "Clear All Catalogs",
            "WARNING\n\n"
            "This will remove ALL auto parts catalog items from inventory!\n"
            "Only custom added products will remain.\n\n"
            "Are you sure you want to continue?"
        )
        
        if not result:
            return
        
        try:
            before_count, success = self.catalog.clear_all_catalogs()
            
            if success:
                messagebox.showinfo(
                    "Clear Complete",
                    f"Successfully cleared all catalog items!\n"
                    f"Removed {before_count} parts from inventory."
                )
                
                # Refresh inventory if open
                if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                    self.inventory.load_inventory()
                
                # Refresh dashboard
                if hasattr(self, 'content_frame'):
                    self.show_dashboard()
            else:
                messagebox.showerror("Clear Error", "Failed to clear catalog items.")
                
        except Exception as e:
            messagebox.showerror("Clear Error", f"Could not clear catalog items: {str(e)}")
    
    def clear_sales_history(self):
        """Clear all sales history from the database"""
        result = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to delete ALL sales history?\nThis action cannot be undone!"
        )
        if not result:
            return
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM sales")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='sales'")
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "All sales history has been cleared successfully!")
            
            if hasattr(self, 'sales_tree') and self.sales_tree.winfo_exists():
                self.load_sales_history()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not clear sales history: {str(e)}")
    
    def clear_all_inventory(self):
        """Clear all inventory items"""
        result = messagebox.askyesno(
            "Confirm Clear",
            "Are you sure you want to delete ALL inventory items?\nThis action cannot be undone!"
        )
        if not result:
            return
        
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM inventory")
            cur.execute("DELETE FROM sqlite_sequence WHERE name='inventory'")
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "All inventory items have been cleared successfully!")
            
            if hasattr(self, 'inventory_tree') and self.inventory_tree.winfo_exists():
                self.inventory.load_inventory()
            
            if hasattr(self, 'content_frame'):
                self.show_dashboard()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not clear inventory: {str(e)}")
    
    def logout(self):
        self.current_user = None
        self.show_login_screen()
    
    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def clear_content(self):
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
    
    def run(self):
        self.root.mainloop()