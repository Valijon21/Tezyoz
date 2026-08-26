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
        
        # Intercept runtime callback exceptions to present user-friendly error messages
        self.root.report_callback_exception = self.report_callback_exception
        
        # Query scaling factor from Tk
        try:
            scale_factor = self.root.tk.call('tk', 'scaling') / 1.33333333
        except Exception:
            scale_factor = 1.0

        scaled_width = int(DEFAULT_WINDOW_WIDTH * scale_factor)
        scaled_height = int(DEFAULT_WINDOW_HEIGHT * scale_factor)

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - scaled_width) // 2
        y = (screen_height - scaled_height) // 2
        
        self.root.geometry(f"{scaled_width}x{scaled_height}+{x}+{y}")
        
        scaled_min_w = int(800 * scale_factor)
        scaled_min_h = int(500 * scale_factor)
        self.root.minsize(scaled_min_w, scaled_min_h)

        
        # Handle clean close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Setup modern styles
        self._setup_style()
        self.current_font_family = "Consolas"
        self.current_font_size = 14
        
        # View manager initialization
        self.current_view = None
        self.views = {}
        
        # Setup containers and create views
        self._create_views()
        self._bind_global_shortcuts()

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
        from ui.dashboard import DashboardView
        from ui.history import HistoryView
        from ui.personal_best import PersonalBestView
        from ui.typing_test import TypingTestView
        from ui.achievements import AchievementsView
        
        # Register Views
        self.views["register"] = RegisterView(self.main_container, self)
        self.views["home"] = DashboardView(self.main_container, self)
        self.views["login"] = LoginView(self.main_container, self)
        self.views["results"] = ResultsView(self.main_container, self)
        self.views["history"] = HistoryView(self.main_container, self)
        self.views["personal_bests"] = PersonalBestView(self.main_container, self)
        self.views["typing_test"] = TypingTestView(self.main_container, self)
        self.views["achievements"] = AchievementsView(self.main_container, self)
        
        # Check auto-login session
        from services.auth_service import load_session_user
        user = load_session_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            setting = SettingsRepository().get_settings(user["id"])
            if setting:
                self.current_theme = setting["theme"]
                self.current_font_family = setting["font_family"]
                self.current_font_size = setting["font_size"]
            else:
                self.current_theme = "dark"
            self.show_view("home")
        else:
            self.current_theme = "dark"
            self.show_view("login")

    def _bind_global_shortcuts(self):
        """Register application-wide keyboard shortcuts at root window."""
        self.root.bind("<Control-h>", lambda e: self.show_view("home"))
        self.root.bind("<Control-H>", lambda e: self.show_view("home"))
        self.root.bind("<Control-l>", lambda e: self._handle_global_logout())
        self.root.bind("<Control-L>", lambda e: self._handle_global_logout())
        self.root.bind("<Escape>", self._handle_global_escape)

    def _handle_global_logout(self):
        """Action handler to logout active session user."""
        from services.auth_service import logout_user, get_current_user
        if get_current_user():
            logout_user()
            self.show_view("login")

    def _handle_global_escape(self, event):
        """Global escape key event handler. Navigates back home if in other sub-views."""
        if not self.current_view:
            return
            
        home_view = self.views.get("home")
        login_view = self.views.get("login")
        register_view = self.views.get("register")
        test_view = self.views.get("typing_test")

        # Skip routing if already in primary views
        if self.current_view in (home_view, login_view, register_view, test_view):
            return

        # Redirect history, personal bests, results back to home dashboard
        self.show_view("home")

    def show_view(self, view_name: str):

        """Transition views content dynamically."""
        if self.current_view:
            self.current_view.on_hide()
            self.current_view.pack_forget()
            
        if view_name == "home":
            from services.auth_service import get_current_user
            user = get_current_user()
            if user:
                from database.repositories.settings_repository import SettingsRepository
                setting = SettingsRepository().get_settings(user["id"])
                if setting:
                    self.current_theme = setting["theme"]
                    self.current_font_family = setting["font_family"]
                    self.current_font_size = setting["font_size"]

        # Apply active theme and font colors
        self.apply_theme(self.current_theme, self.current_font_family, self.current_font_size)

        view = self.views.get(view_name)
        if view:
            view.pack(fill=tk.BOTH, expand=True)
            view.on_show()
            self.current_view = view

    def apply_theme(self, theme_name: str, font_family: str = None, font_size: int = None):
        """
        Updates theme settings globally in the style engine, root window and child view hierarchies.
        """
        self.current_theme = theme_name
        if font_family is not None:
            self.current_font_family = font_family
        if font_size is not None:
            self.current_font_size = font_size
        
        from ui.theme import apply_theme_colors, THEMES
        apply_theme_colors(self.style, theme_name, self.current_font_family, self.current_font_size)
        
        theme_colors = THEMES.get(theme_name, THEMES["dark"])
        self.root.configure(background=theme_colors["bg"])
        
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            repo = SettingsRepository()
            repo.update_setting(user["id"], "theme", theme_name)
            if font_family is not None:
                repo.update_setting(user["id"], "font_family", font_family)
            if font_size is not None:
                repo.update_setting(user["id"], "font_size", font_size)
            
        for view in self.views.values():
            if hasattr(view, "apply_theme"):
                view.apply_theme(theme_name)

    def on_close(self):
        """Clean shutdown handler."""
        self.root.destroy()

    def run(self):
        """Execute the Tkinter event loop."""
        self.root.mainloop()

    def report_callback_exception(self, exc, val, tb):
        """
        Intercepts uncaught runtime event exceptions, logs traceback info,
        and presents a themed user-friendly error message block.
        """
        import traceback
        import logging
        from tkinter import messagebox
        
        logger = logging.getLogger("app.application")
        logger.error("Uncaught runtime exception in event callback", exc_info=(exc, val, tb))
        
        # Format a clean user-friendly alert message
        error_msg = (
            "Kutilmagan tizim xatoligi yuz berdi. Tafsilotlar xatolar logida saqlandi.\n\n"
            f"Xato xabari: {val}"
        )
        try:
            messagebox.showerror("Tizim Xatoligi (System Error)", error_msg)
        except Exception:
            # Fallback if UI is in a corrupt state or closed
            print(f"[CRITICAL CALLBACK ERROR]: {val}\n{''.join(traceback.format_exception(exc, val, tb))}", file=sys.stderr)



# LoginPlaceholderView deleted as LoginView is fully integrated.
