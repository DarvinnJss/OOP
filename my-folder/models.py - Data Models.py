import datetime

class Product:
    """Represents a product in the inventory"""
    def __init__(self, id=None, name="", price=0.0, stock=0, category="", brand="",
                 vehicle_model="", part_category="", part_subcategory="", year_range=""):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.brand = brand
        self.vehicle_model = vehicle_model
        self.part_category = part_category
        self.part_subcategory = part_subcategory
        self.year_range = year_range

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'brand': self.brand,
            'vehicle_model': self.vehicle_model,
            'part_category': self.part_category,
            'part_subcategory': self.part_subcategory,
            'year_range': self.year_range
        }

class CartItem:
    """Represents an item in the shopping cart"""
    def __init__(self, product_id, name, price, quantity=1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def subtotal(self):
        return self.price * self.quantity

    def to_dict(self):
        return {
            'id': self.product_id,
            'name': self.name,
            'price': self.price,
            'qty': self.quantity,
            'subtotal': self.subtotal
        }

class Sale:
    """Represents a sales transaction"""
    def __init__(self, invoice_number="", customer_name="", notes="", status="COMPLETED"):
        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.notes = notes
        self.status = status
        self.date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.items = []
        self.total_amount = 0.0

    def add_item(self, product_name, quantity, subtotal):
        self.items.append({
            'item': product_name,
            'qty': quantity,
            'subtotal': subtotal
        })
        self.total_amount += subtotal

    def to_dict(self):
        return {
            'invoice': self.invoice_number,
            'customer_name': self.customer_name,
            'notes': self.notes,
            'status': self.status,
            'date': self.date,
            'total_amount': self.total_amount,
            'items': self.items
        }

class User:
    """Represents a system user"""
    def __init__(self, id=None, username="", password=""):
        self.id = id
        self.username = username
        self.password = password

    def authenticate(self, input_username, input_password):
        return self.username == input_username and self.password == input_password