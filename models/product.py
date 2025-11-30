from models.base import AutoParts


class Product(AutoParts):
    """Represents a product in the inventory"""

    def __init__(self, id=None, name="", price=0.0, stock=0, category="", brand="",
                 vehicle_model="", part_category="", part_subcategory="", year_range=""):
        super().__init__()
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
        """Convert product to dictionary for database operations"""
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

    @classmethod
    def from_dict(cls, data):
        """Create Product instance from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            price=data.get('price', 0.0),
            stock=data.get('stock', 0),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            vehicle_model=data.get('vehicle_model', ''),
            part_category=data.get('part_category', ''),
            part_subcategory=data.get('part_subcategory', ''),
            year_range=data.get('year_range', '')
        )
