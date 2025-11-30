import customtkinter as ctk
from catalogs.toyota_catalog import TOYOTA_PARTS_CATALOG
from catalogs.honda_catalog import HONDA_PARTS_CATALOG
from catalogs.mitsubishi_catalog import MITSUBISHI_PARTS_CATALOG
from catalogs.ford_catalog import FORD_PARTS_CATALOG
from catalogs.nissan_catalog import NISSAN_PARTS_CATALOG
from catalogs.hyundai_catalog import HYUNDAI_PARTS_CATALOG


class CatalogScreen:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        self.create_widgets()
        self.load_brand_catalog_modern()

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)

        title_label = ctk.CTkLabel(header_frame, text="🚗 PARTS CATALOG",
                                   font=ctk.CTkFont(size=28, weight="bold"),
                                   text_color="#FF6B35")
        title_label.pack(side="left")

        # Brand selector
        brand_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        brand_frame.pack(side="right", padx=10)

        ctk.CTkLabel(brand_frame, text="Select Brand:",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        brands = ["Toyota", "Honda", "Mitsubishi", "Ford", "Nissan", "Hyundai"]
        self.brand_var = ctk.StringVar(value="Toyota")
        brand_combo = ctk.CTkComboBox(brand_frame, values=brands,
                                      variable=self.brand_var,
                                      command=self.load_brand_catalog_modern,
                                      width=150, height=35,
                                      fg_color="#2d3047",
                                      border_color="#FF6B35",
                                      button_color="#FF6B35",
                                      button_hover_color="#E55A30")
        brand_combo.pack(side="left", padx=5)

        # Main catalog container
        self.catalog_container = ctk.CTkScrollableFrame(
            self.parent, fg_color="transparent")
        self.catalog_container.pack(fill="both", expand=True, padx=20, pady=10)

    def load_brand_catalog_modern(self, brand=None):
        if not brand:
            brand = self.brand_var.get()

        # Clear previous content
        for widget in self.catalog_container.winfo_children():
            widget.destroy()

        catalogs = {
            "Toyota": TOYOTA_PARTS_CATALOG,
            "Honda": HONDA_PARTS_CATALOG,
            "Mitsubishi": MITSUBISHI_PARTS_CATALOG,
            "Ford": FORD_PARTS_CATALOG,
            "Nissan": NISSAN_PARTS_CATALOG,
            "Hyundai": HYUNDAI_PARTS_CATALOG
        }

        catalog = catalogs.get(brand, {})

        for model, categories in catalog.items():
            # Model section header
            model_frame = ctk.CTkFrame(self.catalog_container,
                                       fg_color="#2d3047",
                                       corner_radius=15,
                                       border_width=2,
                                       border_color="#FF6B35")
            model_frame.pack(fill="x", pady=10, padx=5)

            model_label = ctk.CTkLabel(model_frame,
                                       text=f"🚗 {model.upper()}",
                                       font=ctk.CTkFont(
                                           size=20, weight="bold"),
                                       text_color="#FF6B35")
            model_label.pack(pady=15)

            # Categories
            for category, subcategories in categories.items():
                category_frame = ctk.CTkFrame(self.catalog_container,
                                              fg_color="#1a1a2e",
                                              corner_radius=12)
                category_frame.pack(fill="x", pady=8, padx=10)

                # Category header
                category_header = ctk.CTkFrame(category_frame,
                                               fg_color="#FF6B35",
                                               corner_radius=10)
                category_header.pack(fill="x", padx=10, pady=10)

                ctk.CTkLabel(category_header,
                             text=f"📁 {category.replace('_', ' ').title()}",
                             font=ctk.CTkFont(size=16, weight="bold"),
                             text_color="white").pack(pady=8)

                # Subcategories and products
                for subcategory, parts in subcategories.items():
                    subcat_frame = ctk.CTkFrame(category_frame,
                                                fg_color="transparent")
                    subcat_frame.pack(fill="x", padx=20, pady=10)

                    ctk.CTkLabel(subcat_frame,
                                 text=f"🔧 {subcategory.replace('_', ' ').title()}",
                                 font=ctk.CTkFont(size=14, weight="bold"),
                                 text_color="#FF9A3D").pack(anchor="w", pady=5)

                    # Products grid
                    products_frame = ctk.CTkFrame(subcat_frame,
                                                  fg_color="transparent")
                    products_frame.pack(fill="x", padx=10)

                    for part_name, part_info in parts.items():
                        product_card = self.create_product_card(products_frame,
                                                                part_name,
                                                                part_info,
                                                                brand,
                                                                model)
                        product_card.pack(fill="x", pady=5, padx=5)

    def create_product_card(self, parent, part_name, part_info, brand, model):
        card = ctk.CTkFrame(parent,
                            fg_color=("#ffffff", "#4a4e69"),
                            corner_radius=10,
                            border_width=1,
                            border_color=("#FF6B35", "#FF9A3D"))

        # Product info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)

        # Product name and price
        name_price_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_price_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(name_price_frame,
                     text=part_name,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=("#2d3047", "white")).pack(side="left")

        price_label = ctk.CTkLabel(name_price_frame,
                                   text=f"₱{part_info['price']:.2f}",
                                   font=ctk.CTkFont(size=14, weight="bold"),
                                   text_color="#00b894")
        price_label.pack(side="right")

        # Compatibility info
        compat_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        compat_frame.pack(fill="x", pady=3)

        ctk.CTkLabel(compat_frame,
                     text=f"📋 Models: {part_info['models']}",
                     font=ctk.CTkFont(size=11),
                     text_color=("#7f8c8d", "#bdc3c7")).pack(anchor="w")

        ctk.CTkLabel(compat_frame,
                     text=f"📅 Years: {part_info['years']}",
                     font=ctk.CTkFont(size=11),
                     text_color=("#7f8c8d", "#bdc3c7")).pack(anchor="w")

        # Add to cart button
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=10)

        add_btn = ctk.CTkButton(button_frame,
                                text="🛒 Add to POS",
                                command=lambda pn=part_name, pi=part_info, b=brand, m=model:
                                self.add_catalog_to_cart(pn, pi, b, m),
                                height=35,
                                fg_color="#0984e3",
                                hover_color="#0971c2",
                                font=ctk.CTkFont(size=12, weight="bold"))
        add_btn.pack(fill="x")

        return card

    def add_catalog_to_cart(self, part_name, part_info, brand, model):
        cart_product_name = f"{part_name} - {model.title()} - {part_info['years']}"

        self.app.show_pos()

        self.app.oop_cart.add_item(
            f"{brand}_{model}_{part_name}",
            cart_product_name,
            part_info['price'],
            1
        )

        self.app.cart = self.app.oop_cart.to_legacy_format()

        # Update cart display if POS screen is active
        if hasattr(self.app, 'pos_screen'):
            self.app.pos_screen.update_cart_display()

        from tkinter import messagebox
        messagebox.showinfo("Success", f"Added {part_name} to cart!")
