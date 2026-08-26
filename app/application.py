"""
Application bootstrap module for TypeMaster.
"""
import tkinter as tk
from tkinter import ttk
from app.config import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT

class Application:
    """
    Core application controller responsible for Tkinter lifecycle and shell layout.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        
        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - DEFAULT_WINDOW_WIDTH) // 2
        y = (screen_height - DEFAULT_WINDOW_HEIGHT) // 2
        
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}+{x}+{y}")
        self.root.minsize(800, 500)
        
        # Handle clean close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Setup modern styles
        self._setup_style()
        
        # View manager initialization
        self.current_view = None
        self.views = {}
        
        # Setup containers and create views
        self._create_views()

    def _setup_style(self):
        """Configure initial styling using ttk themes."""
        self.style = ttk.Style(self.root)
        try:
            if 'clam' in self.style.theme_names():
                self.style.theme_use('clam')
        except Exception:
            pass

    def _create_views(self):
        """Build view panels and transition logic container."""
        # Main shell view container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Lazy imports to avoid circular dependencies
        from ui.register import RegisterView
        from ui.login import LoginView
        from ui.results import ResultsView
        
        # Register Views
        self.views["register"] = RegisterView(self.main_container, self)
        self.views["home"] = HomePlaceholderView(self.main_container, self)
        self.views["login"] = LoginView(self.main_container, self)
        self.views["results"] = ResultsView(self.main_container, self)
        
        # Check auto-login session
        from services.auth_service import load_session_user
        user = load_session_user()
        if user:
            self.show_view("home")
        else:
            self.show_view("login")


    def show_view(self, view_name: str):
        """Transition views content dynamically."""
        if self.current_view:
            self.current_view.on_hide()
            self.current_view.pack_forget()
            
        view = self.views.get(view_name)
        if view:
            view.pack(fill=tk.BOTH, expand=True)
            view.on_show()
            self.current_view = view

    def on_close(self):
        """Clean shutdown handler."""
        self.root.destroy()

    def run(self):
        """Execute the Tkinter event loop."""
        self.root.mainloop()


# Helper placeholders views for routing verifications
from ui.base import BaseView

class HomePlaceholderView(BaseView):
    """Temporary landing view panel."""
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.welcome_label = ttk.Label(
            self.main_frame, 
            text="TypeMaster Home Screen Placeholder", 
            font=("Helvetica", 18, "bold")
        )
        self.welcome_label.pack(pady=20)
        
        ttk.Button(
            self.main_frame,
            text="Chiqish (Logout)",
            command=self.handle_logout
        ).pack(pady=10)

    def on_show(self):
        """Dynamically update welcome text with current user info."""
        from services.auth_service import get_current_user
        user = get_current_user()
        name = user.get("display_name") if user else "Mehmon"
        self.welcome_label.config(text=f"Xush kelibsiz, {name}!")

    def handle_logout(self):
        """Log out user details and redirect back to login."""
        from services.auth_service import logout_user
        logout_user()
        self.controller.show_view("login")


# LoginPlaceholderView deleted as LoginView is fully integrated.
