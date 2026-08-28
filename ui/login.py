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
        self.form_frame = form_frame
        
        # Center Title inside Card
        self.title_lbl = ctk.CTkLabel(
            form_frame, 
            text="Tizimga Kirish", 
            font=("Segoe UI", 24, "bold"),
            text_color=theme_colors["fg"]
        )
        self.title_lbl.pack(pady=(30, 20), padx=30, anchor="n")
        
        # Username
        self.username_label = ctk.CTkLabel(
            form_frame, 
            text="Foydalanuvchi nomi (Username): *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        self.username_label.pack(anchor="w", padx=30, pady=(5, 2))
        
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
        self.password_label = ctk.CTkLabel(
            form_frame, 
            text="Parol: *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        self.password_label.pack(anchor="w", padx=30, pady=(5, 2))
        
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
        
        from services.i18n_service import t
        if not username:
            self.error_label.configure(text=t("login_err_username_required"))
            return
            
        if not password:
            self.error_label.configure(text=t("login_err_password_required"))
            return
            
        # Disable button and update text to show loading state
        self.login_button.configure(state="disabled", text=t("kutilmoqda") if t("kutilmoqda") != "kutilmoqda" else "Kutilmoqda...")
        
        import threading
        def worker():
            user = login_user(username, password)
            self.after(0, self._on_login_complete, user, username)
            
        threading.Thread(target=worker, daemon=True).start()

    def _on_login_complete(self, user, username):
        """Callback executed on main UI thread upon background login completion."""
        from services.i18n_service import t
        self.login_button.configure(state="normal", text=t("login_btn"))
        if user:
            messagebox.showinfo(t("success_title"), t("login_success_msg").format(name=user.get('display_name', username)))
            self.clear_form()
            # Redirect to home shell
            self.controller.show_view("home")
        else:
            self.error_label.configure(text=t("login_err_invalid_credentials"))

    def navigate_to_register(self):
        """Transition back to registration view."""
        self.clear_form()
        self.controller.show_view("register")

    def clear_form(self):
        """Reset forms entry variables."""
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.configure(text="")

    def retranslate_ui(self):
        """Dynamic text configuration mapping for login view form labels and redirect link."""
        from services.i18n_service import t
        if hasattr(self, "title_lbl") and self.title_lbl:
            self.title_lbl.configure(text=t("login_title"))
        if hasattr(self, "username_label") and self.username_label:
            self.username_label.configure(text=t("login_username") + ": *")
        if hasattr(self, "password_label") and self.password_label:
            self.password_label.configure(text=t("login_password") + ": *")
        if hasattr(self, "login_button") and self.login_button:
            if self.login_button.cget("state") == "normal":
                self.login_button.configure(text=t("login_btn"))
        if hasattr(self, "register_link") and self.register_link:
            self.register_link.configure(text=t("login_no_account"))

    def apply_theme(self, theme_name: str):
        """Applies theme variables to active widgets dynamically."""
        from ui.theme import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        
        self.configure(fg_color="transparent")
        if hasattr(self, "form_frame") and self.form_frame:
            self.form_frame.configure(fg_color=theme["card_bg"])
        if hasattr(self, "title_lbl") and self.title_lbl:
            self.title_lbl.configure(text_color=theme["fg"])
        if hasattr(self, "username_label") and self.username_label:
            self.username_label.configure(text_color=theme["secondary_fg"])
        if hasattr(self, "username_entry") and self.username_entry:
            self.username_entry.configure(
                fg_color=theme["bg"],
                text_color=theme["fg"],
                border_color=theme["border"]
            )
        if hasattr(self, "password_label") and self.password_label:
            self.password_label.configure(text_color=theme["secondary_fg"])
        if hasattr(self, "password_entry") and self.password_entry:
            self.password_entry.configure(
                fg_color=theme["bg"],
                text_color=theme["fg"],
                border_color=theme["border"]
            )
        if hasattr(self, "login_button") and self.login_button:
            self.login_button.configure(
                fg_color=theme["accent"],
                hover_color=theme["select_bg"],
                text_color=theme["bg"]
            )
        if hasattr(self, "register_link") and self.register_link:
            self.register_link.configure(text_color=theme["accent"])
