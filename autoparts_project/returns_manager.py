from utils import *
import datetime

class ReturnsManager(AutoParts):
    """Manages returns processing and tracking."""
    
    def __init__(self, system):
        super().__init__()
        self.system = system
        self.database = system.database
    
    def get_todays_returns_summary(self):
        """Get today's returns summary for dashboard."""
        try:
            today = self.get_current_time().strftime('%Y-%m-%d')
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Count distinct return invoices and sum amounts
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT invoice) as return_count,
                    ABS(SUM(subtotal)) as return_amount
                FROM sales 
                WHERE status = 'RETURNED' 
                AND date LIKE ?
                AND subtotal < 0
            """, (f"{today}%",))
            
            result = cur.fetchone()
            conn.close()
            
            return_count = result[0] or 0
            return_amount = result[1] or 0.0
            
            return return_count, return_amount
            
        except Exception as e:
            print(f"Error getting returns summary: {e}")
            return 0, 0.0
    
    def process_return(self, sale_id, return_qty, reason, notes=""):
        """Process a return for a specific sale."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get the original sale details
            cur.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
            sale = cur.fetchone()
            
            if not sale:
                return False, "Sale not found!"
            
            # Get product details
            cur.execute("SELECT id, price, stock FROM inventory WHERE name = ?", (sale[2],))
            product = cur.fetchone()
            
            if not product:
                return False, f"Product '{sale[2]}' not found in inventory!"
            
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
            
            # Create the return record
            cur.execute("""INSERT INTO sales 
                        (invoice, item, qty, subtotal, date, notes, customer_name, status, 
                         return_reason, return_date, returned_qty, original_sale_id, original_invoice) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (return_invoice,
                         sale[2],
                         return_qty,
                         -return_amount,  # Negative amount for returns
                         self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                         notes,
                         sale[7],
                         "RETURNED",
                         reason,
                         self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                         return_qty,
                         sale_id,
                         sale[1]))
            
            # Update inventory stock
            new_stock = current_stock + return_qty
            cur.execute("UPDATE inventory SET stock = ? WHERE id = ?",
                        (new_stock, product_id))
            
            # Update the original sale status if fully returned
            if return_qty >= sale[3]:
                cur.execute("UPDATE sales SET status = 'RETURNED' WHERE id = ?", (sale_id,))
            
            conn.commit()
            conn.close()
            
            return True, {
                'return_invoice': return_invoice,
                'return_amount': return_amount,
                'new_stock': new_stock,
                'original_stock': current_stock
            }
            
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def get_return_history(self, start_date=None, end_date=None, invoice_filter=None):
        """Get return history with optional filters."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    invoice,
                    original_invoice,
                    item,
                    qty,
                    ABS(subtotal) as return_amount,
                    date,
                    customer_name,
                    return_reason,
                    notes
                FROM sales 
                WHERE status = 'RETURNED'
                AND subtotal < 0
            """
            
            params = []
            
            if start_date:
                query += " AND date >= ?"
                params.append(f"{start_date}%")
            
            if end_date:
                query += " AND date <= ?"
                params.append(f"{end_date} 23:59:59")
            
            if invoice_filter:
                query += " AND (invoice LIKE ? OR original_invoice LIKE ?)"
                params.append(f"%{invoice_filter}%")
                params.append(f"%{invoice_filter}%")
            
            query += " ORDER BY date DESC"
            
            cur.execute(query, params)
            returns = cur.fetchall()
            conn.close()
            
            return returns
            
        except Exception as e:
            print(f"Error getting return history: {e}")
            return []
    
    def get_sales_for_return(self, invoice_number=None):
        """Get sales eligible for return, optionally filtered by invoice."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Only show sales from last 30 days that haven't been fully returned
            thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            
            query = """
                SELECT s.id, s.invoice, s.item, s.qty, s.subtotal, s.date, 
                       s.customer_name, i.price, i.stock,
                       COALESCE(SUM(r.qty), 0) as already_returned_qty
                FROM sales s
                LEFT JOIN inventory i ON s.item = i.name
                LEFT JOIN sales r ON s.id = r.original_sale_id AND r.status = 'RETURNED'
                WHERE s.status != 'RETURNED'
                AND s.date >= ?
                AND s.original_sale_id IS NULL
            """
            
            params = [thirty_days_ago]
            
            if invoice_number:
                query += " AND s.invoice LIKE ?"
                params.append(f"%{invoice_number}%")
            
            query += " GROUP BY s.id, s.invoice, s.item, s.qty, s.subtotal, s.date, s.customer_name"
            query += " HAVING s.qty > COALESCE(SUM(r.qty), 0)"
            query += " ORDER BY s.date DESC LIMIT 50"
            
            cur.execute(query, params)
            sales = cur.fetchall()
            conn.close()
            
            return sales
            
        except Exception as e:
            print(f"Error getting sales for return: {e}")
            return []
    
    def get_return_statistics(self, period='today'):
        """Get return statistics for a given period."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            if period == 'today':
                date_filter = datetime.datetime.now().strftime('%Y-%m-%d')
                query = "SELECT COUNT(DISTINCT invoice), ABS(SUM(subtotal)) FROM sales WHERE status = 'RETURNED' AND date LIKE ?"
                params = (f"{date_filter}%",)
            elif period == 'week':
                week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                query = "SELECT COUNT(DISTINCT invoice), ABS(SUM(subtotal)) FROM sales WHERE status = 'RETURNED' AND date >= ?"
                params = (week_ago,)
            elif period == 'month':
                month_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
                query = "SELECT COUNT(DISTINCT invoice), ABS(SUM(subtotal)) FROM sales WHERE status = 'RETURNED' AND date >= ?"
                params = (month_ago,)
            else:  # all time
                query = "SELECT COUNT(DISTINCT invoice), ABS(SUM(subtotal)) FROM sales WHERE status = 'RETURNED'"
                params = ()
            
            cur.execute(query, params)
            result = cur.fetchone()
            conn.close()
            
            return_count = result[0] or 0
            return_amount = result[1] or 0.0
            
            return return_count, return_amount
            
        except Exception as e:
            print(f"Error getting return statistics: {e}")
            return 0, 0.0
    
    def get_top_returned_products(self, limit=10):
        """Get most frequently returned products."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    item,
                    COUNT(*) as return_count,
                    SUM(qty) as total_returned_qty,
                    ABS(SUM(subtotal)) as total_return_amount
                FROM sales 
                WHERE status = 'RETURNED'
                GROUP BY item
                ORDER BY return_count DESC
                LIMIT ?
            """
            
            cur.execute(query, (limit,))
            products = cur.fetchall()
            conn.close()
            
            return products
            
        except Exception as e:
            print(f"Error getting top returned products: {e}")
            return []
    
    def validate_return_quantity(self, sale_id, return_qty):
        """Validate if the return quantity is acceptable."""
        try:
            conn = self.database.get_db()
            cur = conn.cursor()
            
            # Get original sale quantity and already returned quantity
            cur.execute("""
                SELECT 
                    s.qty,
                    COALESCE(SUM(r.qty), 0) as already_returned
                FROM sales s
                LEFT JOIN sales r ON s.id = r.original_sale_id AND r.status = 'RETURNED'
                WHERE s.id = ?
                GROUP BY s.id
            """, (sale_id,))
            
            result = cur.fetchone()
            conn.close()
            
            if not result:
                return False, "Sale not found"
            
            original_qty, already_returned = result
            available_to_return = original_qty - already_returned
            
            if return_qty <= 0:
                return False, "Return quantity must be greater than 0"
            
            if return_qty > available_to_return:
                return False, f"Cannot return more than {available_to_return} (original: {original_qty}, already returned: {already_returned})"
            
            return True, available_to_return
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"