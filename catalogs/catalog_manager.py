import sqlite3
from database.db_connection import get_db
from catalogs.toyota_catalog import TOYOTA_PARTS_CATALOG
from catalogs.honda_catalog import HONDA_PARTS_CATALOG
from catalogs.mitsubishi_catalog import MITSUBISHI_PARTS_CATALOG
from catalogs.ford_catalog import FORD_PARTS_CATALOG
from catalogs.nissan_catalog import NISSAN_PARTS_CATALOG
from catalogs.hyundai_catalog import HYUNDAI_PARTS_CATALOG


class CatalogManager:
    """Manages catalog operations"""

    @staticmethod
    def add_all_toyota_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(TOYOTA_PARTS_CATALOG, "Toyota")

    @staticmethod
    def add_all_honda_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(HONDA_PARTS_CATALOG, "Honda")

    @staticmethod
    def add_all_mitsubishi_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(MITSUBISHI_PARTS_CATALOG, "Mitsubishi")

    @staticmethod
    def add_all_ford_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(FORD_PARTS_CATALOG, "Ford")

    @staticmethod
    def add_all_nissan_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(NISSAN_PARTS_CATALOG, "Nissan")

    @staticmethod
    def add_all_hyundai_parts_to_inventory():
        return CatalogManager._add_catalog_to_inventory(HYUNDAI_PARTS_CATALOG, "Hyundai")

    @staticmethod
    def _add_catalog_to_inventory(catalog, brand):
        """Add catalog parts to inventory"""
        try:
            conn = get_db()
            cur = conn.cursor()

            added_count = 0
            for model, categories in catalog.items():
                for category, subcategories in categories.items():
                    for subcategory, parts in subcategories.items():
                        for part_name, part_info in parts.items():
                            # Create a unique identifier for each product
                            unique_name = f"{part_name} - {model.title()} - {part_info['years']}"

                            cur.execute(
                                "SELECT id FROM inventory WHERE name = ? AND brand = ? AND vehicle_model = ?",
                                (unique_name, brand, model)
                            )
                            if not cur.fetchone():
                                cur.execute("""
                                    INSERT INTO inventory 
                                    (name, price, stock, category, brand, vehicle_model, 
                                     part_category, part_subcategory, year_range)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    unique_name,
                                    part_info['price'],
                                    50,
                                    f"{brand} Parts",
                                    brand,
                                    model,
                                    category,
                                    subcategory,
                                    part_info['years']
                                ))
                                added_count += 1

            conn.commit()
            conn.close()
            print(f"✅ Added {added_count} {brand} parts to inventory")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error adding {brand} parts: {e}")
            return False
