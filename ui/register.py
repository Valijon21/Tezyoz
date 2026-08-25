"""
Registration UI module for TypeMaster.
Provides RegisterView form widgets, client-side input validations, and navigation handles.
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        
        # Container frame for form fields (to keep them centered)
        form_frame = ttk.LabelFrame(self, text=" Ro'yxatdan O'tish ", padding=25)
        form_frame.grid(row=1, column=1, sticky="nsew", pady=10)
        
        # Username Field
        ttk.Label(form_frame, text="Foydalanuvchi nomi (Username): *", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, font=("Helvetica", 11), width=30)
        self.username_entry.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)
        
        # Display Name Field
        ttk.Label(form_frame, text="Ko'rinadigan ism (Display Name):", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.display_name_entry = ttk.Entry(form_frame, textvariable=self.display_name_var, font=("Helvetica", 11), width=30)
        self.display_name_entry.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Password Field
        ttk.Label(form_frame, text="Parol: *", font=("Helvetica", 11)).grid(row=4, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", font=("Helvetica", 11), width=30)
        self.password_entry.grid(row=5, column=0, columnspan=2, sticky="w", pady=5)
        
        # Confirm Password Field
        ttk.Label(form_frame, text="Parolni tasdiqlang: *", font=("Helvetica", 11)).grid(row=6, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(form_frame, textvariable=self.confirm_password_var, show="*", font=("Helvetica", 11), width=30)
        self.confirm_password_entry.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)
        
        # Feedback/Error Label
        self.error_label = ttk.Label(form_frame, text="", font=("Helvetica", 10, "italic"))
        self.error_label.grid(row=8, column=0, columnspan=2, sticky="w", pady=5)
        
        # Buttons Container inside form_frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Register Action Button
        self.register_button = ttk.Button(
            btn_frame,
            text="Ro'yxatdan o'tish",
            command=self.handle_register
        )
        self.register_button.pack(side="left", padx=(0, 10))
        
        # Login Redirect Link Label (simulated)
        self.login_link = ttk.Label(
            btn_frame,
            text="Tizimga kirish",
            font=("Helvetica", 10, "underline"),
            cursor="hand2",
            foreground="blue"
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
        self.error_label.config(text="", foreground="red")
        
        # Username Check
        if not username:
            self.error_label.config(text="Foydalanuvchi nomi kiritilishi shart!")
            return False
            
        # Password Check
        if not password:
            self.error_label.config(text="Parol kiritilishi shart!")
            return False
            
        if len(password) < 6:
            self.error_label.config(text="Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
            return False
            
        if password != confirm_password:
            self.error_label.config(text="Parollar o'zaro mos kelmadi!")
            return False
            
        return True

    def handle_register(self):
        """Processes form inputs and executes validation success flows."""
        if not self.validate_inputs():
            return
            
        # Get details
        username = self.username_var.get().strip()
        display_name = self.display_name_var.get().strip() or username
        
        # Successfully validated inputs, notify user via alert wrapper.
        messagebox.showinfo(
            "Muvaffaqiyat",
            f"Foydalanuvchi '{display_name}' ({username}) muvaffaqiyatli validatsiya qilindi.\n\n"
            "Ro'yxatdan o'tish jarayoni yakunlandi!"
        )
        self.clear_form()

    def navigate_to_login(self):
        """Link navigation stub hook."""
        self.error_label.config(text="Login sahifasiga o'tish bosildi.", foreground="blue")
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
        self.error_label.config(text="")
