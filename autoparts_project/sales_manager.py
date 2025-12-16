from utils import *
from database import Database

# SALES MANAGER CLASS
# ============================================================================
class SalesManager(AutoParts):
    """Manages sales operations"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.db = Database()
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        return f"INV{self.get_current_time().strftime('%Y%m%d%H%M%S')}"
    
    def generate_return_number(self):
        """Generate unique return number"""
        return f"RET{self.get_current_time().strftime('%Y%m%d%H%M%S')}"
    
    def process_sale(self):
        """Process the sale"""
        if not self.app.cart:
            messagebox.showwarning("Warning", "Cart is empty!")
            return
        try:
            conn = self.db.get_db()
            cur = conn.cursor()
            invoice_number = self.generate_invoice_number()
            customer_name = self.app.customer_entry.get() or "Walk-in Customer"
            notes = self.app.notes_entry.get()
            for cart_item in self.app.cart:
                # Record sale  
                cur.execute("""INSERT INTO sales 
                            (invoice, item, qty, subtotal, date, notes, customer_name, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (invoice_number, cart_item['name'], cart_item['qty'], cart_item['subtotal'],
                             self.get_current_time().strftime('%Y-%m-%d %H:%M:%S'), notes, customer_name, "COMPLETED"))
                # Update inventory stock
                cur.execute("UPDATE inventory SET stock = stock - ? WHERE id = ?",
                            (cart_item['qty'], cart_item['id']))
            conn.commit()
            conn.close()
            # Generate receipt
            self.generate_receipt(invoice_number, customer_name, notes)
            messagebox.showinfo("Sale Completed",
                                f"Sale processed successfully!\nInvoice: {invoice_number}\nTotal: ₱{sum(item['subtotal'] for item in self.app.cart):.2f}")
            # Clear cart
            self.app.cart = []
            if hasattr(self.app, 'customer_entry'):
                self.app.customer_entry.delete(0, 'end')
            if hasattr(self.app, 'notes_entry'):
                self.app.notes_entry.delete(0, 'end')
            
            # Refresh dashboard
            if hasattr(self.app, 'content_frame'):
                self.app.show_dashboard()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not process sale: {str(e)}")
    
    def generate_receipt(self, invoice_number, customer_name, notes):
        """Generate and display a receipt for the sale"""
        receipt_window = ctk.CTkToplevel(self.app.root)
        receipt_window.title("Sales Receipt")
        receipt_window.geometry("600x700")
        receipt_window.transient(self.app.root)
        receipt_window.grab_set()
        # Create receipt frame
        receipt_frame = ctk.CTkFrame(receipt_window)
        receipt_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Receipt header
        header_frame = ctk.CTkFrame(receipt_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(header_frame, text="AUTO PARTS STORE",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=5)
        ctk.CTkLabel(header_frame, text="Official Sales Receipt",
                     font=ctk.CTkFont(size=16)).pack(pady=2)
        ctk.CTkLabel(header_frame, text="123 Main Street, City, Philippines",
                     font=ctk.CTkFont(size=12)).pack(pady=2)
        ctk.CTkLabel(header_frame, text="Tel: (02) 1234-5678",
                     font=ctk.CTkFont(size=12)).pack(pady=2)
        # Separator
        separator = ctk.CTkFrame(header_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=10)
        # Receipt details
        details_frame = ctk.CTkFrame(receipt_frame)
        details_frame.pack(fill="x", padx=10, pady=5)
        # Invoice and date
        ctk.CTkLabel(details_frame, text=f"Invoice: {invoice_number}",
                     font=ctk.CTkFont(size=12, weight="bold"), justify="left").pack(anchor="w")
        ctk.CTkLabel(details_frame, text=f"Date: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}",
                     font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")
        ctk.CTkLabel(details_frame, text=f"Customer: {customer_name}",
                     font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")
        if notes:
            ctk.CTkLabel(details_frame, text=f"Notes: {notes}",
                         font=ctk.CTkFont(size=12), justify="left").pack(anchor="w")
        # Items table
        items_frame = ctk.CTkFrame(receipt_frame)
        items_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Create table header
        header_frame = ctk.CTkFrame(items_frame)
        header_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(header_frame, text="Item", width=200,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Qty", width=60,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Price", width=80,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Subtotal", width=100,
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
        # Add items to receipt
        total_amount = 0
        for item in self.app.cart:
            item_frame = ctk.CTkFrame(items_frame)
            item_frame.pack(fill="x", pady=2)
            # Item name (truncate if too long)
            item_name = item['name']
            if len(item_name) > 25:
                item_name = item_name[:22] + "..."
            ctk.CTkLabel(item_frame, text=item_name, width=200,
                         justify="left").pack(side="left", padx=2)
            ctk.CTkLabel(item_frame, text=str(
                item['qty']), width=60).pack(side="left", padx=2)
            ctk.CTkLabel(item_frame, text=f"₱{item['price']:.2f}", width=80).pack(
                side="left", padx=2)
            ctk.CTkLabel(item_frame, text=f"₱{item['subtotal']:.2f}", width=100).pack(
                side="left", padx=2)
            
            total_amount += item['subtotal']
        # Total section
        total_frame = ctk.CTkFrame(receipt_frame)
        total_frame.pack(fill="x", padx=10, pady=10)
        separator = ctk.CTkFrame(total_frame, height=2, fg_color="gray")
        separator.pack(fill="x", pady=5)
        ctk.CTkLabel(total_frame, text=f"TOTAL: ₱{total_amount:>38.2f}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        # Footer
        footer_frame = ctk.CTkFrame(receipt_frame)
        footer_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(footer_frame, text="Thank you for your business!",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)
        ctk.CTkLabel(footer_frame, text="Please keep this receipt for returns",
                     font=ctk.CTkFont(size=10)).pack(pady=2)
        # Action buttons
        button_frame = ctk.CTkFrame(receipt_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(button_frame, text="Save Receipt",
                      command=lambda: self.save_receipt_to_file(invoice_number, customer_name, notes, total_amount),
                      fg_color="#0984e3", hover_color="#0971c2").pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="Close",
                      command=receipt_window.destroy,
                      fg_color="#e74c3c", hover_color="#c0392b").pack(side="right", padx=5)
    
    def save_receipt_to_file(self, invoice_number, customer_name, notes, total_amount):
        """Save receipt to a text file"""
        try:
            default_filename = f"receipt_{invoice_number}_{self.get_current_time().strftime('%Y%m%d_%H%M%S')}.txt"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename,
                title="Save Receipt As"
            )
            
            if filename:
                receipt_text = self.generate_receipt_text(invoice_number, customer_name, notes, total_amount)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(receipt_text)
                
                messagebox.showinfo("Success", f"Receipt saved successfully to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save receipt: {str(e)}")
    
    def generate_receipt_text(self, invoice_number, customer_name, notes, total_amount):
        """Generate receipt as text string"""
        receipt = "=" * 50 + "\n"
        receipt += "         AUTO PARTS STORE\n"
        receipt += "       Official Sales Receipt\n"
        receipt += "   123 Main Street, City, Philippines\n"
        receipt += "          Tel: (02) 1234-5678\n"
        receipt += "=" * 50 + "\n\n"
        receipt += f"Invoice: {invoice_number}\n"
        receipt += f"Date: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}\n"
        receipt += f"Customer: {customer_name}\n"
        if notes:
            receipt += f"Notes: {notes}\n"
        receipt += "\n" + "-" * 50 + "\n"
        receipt += "ITEM                            QTY   PRICE   SUBTOTAL\n"
        receipt += "-" * 50 + "\n"
        for item in self.app.cart:
            item_name = item['name']
            if len(item_name) > 30:
                item_name = item_name[:27] + "..."
            receipt += f"{item_name:<30} {item['qty']:>3}  ₱{item['price']:>6.2f}  ₱{item['subtotal']:>7.2f}\n"
        receipt += "-" * 50 + "\n"
        receipt += f"TOTAL: ₱{total_amount:>38.2f}\n"
        receipt += "=" * 50 + "\n\n"
        receipt += "RETURN POLICY:\n"
        receipt += "• Returns accepted within 7 days\n"
        receipt += "• Original receipt required\n"
        receipt += "• Items must be in original condition\n"
        receipt += "• No returns on installed parts\n\n"
        receipt += "Thank you for your business!\n"
        receipt += "Please keep this receipt for returns\n"
        receipt += "=" * 50 + "\n"
        return receipt
# ============================================================================
