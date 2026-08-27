"""
Login UI module for TypeMaster.
Provides LoginView form widgets, inputs validation, and callbacks linking to auth services.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from ui.base import BaseView
from services.auth_service import login_user

class LoginView(BaseView):
    """
    Login screen view panel.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self._build_ui()

    def _build_ui(self):
        """Construct entry items and transition links."""
        # Main grid configurations
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        
        from ui.theme import THEMES
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        form_frame = ctk.CTkFrame(
            self, 
            fg_color=theme_colors["card_bg"],
            corner_radius=12,
            width=360
        )
        form_frame.grid(row=1, column=1, sticky="nsew", pady=10)
        
        # Center Title inside Card
        title_lbl = ctk.CTkLabel(
            form_frame, 
            text="Tizimga Kirish", 
            font=("Segoe UI", 24, "bold"),
            text_color=theme_colors["fg"]
        )
        title_lbl.pack(pady=(30, 20), padx=30, anchor="n")
        
        # Username
        username_label = ctk.CTkLabel(
            form_frame, 
            text="Foydalanuvchi nomi (Username): *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        username_label.pack(anchor="w", padx=30, pady=(5, 2))
        
        self.username_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.username_var, 
            width=300,
            height=36,
            fg_color=theme_colors["bg"],
            text_color=theme_colors["fg"],
            border_color=theme_colors["border"],
            corner_radius=8
        )
        self.username_entry.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Password
        password_label = ctk.CTkLabel(
            form_frame, 
            text="Parol: *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        password_label.pack(anchor="w", padx=30, pady=(5, 2))
        
        self.password_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.password_var, 
            show="*", 
            width=300,
            height=36,
            fg_color=theme_colors["bg"],
            text_color=theme_colors["fg"],
            border_color=theme_colors["border"],
            corner_radius=8
        )
        self.password_entry.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Error Label
        self.error_label = ctk.CTkLabel(
            form_frame, 
            text="", 
            font=("Segoe UI", 11),
            text_color="#ef4444"
        )
        self.error_label.pack(anchor="w", padx=30, pady=5)
        
        # Buttons Container (with Card/Elevated Frame background)
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent", corner_radius=0)
        btn_frame.pack(fill=tk.X, padx=30, pady=(15, 30))
        
        self.login_button = ctk.CTkButton(
            btn_frame,
            text="Kirish",
            fg_color=theme_colors["accent"],
            hover_color=theme_colors["select_bg"],
            text_color=theme_colors["bg"],
            font=("Segoe UI", 12, "bold"),
            height=36,
            corner_radius=8,
            command=self.handle_login
        )
        self.login_button.pack(side="left", padx=(0, 10))
        
        self.register_link = ctk.CTkLabel(
            btn_frame,
            text="Ro'yxatdan o'tish",
            font=("Segoe UI", 11, "underline"),
            text_color=theme_colors["accent"],
            cursor="hand2"
        )
        self.register_link.pack(side="left", padx=10)
        self.register_link.bind("<Button-1>", lambda e: self.navigate_to_register())

    def handle_login(self):
        """Invoke auth login service and trigger transitions using background thread."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        self.error_label.configure(text="", text_color="#ef4444")
        
        if not username:
            self.error_label.configure(text="Foydalanuvchi nomi kiritilishi shart!")
            return
            
        if not password:
            self.error_label.configure(text="Parol kiritilishi shart!")
            return
            
        # Disable button and update text to show loading state
        self.login_button.configure(state="disabled", text="Kutilmoqda...")
        
        import threading
        def worker():
            user = login_user(username, password)
            self.after(0, self._on_login_complete, user, username)
            
        threading.Thread(target=worker, daemon=True).start()

    def _on_login_complete(self, user, username):
        """Callback executed on main UI thread upon background login completion."""
        self.login_button.configure(state="normal", text="Kirish")
        if user:
            messagebox.showinfo("Muvaffaqiyatli", f"Xush kelibsiz, {user.get('display_name', username)}!")
            self.clear_form()
            # Redirect to home shell
            self.controller.show_view("home")
        else:
            self.error_label.configure(text="Foydalanuvchi nomi yoki parol noto'g'ri!")

    def navigate_to_register(self):
        """Transition back to registration view."""
        self.clear_form()
        self.controller.show_view("register")

    def clear_form(self):
        """Reset forms entry variables."""
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.configure(text="")
