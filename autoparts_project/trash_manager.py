from utils import *
from database import Database

# TRASH MANAGER CLASS
# ============================================================================
class TrashManager(AutoParts):
    """Manages trash bin operations"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.db = Database()
    
    def move_to_trash(self, product_id):
        """Move product to trash instead of deleting permanently"""
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            
            # Get the product details
            cur.execute("SELECT * FROM inventory WHERE id = ?", (product_id,))
            product = cur.fetchone()
            
            if product:
                # Insert into trash table
                cur.execute("""
                    INSERT INTO trash 
                    (original_id, name, price, stock, category, image, brand, 
                     vehicle_model, year_range, part_category, part_subcategory, 
                     deleted_at, deleted_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product[0],  # original_id
                    product[1],  # name
                    product[2],  # price
                    product[3],  # stock
                    product[4],  # category
                    product[5],  # image
                    product[6],  # brand
                    product[7],  # vehicle_model
                    product[8],  # year_range
                    product[9],  # part_category
                    product[10], # part_subcategory
                    self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),  # deleted_at
                    self.app.current_user[1] if self.app.current_user else "System"  # deleted_by
                ))
                
                # Delete from inventory
                cur.execute("DELETE FROM inventory WHERE id = ?", (product_id,))
                
                conn.commit()
                conn.close()
                return True, f"Product moved to trash successfully!"
            else:
                return False, "Product not found!"
                
        except Exception as e:
            return False, f"Could not move to trash: {str(e)}"
    
    def get_trash_items(self):
        """Get all items in trash"""
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM trash ORDER BY deleted_at DESC")
            items = cur.fetchall()
            conn.close()
            return items
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load trash items: {str(e)}")
            return []
    
    def restore_item(self, trash_id):
        """Restore item from trash back to inventory"""
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            
            # Get item from trash
            cur.execute("SELECT * FROM trash WHERE id = ?", (trash_id,))
            item = cur.fetchone()
            
            if item:
                # Check if product already exists in inventory with same name
                cur.execute("SELECT id FROM inventory WHERE name = ?", (item[2],))
                existing = cur.fetchone()
                
                if existing:
                    return False, f"Product '{item[2]}' already exists in inventory!"
                
                # Insert back to inventory
                cur.execute("""
                    INSERT INTO inventory 
                    (name, price, stock, category, image, brand, 
                     vehicle_model, year_range, part_category, part_subcategory)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item[2],  # name
                    item[3],  # price
                    item[4],  # stock
                    item[5],  # category
                    item[6],  # image
                    item[7],  # brand
                    item[8],  # vehicle_model
                    item[9],  # year_range
                    item[10], # part_category
                    item[11]  # part_subcategory
                ))
                
                # Remove from trash
                cur.execute("DELETE FROM trash WHERE id = ?", (trash_id,))
                
                conn.commit()
                conn.close()
                return True, f"Product '{item[2]}' restored successfully!"
            else:
                return False, "Item not found in trash!"
                
        except Exception as e:
            return False, f"Could not restore item: {str(e)}"
    
    def permanent_delete(self, trash_id):
        """Permanently delete item from trash"""
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            
            # Get item name for message
            cur.execute("SELECT name FROM trash WHERE id = ?", (trash_id,))
            item = cur.fetchone()
            
            if item:
                # Delete from trash
                cur.execute("DELETE FROM trash WHERE id = ?", (trash_id,))
                conn.commit()
                conn.close()
                return True, f"Product '{item[0]}' permanently deleted!"
            else:
                return False, "Item not found in trash!"
                
        except Exception as e:
            return False, f"Could not delete permanently: {str(e)}"
    
    def empty_trash(self):
        """Empty all items from trash"""
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            
            # Count items before deletion
            cur.execute("SELECT COUNT(*) FROM trash")
            count = cur.fetchone()[0]
            
            # Delete all from trash
            cur.execute("DELETE FROM trash")
            
            # Reset auto-increment
            cur.execute("DELETE FROM sqlite_sequence WHERE name='trash'")
            
            conn.commit()
            conn.close()
            
            return True, f"Trash emptied! {count} items permanently deleted."
        except Exception as e:
            return False, f"Could not empty trash: {str(e)}"
# ============================================================================