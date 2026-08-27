"""
Registration UI module for TypeMaster.
Provides RegisterView form widgets, client-side input validations, and navigation handles.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from ui.base import BaseView

class RegisterView(BaseView):
    """
    Form view for user registration.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        
        # Setup local UI variables
        self.username_var = tk.StringVar()
        self.display_name_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        self._build_ui()

    def _build_ui(self):
        """Construct form grids and styling widgets."""
        # Top Grid Spacer
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        
        from ui.theme import THEMES
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Container frame for form fields (to keep them centered)
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
            text="Ro'yxatdan O'tish", 
            font=("Segoe UI", 24, "bold"),
            text_color=theme_colors["fg"]
        )
        title_lbl.pack(pady=(30, 20), padx=30, anchor="n")
        
        # Username Field
        username_lbl = ctk.CTkLabel(
            form_frame, 
            text="Foydalanuvchi nomi (Username): *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        username_lbl.pack(anchor="w", padx=30, pady=(5, 2))
        
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
        
        # Display Name Field
        display_name_lbl = ctk.CTkLabel(
            form_frame, 
            text="Ko'rinadigan ism (Display Name):", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        display_name_lbl.pack(anchor="w", padx=30, pady=(5, 2))
        
        self.display_name_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.display_name_var, 
            width=300,
            height=36,
            fg_color=theme_colors["bg"],
            text_color=theme_colors["fg"],
            border_color=theme_colors["border"],
            corner_radius=8
        )
        self.display_name_entry.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Password Field
        password_lbl = ctk.CTkLabel(
            form_frame, 
            text="Parol: *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        password_lbl.pack(anchor="w", padx=30, pady=(5, 2))
        
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
        
        # Confirm Password Field
        confirm_password_lbl = ctk.CTkLabel(
            form_frame, 
            text="Parolni tasdiqlang: *", 
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        confirm_password_lbl.pack(anchor="w", padx=30, pady=(5, 2))
        
        self.confirm_password_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.confirm_password_var, 
            show="*", 
            width=300,
            height=36,
            fg_color=theme_colors["bg"],
            text_color=theme_colors["fg"],
            border_color=theme_colors["border"],
            corner_radius=8
        )
        self.confirm_password_entry.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        # Feedback/Error Label
        self.error_label = ctk.CTkLabel(
            form_frame, 
            text="", 
            font=("Segoe UI", 11),
            text_color="#ef4444"
        )
        self.error_label.pack(anchor="w", padx=30, pady=5)
        
        # Buttons Container inside form_frame
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent", corner_radius=0)
        btn_frame.pack(fill=tk.X, padx=30, pady=(15, 30))
        
        # Register Action Button
        self.register_button = ctk.CTkButton(
            btn_frame,
            text="Ro'yxatdan o'tish",
            fg_color=theme_colors["accent"],
            hover_color=theme_colors["select_bg"],
            text_color=theme_colors["bg"],
            font=("Segoe UI", 12, "bold"),
            height=36,
            corner_radius=8,
            command=self.handle_register
        )
        self.register_button.pack(side="left", padx=(0, 10))
        
        # Login Redirect Link Label (simulated)
        self.login_link = ctk.CTkLabel(
            btn_frame,
            text="Tizimga kirish",
            font=("Segoe UI", 11, "underline"),
            text_color=theme_colors["accent"],
            cursor="hand2"
        )
        self.login_link.pack(side="left", padx=10)
        
        # Bind link click to trigger navigation stub
        self.login_link.bind("<Button-1>", lambda e: self.navigate_to_login())

    def validate_inputs(self) -> bool:
        """
        Runs client-side form validations.
        Updates self.error_label and yields success boolean status.
        """
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()
        
        # Clean previous error state
        self.error_label.configure(text="", text_color="#ef4444")
        
        # Username Check
        if not username:
            self.error_label.configure(text="Foydalanuvchi nomi kiritilishi shart!")
            return False
            
        # Password Check
        if not password:
            self.error_label.configure(text="Parol kiritilishi shart!")
            return False
            
        if len(password) < 6:
            self.error_label.configure(text="Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
            return False
            
        if password != confirm_password:
            self.error_label.configure(text="Parollar o'zaro mos kelmadi!")
            return False
            
        return True

    def handle_register(self):
        """Processes form inputs and executes validation success flows in background."""
        if not self.validate_inputs():
            return
            
        username = self.username_var.get().strip()
        display_name = self.display_name_var.get().strip()
        password = self.password_var.get().strip()
        
        self.register_button.configure(state="disabled", text="Kutilmoqda...")
        
        from services.auth_service import register_user
        import threading
        
        def worker():
            try:
                register_user(username, display_name, password)
                self.after(0, self._on_register_success, username)
            except ValueError as err:
                self.after(0, self._on_register_error, str(err))
            except Exception as err:
                self.after(0, self._on_register_error, f"Tizim xatoligi: {err}")
                
        threading.Thread(target=worker, daemon=True).start()

    def _on_register_success(self, username):
        """Callback for successful user registration."""
        self.register_button.configure(state="normal", text="Ro'yxatdan o'tish")
        messagebox.showinfo(
            "Muvaffaqiyatli",
            f"Foydalanuvchi '{username}' tizimga muvaffaqiyatli ro'yxatdan o'tdi!"
        )
        self.clear_form()
        self.controller.show_view("login")

    def _on_register_error(self, error_message):
        """Callback for registration failures."""
        self.register_button.configure(state="normal", text="Ro'yxatdan o'tish")
        self.error_label.configure(text=error_message, text_color="#ef4444")

    def navigate_to_login(self):
        """Link navigation stub hook."""
        self.error_label.configure(text="Login sahifasiga o'tish bosildi.", text_color="#3b82f6")
        try:
            self.controller.show_view("login")
        except Exception:
            pass

    def clear_form(self):
        """Cleans input buffers."""
        self.username_var.set("")
        self.display_name_var.set("")
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.error_label.configure(text="")
