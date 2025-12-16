from utils import *

# GUI MANAGER CLASS
# ============================================================================
class GUIManager(AutoParts):
    """Manages GUI creation and navigation"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = ctk.CTkFrame(self.app.main_container, width=280, fg_color=(
            "#1a1a2e", "#16213e"), corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=(0, 5), pady=10)
        sidebar.pack_propagate(False)
        # User profile section
        user_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        user_frame.pack(pady=30, padx=20, fill="x")
        welcome_label = ctk.CTkLabel(user_frame, text=f"Welcome,", font=ctk.CTkFont(
            size=14), text_color=("#FF9A3D", "#FF9A3D"))
        welcome_label.pack()
        username_label = ctk.CTkLabel(user_frame, text=f"{self.app.current_user[1].title()}!", font=ctk.CTkFont(
            size=18, weight="bold"), text_color=("#FF6B35", "#FF6B35"))
        username_label.pack(pady=5)
        # Navigation section
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=15, pady=20)
        nav_buttons = [
            ("Dashboard", self.app.show_dashboard),
            ("Inventory", self.app.show_inventory),
            ("Trash Bin", self.app.show_trash_bin), 
            ("Point of Sale", self.app.show_pos),
            ("Sales History", self.app.show_sales_history),
            ("Returns", self.app.show_returns),
            ("Settings", self.app.show_settings),
        ]
        for text, command in nav_buttons:
            btn = ctk.CTkButton(nav_frame, text=text, command=command, font=ctk.CTkFont(size=14), anchor="w", height=45,
                                fg_color=("#2d3047", "#2d3047"), hover_color=("#FF6B35", "#FF6B35"), text_color="white", corner_radius=10)
            btn.pack(fill="x", pady=8)
        # Logout button
        logout_btn = ctk.CTkButton(sidebar, text="🚪 Logout", command=self.app.logout, font=ctk.CTkFont(size=14, weight="bold"),
                                   height=45, fg_color=("#e74c3c", "#c0392b"), hover_color=("#ff7979", "#e74c3c"), corner_radius=10)
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)
        
        return sidebar
    
    def show_login_screen(self):
        """Display the login screen"""
        self.app.clear_screen()
        # Main container
        login_container = ctk.CTkFrame(
            self.app.main_container, fg_color=("white", "#1a1a2e"))
        login_container.pack(expand=True, fill="both", padx=150, pady=80)
        # Header
        header_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        header_frame.pack(pady=(40, 30))
        title_label = ctk.CTkLabel(
            header_frame, text="Auto Parts Pro", font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=5)
        subtitle_label = ctk.CTkLabel(
            header_frame, text="Admin System", font=ctk.CTkFont(size=18), text_color="#FF6B35")
        subtitle_label.pack()
        decor_line = ctk.CTkFrame(
            header_frame, height=3, fg_color="#FF6B35", width=100)
        decor_line.pack(pady=10)
        # Form
        form_frame = ctk.CTkFrame(login_container, fg_color=(
            "#f8f9fa", "#2d3047"), corner_radius=20, border_width=2, border_color=("#FF6B35", "#FF9A3D"))
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)
        form_title = ctk.CTkLabel(
            form_frame, text="Welcome Back!", font=ctk.CTkFont(size=22, weight="bold"))
        form_title.pack(pady=(30, 20))
        # Username
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.pack(pady=15, padx=40, fill="x")
        ctk.CTkLabel(username_frame, text="👤 Username", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w")
        username_entry = ctk.CTkEntry(username_frame, height=45, placeholder_text="Enter your username", font=ctk.CTkFont(
            size=14), border_width=2, border_color=("#FF6B35", "#FF9A3D"), corner_radius=12)
        username_entry.pack(pady=(8, 0), fill="x")
        username_entry.insert(0, "autoparts")
        # Password
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(pady=15, padx=40, fill="x")
        ctk.CTkLabel(password_frame, text="🔒 Password", font=ctk.CTkFont(
            size=14, weight="bold")).pack(anchor="w")
        password_entry = ctk.CTkEntry(password_frame, height=45, placeholder_text="Enter your password", show="•", font=ctk.CTkFont(
            size=14), border_width=2, border_color=("#FF6B35", "#FF9A3D"), corner_radius=12)
        password_entry.pack(pady=(8, 0), fill="x")
        password_entry.insert(0, "oilengine")
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=(30, 20), padx=40, fill="x")
        login_btn = ctk.CTkButton(button_frame, text="🚀 Login to Dashboard", 
                                 command=lambda: self.app.login(username_entry, password_entry), 
                                 font=ctk.CTkFont(size=16, weight="bold"), height=50, 
                                 fg_color=("#FF6B35", "#FF9A3D"), hover_color=("#E55A30", "#FF8C2D"), 
                                 corner_radius=12)
        login_btn.pack(fill="x", pady=10)
        # Footer
        footer_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        footer_frame.pack(pady=(20, 30))
        dots_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        dots_frame.pack()
        colors = ["#FF6B35", "#FF9A3D", "#2d3047", "#4a4e69"]
        for color in colors:
            dot = ctk.CTkFrame(dots_frame, width=8, height=8,
                               fg_color=color, corner_radius=4)
            dot.pack(side="left", padx=3)
        footer_text = ctk.CTkLabel(footer_frame, text="Auto Parts Management System v2.0", 
                                   font=ctk.CTkFont(size=12), text_color=("#7f8c8d", "#bdc3c7"))
        footer_text.pack(pady=10)
        self.app.root.after(100, lambda: username_entry.focus())
        self.apply_theme(self.app.root)
# ============================================================================
