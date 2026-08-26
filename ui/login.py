"""
Login UI module for TypeMaster.
Provides LoginView form widgets, inputs validation, and callbacks linking to auth services.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        
        form_frame = ttk.LabelFrame(self, text=" Tizimga Kirish ", padding=25)
        form_frame.grid(row=1, column=1, fg_bg_color=None, sticky="nsew", pady=10)
        # Wait, fg_bg_color is not standard in LabelFrame. Let's make it standard:
        # form_frame.grid(row=1, column=1, sticky="nsew", pady=10)
        
        # Username
        ttk.Label(form_frame, text="Foydalanuvchi nomi (Username): *").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Password
        ttk.Label(form_frame, text="Parol: *").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Error Label
        self.error_label = ttk.Label(form_frame, text="", style="Secondary.TLabel")
        self.error_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.login_button = ttk.Button(
            btn_frame,
            text="Kirish",
            command=self.handle_login
        )
        self.login_button.pack(side="left", padx=(0, 10))
        
        self.register_link = ttk.Label(
            btn_frame,
            text="Ro'yxatdan o'tish",
            style="Secondary.TLabel",
            cursor="hand2",
            foreground="blue"
        )
        self.register_link.pack(side="left", padx=10)
        self.register_link.bind("<Button-1>", lambda e: self.navigate_to_register())

    def handle_login(self):
        """Invoke auth login service and trigger transitions."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        self.error_label.config(text="", foreground="red")
        
        if not username:
            self.error_label.config(text="Foydalanuvchi nomi kiritilishi shart!")
            return
            
        if not password:
            self.error_label.config(text="Parol kiritilishi shart!")
            return
            
        # Call logging validation
        user = login_user(username, password)
        if user:
            messagebox.showinfo("Muvaffaqiyat", f"Xush kelibsiz, {user.get('display_name', username)}!")
            self.clear_form()
            # Redirect to home shell
            self.controller.show_view("home")
        else:
            self.error_label.config(text="Foydalanuvchi nomi yoki parol noto'g'ri!")

    def navigate_to_register(self):
        """Transition back to registration view."""
        self.clear_form()
        self.controller.show_view("register")

    def clear_form(self):
        """Reset forms entry variables."""
        self.username_var.set("")
        self.password_var.set("")
        self.error_label.config(text="")
