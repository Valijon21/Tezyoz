import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from app.config import APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT
from app.event_bus import EventBus

class Application:
    """
    Core application controller responsible for CustomTkinter lifecycle and shell layout.
    """
    def __init__(self):
        # Configure CTk default settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        
        # Setup EventBus
        self.event_bus = EventBus()

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
        self.current_theme = "dark"
        self.current_font_family = "Consolas"
        self.current_font_size = 14
        
        # View manager initialization
        self.current_view = None
        self.views = {}
        
        # Setup containers and create views
        self._create_views()
        self._bind_global_shortcuts()

    def _setup_style(self):
        """Configure initial styling using ttk themes (kept for legacy tk widgets compatibility)."""
        self.style = ttk.Style(self.root)
        try:
            if 'clam' in self.style.theme_names():
                self.style.theme_use('clam')
        except Exception:
            pass

    def _create_views(self):
        """Build view panels and transition logic container using customtkinter."""
        # Main shell view container
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent", corner_radius=0)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar navigation UI (hidden by default, packed when logged in)
        self.sidebar_frame = ctk.CTkFrame(self.main_container, corner_radius=0, width=240)
        self.nav_btns = {}
        
        # Content frame container for sub-views when sidebar is active
        self.content_container = ctk.CTkFrame(self.main_container, fg_color="transparent", corner_radius=0)

        # Lazy imports to avoid circular dependencies
        from ui.register import RegisterView
        from ui.login import LoginView
        from ui.results import ResultsView
        from ui.dashboard import DashboardView
        from ui.history import HistoryView
        from ui.personal_best import PersonalBestView
        from ui.typing_test import TypingTestView
        from ui.achievements import AchievementsView
        from ui.leaderboard import LeaderboardView
        
        # Register Views (login and register use main_container, others use content_container)
        self.views["register"] = RegisterView(self.main_container, self)
        self.views["login"] = LoginView(self.main_container, self)
        
        self.views["home"] = DashboardView(self.content_container, self)
        self.views["results"] = ResultsView(self.content_container, self)
        self.views["history"] = HistoryView(self.content_container, self)
        self.views["personal_bests"] = PersonalBestView(self.content_container, self)
        self.views["typing_test"] = TypingTestView(self.content_container, self)
        self.views["achievements"] = AchievementsView(self.content_container, self)
        self.views["leaderboard"] = LeaderboardView(self.content_container, self)
        
        # Build persistent sidebar contents
        self._build_sidebar()
        
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

        if view_name in ("login", "register"):
            # Hide sidebar layout
            self.sidebar_frame.pack_forget()
            self.content_container.pack_forget()
            view = self.views.get(view_name)
            if view:
                view.pack(fill=tk.BOTH, expand=True)
                view.on_show()
                self.current_view = view
        else:
            # Pack sidebar persistently on the left, views inside right container
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
            self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            self._update_nav_highlights(view_name)
            self.update_sidebar_profile()
            
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
        
        # CustomTkinter theme settings
        if theme_name == "light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
            
        from ui.theme import apply_theme_colors, THEMES
        apply_theme_colors(self.style, theme_name, self.current_font_family, self.current_font_size)
        
        theme_colors = THEMES.get(theme_name, THEMES["dark"])
        self.root.configure(fg_color=theme_colors["bg"])
        
        # Configure sidebar frame background color
        if hasattr(self, "sidebar_frame") and self.sidebar_frame:
            self.sidebar_frame.configure(fg_color=theme_colors["sidebar_bg"])
        if hasattr(self, "profile_card") and self.profile_card:
            self.profile_card.configure(fg_color=theme_colors["card_bg"])
        if hasattr(self, "settings_card") and self.settings_card:
            self.settings_card.configure(fg_color=theme_colors["card_bg"])
        if hasattr(self, "sidebar_divider") and self.sidebar_divider:
            self.sidebar_divider.configure(fg_color=theme_colors["border"])
        if hasattr(self, "caret_label") and self.caret_label:
            self.caret_label.configure(text_color=theme_colors["secondary_fg"])
            
        # Sync Settings dropdown variables on application sidebar if available
        if hasattr(self, "sidebar_theme_combo") and self.sidebar_theme_combo:
            self.sidebar_theme_combo.set(theme_name)
        if hasattr(self, "sidebar_font_family_combo") and self.sidebar_font_family_combo:
            self.sidebar_font_family_combo.set(self.current_font_family)
        if hasattr(self, "sidebar_font_size_combo") and self.sidebar_font_size_combo:
            self.sidebar_font_size_combo.set(str(self.current_font_size))
            
        # Sync sound switch states in sidebar settings frame
        if hasattr(self, "sidebar_sound_switch") and self.sidebar_sound_switch:
            from services.sound_service import sound_player
            if sound_player._is_sound_enabled():
                self.sidebar_sound_switch.select()
            else:
                self.sidebar_sound_switch.deselect()
            
        # Re-layout active nav highlights
        if hasattr(self, "current_view") and self.current_view:
            self._update_nav_highlights(self.current_view.__class__.__name__.lower().replace("view", ""))

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

    def _build_sidebar(self):
        """Constructs elements inside the left persistent navigation panel in Sokin Neon style using CTk."""
        from ui.theme import THEMES
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])

        inner_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent", corner_radius=0)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # 1. App Identity / Logo
        app_title = ctk.CTkLabel(inner_frame, text="⚡ TypeMaster", font=("Segoe UI", 20, "bold"))
        app_title.pack(anchor="w", pady=(0, 20))

        # 2. Profile Card Panel (Mockup Horizontal Layout)
        self.profile_card = ctk.CTkFrame(inner_frame, fg_color=theme_colors["card_bg"], corner_radius=12)
        self.profile_card.pack(fill=tk.X, pady=(0, 20))
        
        self.profile_card.columnconfigure(1, weight=1)

        # Avatar placeholder
        self.avatar_label = ctk.CTkLabel(
            self.profile_card, 
            text="👤", 
            font=("Segoe UI", 18)
        )
        self.avatar_label.grid(row=0, column=0, padx=(10, 8), pady=8, sticky="w")

        # Username
        self.sidebar_user_label = ctk.CTkLabel(
            self.profile_card, 
            text="Alex R.", 
            font=("Segoe UI", 12, "bold")
        )
        self.sidebar_user_label.grid(row=0, column=1, pady=8, sticky="w")

        # Dropdown caret
        self.caret_label = ctk.CTkLabel(
            self.profile_card, 
            text=" ∨", 
            font=("Segoe UI", 10, "bold"),
            text_color=theme_colors["secondary_fg"]
        )
        self.caret_label.grid(row=0, column=2, padx=(5, 10), pady=8, sticky="e")

        # Divider Separator
        self.sidebar_divider = ctk.CTkFrame(inner_frame, height=2, fg_color=theme_colors["border"])
        self.sidebar_divider.pack(fill=tk.X, pady=(0, 20))

        # 3. Navigation Controls Area (Aligned to English Mockup list)
        menu_frame = ctk.CTkFrame(inner_frame, fg_color="transparent", corner_radius=0)
        menu_frame.pack(fill=tk.BOTH, expand=True)

        nav_config = [
            ("home", "⊞  Dashboard"),
            ("typing_test", "📋  Practice"),
            ("history", "📜  Test History"),
            ("achievements", "🏆  Achievements"),
            ("personal_bests", "🥇  Personal Bests"),
            ("leaderboard", "🏆  Leaderboard")
        ]

        for view_key, label_txt in nav_config:
            btn = ctk.CTkButton(
                menu_frame,
                text=label_txt,
                fg_color="transparent",
                text_color=theme_colors["secondary_fg"],
                hover_color=theme_colors["select_bg"],
                font=("Segoe UI", 12, "bold"),
                anchor="w",
                height=36,
                corner_radius=8,
                command=lambda vk=view_key: self.show_view(vk)
            )
            btn.pack(fill=tk.X, pady=3, anchor="w")
            self.nav_btns[view_key] = btn

        # Logout button
        logout_btn = ctk.CTkButton(
            menu_frame,
            text="🚪 Chiqish (Logout)",
            fg_color="transparent",
            text_color=theme_colors["secondary_fg"],
            hover_color=theme_colors["select_bg"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
            height=36,
            corner_radius=8,
            command=self._handle_global_logout
        )
        logout_btn.pack(fill=tk.X, pady=(20, 3), anchor="w")
        self.nav_btns["logout"] = logout_btn

        # 4. Settings Section (Theme, Font, Size Selection)
        self.settings_card = ctk.CTkFrame(inner_frame, fg_color=theme_colors["card_bg"], corner_radius=12)
        self.settings_card.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0), padx=0)
        
        settings_inner = ctk.CTkFrame(self.settings_card, fg_color="transparent", corner_radius=0)
        settings_inner.pack(fill=tk.X, padx=10, pady=10)

        # Title
        ctk.CTkLabel(settings_inner, text="Sozlamalar", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 5))

        # Theme Combo
        ctk.CTkLabel(settings_inner, text="Mavzu:", font=("Segoe UI", 10)).pack(anchor="w")
        self.sidebar_theme_combo = ctk.CTkOptionMenu(
            settings_inner,
            values=["dark", "light", "cyberpunk"],
            command=self._handle_sidebar_settings_change,
            height=26,
            font=("Segoe UI", 11)
        )
        self.sidebar_theme_combo.pack(fill=tk.X, pady=(2, 6))

        # Font Combo
        ctk.CTkLabel(settings_inner, text="Shrift:", font=("Segoe UI", 10)).pack(anchor="w")
        self.sidebar_font_family_combo = ctk.CTkOptionMenu(
            settings_inner,
            values=["Segoe UI", "Consolas", "Courier New", "Arial"],
            command=self._handle_sidebar_settings_change,
            height=26,
            font=("Segoe UI", 11)
        )
        self.sidebar_font_family_combo.pack(fill=tk.X, pady=(2, 6))

        # Font Size Combo
        ctk.CTkLabel(settings_inner, text="O'lcham:", font=("Segoe UI", 10)).pack(anchor="w")
        self.sidebar_font_size_combo = ctk.CTkOptionMenu(
            settings_inner,
            values=["11", "12", "13", "14", "15", "16", "18"],
            command=self._handle_sidebar_settings_change,
            height=26,
            font=("Segoe UI", 11)
        )
        self.sidebar_font_size_combo.pack(fill=tk.X, pady=(2, 2))

        # Sound Switch Toggle
        self.sidebar_sound_switch = ctk.CTkSwitch(
            settings_inner,
            text="Ovozli effektlar",
            command=self._handle_sidebar_sound_toggle,
            font=("Segoe UI", 11)
        )
        self.sidebar_sound_switch.pack(anchor="w", pady=(6, 2))

    def _handle_sidebar_settings_change(self, choice=None):
        """Action handler when any of the sidebar combobox elements is changed."""
        theme_name = self.sidebar_theme_combo.get()
        font_family = self.sidebar_font_family_combo.get()
        try:
            font_size = int(self.sidebar_font_size_combo.get())
        except ValueError:
            font_size = 14
        self.apply_theme(theme_name, font_family, font_size)

    def _handle_sidebar_sound_toggle(self):
        """Action handler when the sound toggle switch is flipped."""
        from services.sound_service import sound_player
        enabled = sound_player.toggle_sound()
        if enabled:
            sound_player.play_click()

    def _update_nav_highlights(self, active_view_name: str):
        """Highlights the active navigation button in the left sidebar menu."""
        from ui.theme import THEMES
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
        for key, btn in self.nav_btns.items():
            if key == active_view_name:
                btn.configure(fg_color=theme_colors["select_bg"], text_color=theme_colors["fg"])
            else:
                btn.configure(fg_color="transparent", text_color=theme_colors["secondary_fg"])

    def update_sidebar_profile(self):
        """Fetches active user data from memory and updates user card in the sidebar."""
        from services.auth_service import get_current_user, refresh_current_user
        refresh_current_user() # sync and read last state from DB
        user = get_current_user()
        if user:
            display_name = user.get("display_name") or user.get("username")
            self.sidebar_user_label.configure(text=display_name)
            self.avatar_label.configure(text="👤")
        else:
            self.sidebar_user_label.configure(text="Mehmon")
            self.avatar_label.configure(text="👤")

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
        import sys
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
