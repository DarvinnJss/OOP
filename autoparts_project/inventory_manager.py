from utils import *
from database import Database

# INVENTORY MANAGER CLASS
# ============================================================================
class InventoryManager(AutoParts):
    """Manages inventory operations"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.db = Database()
    
    def load_inventory(self):
        """Load inventory data into treeview"""
        try:
            if not hasattr(self.app, 'inventory_tree') or not self.app.inventory_tree.winfo_exists():
                return
            
            conn = self.db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory")
            products = cur.fetchall()
            # Clear existing items
            for item in self.app.inventory_tree.get_children():
                self.app.inventory_tree.delete(item)
            for product in products:
                self.app.inventory_tree.insert("", "end", values=(
                    product[0],
                    product[1],
                    f"₱{product[2]:.2f}",
                    product[3],
                    product[4],
                    product[6],
                    product[7],
                    product[8] or "Not Specified"
                ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load inventory: {str(e)}")
    
    def search_inventory(self):
        """Search inventory by search term"""
        search_term = self.app.search_entry.get()
        try:
            if not hasattr(self.app, 'inventory_tree') or not self.app.inventory_tree.winfo_exists():
                return
            
            conn = self.db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM inventory WHERE name LIKE ? OR brand LIKE ? OR vehicle_model LIKE ?",
                        (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            products = cur.fetchall()
            # Clear existing items
            for item in self.app.inventory_tree.get_children():
                self.app.inventory_tree.delete(item)
            if not products:
                self.app.inventory_tree.insert("", "end", values=(
                    "", "There's no product in the inventory", "", "", "", "", "", ""
                ))
            else:
                for product in products:
                    self.app.inventory_tree.insert("", "end", values=(
                        product[0],
                        product[1],
                        f"₱{product[2]:.2f}",
                        product[3],
                        product[4],
                        product[6],
                        product[7],
                        product[8] or "Not Specified"
                    ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")
    
    def delete_selected_product(self):
        """Delete the selected product from inventory (move to trash)"""
        if not hasattr(self.app, 'inventory_tree') or not self.app.inventory_tree.winfo_exists():
            return
        
        selection = self.app.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete!")
            return
        
        item = self.app.inventory_tree.item(selection[0])
        product_data = item['values']
        product_id = product_data[0]
        product_name = product_data[1]
        
        if product_name == "There's no product in the inventory":
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to move '{product_name}' to trash?\n\n"
            f"You can restore it later from the Trash Bin."
        )
        
        if not result:
            return
        
        try:
            # Use trash manager to move to trash instead of permanent delete
            success, message = self.app.trash.move_to_trash(product_id)
            
            if success:
                messagebox.showinfo("Moved to Trash", message)
                self.load_inventory()
                # Refresh dashboard if open
                if hasattr(self.app, 'content_frame'):
                    self.app.show_dashboard()
            else:
                messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not delete product: {str(e)}")
