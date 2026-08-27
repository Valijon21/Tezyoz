"""
Local Leaderboard display view comparing registered users by total XP.
Renders user ranks utilizing a modern scrollable card list layout.
"""
import tkinter as tk
import customtkinter as ctk
from ui.base import BaseView
from services.auth_service import get_leaderboard, get_current_user
from ui.theme import THEMES

class LeaderboardView(BaseView):
    """
    Renders comparative local ranking of all registered users on the system.
    Utilizes CTkScrollableFrame and individual card frames for top visual look.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.cards_frame = None
        self.rows_list = []
        self._setup_ui()

    def _setup_ui(self):
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Base container
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title Block
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill=tk.X, pady=(0, 15))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🏆  Reyting (Leaderboard)",
            font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(side=tk.LEFT, anchor="w")

        self.refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄 Yangilash",
            width=100,
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"],
            font=("Segoe UI", 12, "bold"),
            command=self.on_show
        )
        self.refresh_btn.pack(side=tk.RIGHT, anchor="e")

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.container,
            text="Umumiy to'plangan XP bo'yicha eng faol foydalanuvchilar ro'yxati:",
            font=("Segoe UI", 12, "italic"),
            text_color=theme_colors["secondary_fg"]
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 15))

        # Table Column Headers Frame
        self.headers_frame = ctk.CTkFrame(self.container, fg_color="transparent", height=30)
        self.headers_frame.pack(fill=tk.X, pady=(0, 5))
        self.headers_frame.pack_propagate(False)

        # Headers Layout grid sizing
        self.headers_frame.columnconfigure(0, weight=0, minsize=60) # Rank
        self.headers_frame.columnconfigure(1, weight=1)             # Username
        self.headers_frame.columnconfigure(2, weight=0, minsize=100) # Level
        self.headers_frame.columnconfigure(3, weight=0, minsize=120) # Total XP
        self.headers_frame.columnconfigure(4, weight=0, minsize=120) # Max Streak

        h_rank = ctk.CTkLabel(self.headers_frame, text="O'rin", font=("Segoe UI", 11, "bold"), text_color=theme_colors["secondary_fg"], anchor="center")
        h_rank.grid(row=0, column=0, sticky="w", padx=(10, 0))

        h_name = ctk.CTkLabel(self.headers_frame, text="Foydalanuvchi", font=("Segoe UI", 11, "bold"), text_color=theme_colors["secondary_fg"], anchor="w")
        h_name.grid(row=0, column=1, sticky="w", padx=10)

        h_lvl = ctk.CTkLabel(self.headers_frame, text="Daraja", font=("Segoe UI", 11, "bold"), text_color=theme_colors["secondary_fg"], anchor="center")
        h_lvl.grid(row=0, column=2)

        h_xp = ctk.CTkLabel(self.headers_frame, text="Umumiy XP", font=("Segoe UI", 11, "bold"), text_color=theme_colors["secondary_fg"], anchor="center")
        h_xp.grid(row=0, column=3)

        h_str = ctk.CTkLabel(self.headers_frame, text="Eng Uzun Streak", font=("Segoe UI", 11, "bold"), text_color=theme_colors["secondary_fg"], anchor="center")
        h_str.grid(row=0, column=4, padx=(0, 10))

        # Main Scrollable list frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent", corner_radius=0)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Bottom navigation
        self.nav_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.nav_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.back_btn = ctk.CTkButton(
            self.nav_frame,
            text="Orqaga (Dashboard)",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"],
            command=self._handle_back
        )
        self.back_btn.pack(side=tk.LEFT, ipady=4)

    def on_show(self):
        """Lifecycle hook refreshing the users rankings list."""
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Fetch rankings from db safely
        try:
            top_list = get_leaderboard(limit=25)
        except Exception:
            top_list = []

        # Clear existing row cards
        for row in self.rows_list:
            row.destroy()
        self.rows_list.clear()

        # Render rows dynamically
        for i, u in enumerate(top_list, 1):
            is_highlighted = i <= 3
            
            # Custom card background and border colors for top 3
            border_color = None
            border_width = 0
            if is_highlighted:
                if theme == "light":
                    # Light theme highlights
                    if i == 1:
                        text_color = "#b25e00"   # Gold/amber dark text
                        bg_color = "#fff9e6"     # Soft gold background
                        border_color = "#ffd700"
                        border_width = 1
                    elif i == 2:
                        text_color = "#5e5e5e"   # Silver dark text
                        bg_color = "#f1f3f5"     # Soft silver background
                        border_color = "#c0c0c0"
                        border_width = 1
                    else:
                        text_color = "#8b4513"   # Bronze dark text
                        bg_color = "#faf0e6"     # Soft bronze background
                        border_color = "#cd7f32"
                        border_width = 1
                else:
                    # Dark & Cyberpunk highlights
                    if i == 1:
                        text_color = "#ffd700"
                        bg_color = "#2a2825"
                        border_color = "#ffd700"
                        border_width = 1
                    elif i == 2:
                        text_color = "#c0c0c0"
                        bg_color = "#23242c"
                        border_color = "#c0c0c0"
                        border_width = 1
                    else:
                        text_color = "#cd7f32"
                        bg_color = "#211e1f"
                        border_color = "#cd7f32"
                        border_width = 1
            else:
                text_color = theme_colors["fg"]
                bg_color = theme_colors["card_bg"]

            curr_user = get_current_user()
            is_self = curr_user and curr_user.get("id") == u.get("id")
            
            # Double thickness border if it is the logged in user
            if is_self and not is_highlighted:
                border_color = theme_colors["select_bg"]
                border_width = 1

            row_frame = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=bg_color,
                corner_radius=8,
                border_color=border_color,
                border_width=border_width,
                height=42
            )
            row_frame.pack(fill=tk.X, pady=4)
            row_frame.pack_propagate(False)
            self.rows_list.append(row_frame)

            # Columns allocation
            row_frame.columnconfigure(0, weight=0, minsize=60) # Rank
            row_frame.columnconfigure(1, weight=1)             # Username
            row_frame.columnconfigure(2, weight=0, minsize=100) # Level
            row_frame.columnconfigure(3, weight=0, minsize=120) # Total XP
            row_frame.columnconfigure(4, weight=0, minsize=120) # Max Streak

            # Rank label
            rank_prefix = "👑 " if i == 1 else "🥈 " if i == 2 else "🥉 " if i == 3 else f"{i:02d} "
            rank_lbl = ctk.CTkLabel(
                row_frame,
                text=rank_prefix,
                font=("Segoe UI", 13, "bold"),
                text_color=text_color,
                anchor="center"
            )
            rank_lbl.grid(row=0, column=0, sticky="w", padx=(15, 0), pady=6)

            # Display name (or username)
            name_suffix = " (Oqdilan)" if is_self else ""
            display_name = u.get("display_name") or u.get("username")
            name_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{display_name}{name_suffix}",
                font=("Segoe UI", 12, "bold" if is_self else "normal"),
                text_color=theme_colors["fg"] if not is_highlighted else text_color,
                anchor="w"
            )
            name_lbl.grid(row=0, column=1, sticky="w", padx=10, pady=6)

            # Level
            lvl_lbl = ctk.CTkLabel(
                row_frame,
                text=f"Lvl {u.get('level', 1)}",
                font=("Segoe UI", 12, "bold"),
                text_color=theme_colors["select_bg"] if not is_highlighted else text_color,
                anchor="center"
            )
            lvl_lbl.grid(row=0, column=2, pady=6)

            # Total XP
            xp_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{u.get('xp', 0)} XP",
                font=("Segoe UI", 12),
                text_color=theme_colors["fg"],
                anchor="center"
            )
            xp_lbl.grid(row=0, column=3, pady=6)

            # Streak
            streak_val = u.get("longest_streak", 0)
            streak_txt = f"🔥 {streak_val} kun" if streak_val > 0 else "-"
            str_lbl = ctk.CTkLabel(
                row_frame,
                text=streak_txt,
                font=("Segoe UI", 12),
                text_color="#f97316" if streak_val > 0 else theme_colors["secondary_fg"],
                anchor="center"
            )
            str_lbl.grid(row=0, column=4, pady=6, padx=(0, 10))

    def apply_theme(self, theme_name: str):
        """Applies theme styling to static buttons and scrollable components."""
        from ui.theme import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        
        if hasattr(self, "refresh_btn") and self.refresh_btn:
            self.refresh_btn.configure(
                fg_color=theme["card_bg"],
                text_color=theme["fg"],
                hover_color=theme["select_bg"]
            )
        if hasattr(self, "back_btn") and self.back_btn:
            self.back_btn.configure(
                fg_color=theme["card_bg"],
                text_color=theme["fg"],
                hover_color=theme["select_bg"]
            )
        # Reload card lists to repaint correct item backgrounds matching active highlights if visible
        if self.winfo_ismapped():
            self.on_show()

    def _handle_back(self):
        """Action navigating back to Dashboard."""
        if self.controller:
            self.controller.show_view("home")
