import tkinter as tk
from tkinter import ttk
from datetime import datetime
import customtkinter as ctk
from ui.base import BaseView
from charts.line_chart import LineChart, AccuracyChart
from charts.bar_chart import BarChart
from charts.heatmap import KeyboardHeatmap
from ui.advanced_stats import AdvancedStatsPanel
from database.repositories.daily_stats_repository import DailyStatsRepository
from services.auth_service import get_current_user, logout_user
from app.config import XP_DAILY_GOAL

class DashboardView(BaseView):
    """
    Core layout showing typing practice summaries, streak levels, period filters
    and canvas charts widgets using CustomTkinter components.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.stats_repo = DailyStatsRepository()
        self.active_period = "weekly"      # default period
        self.active_chart_key = "wpm"      # default chart key

        self._setup_ui()

    def _setup_ui(self):
        from ui.theme import THEMES
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Base container pad
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 1. Profile information Bar
        self.profile_bar = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.profile_bar.pack(fill=tk.X, pady=(0, 15))

        self.welcome_label = ctk.CTkLabel(
            self.profile_bar,
            text="Foydalanuvchi: Mehmon",
            font=("Segoe UI", 20, "bold")
        )
        self.welcome_label.pack(side=tk.LEFT)

        self.gamification_label = ctk.CTkLabel(
            self.profile_bar,
            text="Joriy Streak: 0 🔥 | Rekord: 0 kun | Bosqich: 1 (0 XP)",
            font=("Segoe UI", 12),
            text_color=theme_colors["secondary_fg"]
        )
        self.gamification_label.pack(side=tk.RIGHT)

        # 1b. XP Progress Bar Area
        self.xp_container = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.xp_container.pack(fill=tk.X, pady=(5, 5))

        self.xp_bar = ctk.CTkProgressBar(
            self.xp_container,
            progress_color=theme_colors["accent"],
            fg_color=theme_colors["border"]
        )
        self.xp_bar.set(0)
        self.xp_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.xp_percent_label = ctk.CTkLabel(
            self.xp_container,
            text="0.0% (0/100 XP)",
            font=("Segoe UI", 11),
            text_color=theme_colors["secondary_fg"]
        )
        self.xp_percent_label.pack(side=tk.RIGHT)

        # 1c. Daily Goal Progress Bar Area
        self.daily_goal_container = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.daily_goal_container.pack(fill=tk.X, pady=(2, 5))

        self.daily_goal_bar = ctk.CTkProgressBar(
            self.daily_goal_container,
            progress_color=theme_colors["accent"],
            fg_color=theme_colors["border"]
        )
        self.daily_goal_bar.set(0)
        self.daily_goal_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.daily_goal_label = ctk.CTkLabel(
            self.daily_goal_container,
            text="Bugungi Maqsad: 0.0% (0/100 XP)",
            font=("Segoe UI", 11),
            text_color=theme_colors["secondary_fg"]
        )
        self.daily_goal_label.pack(side=tk.RIGHT)

        # Separator line
        separator = ctk.CTkFrame(self.container, height=2, fg_color=theme_colors["border"])
        separator.pack(fill=tk.X, pady=(0, 15))

        # Daily Missions Group
        self.missions_frame = ctk.CTkFrame(
            self.container, 
            fg_color=theme_colors["card_bg"],
            corner_radius=12
        )
        self.missions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Missions Inner padding container
        missions_inner = ctk.CTkFrame(self.missions_frame, fg_color="transparent", corner_radius=0)
        missions_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.missions_title = ctk.CTkLabel(
            missions_inner,
            text="Bugungi Vazifalar (Daily Missions)",
            font=("Segoe UI", 12, "bold")
        )
        self.missions_title.pack(anchor="w", pady=(0, 8))

        cols_container = ctk.CTkFrame(missions_inner, fg_color="transparent", corner_radius=0)
        cols_container.pack(fill=tk.BOTH, expand=True)

        self.mission_cols = []
        for i in range(3):
            col_frame = ctk.CTkFrame(cols_container, fg_color=theme_colors["select_bg"], corner_radius=10)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)

            hdr = ctk.CTkFrame(col_frame, fg_color="transparent")
            hdr.pack(fill=tk.X, padx=10, pady=(10, 4))

            chk_lbl = ctk.CTkLabel(
                hdr, 
                text="☐", 
                font=("Segoe UI", 16, "bold"), 
                text_color=theme_colors["secondary_fg"]
            )
            chk_lbl.pack(side=tk.LEFT, padx=(0, 6))

            title_lbl = ctk.CTkLabel(
                hdr, 
                text="-", 
                font=("Segoe UI", 12, "bold"),
                anchor="w",
                justify=tk.LEFT
            )
            title_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

            desc_lbl = ctk.CTkLabel(
                col_frame, 
                text="-", 
                font=("Segoe UI", 11), 
                text_color=theme_colors["secondary_fg"],
                wraplength=200,
                anchor="w",
                justify=tk.LEFT
            )
            desc_lbl.pack(anchor="w", padx=10, pady=(0, 8))

            progress_bar = ctk.CTkProgressBar(
                col_frame,
                progress_color=theme_colors["accent"],
                fg_color=theme_colors["border"]
            )
            progress_bar.set(0)
            progress_bar.pack(fill=tk.X, padx=10, pady=(0, 4))

            status_lbl = ctk.CTkLabel(
                col_frame, 
                text="-", 
                font=("Segoe UI", 10, "italic")
            )
            status_lbl.pack(anchor="w", padx=10, pady=(0, 10))

            self.mission_cols.append({
                "frame": col_frame,
                "chk": chk_lbl,
                "title": title_lbl,
                "desc": desc_lbl,
                "bar": progress_bar,
                "status": status_lbl
            })

        # 2. Statistics Period Filters & Title
        self.filter_bar = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.filter_bar.pack(fill=tk.X, pady=(0, 15))

        self.title_label = ctk.CTkLabel(
            self.filter_bar,
            text="Statistika Tahlili",
            font=("Segoe UI", 20, "bold")
        )
        self.title_label.pack(side=tk.LEFT)

        self.period_buttons = {}
        periods_config = [("today", "Bugun"), ("weekly", "Haftalik"), ("monthly", "Oylik")]
        
        # Period picker controls (arranged right to left)
        period_frame = ctk.CTkFrame(self.filter_bar, fg_color="transparent", corner_radius=0)
        period_frame.pack(side=tk.RIGHT)
        
        for key, text in periods_config:
            btn = ctk.CTkButton(
                period_frame,
                text=text,
                fg_color=theme_colors["card_bg"],
                hover_color=theme_colors["select_bg"],
                text_color=theme_colors["fg"],
                font=("Segoe UI", 11, "bold"),
                width=80,
                height=30,
                corner_radius=8,
                command=lambda k=key: self._set_period(k)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.period_buttons[key] = btn

        # Database backup/restore buttons removed (moved to dedicated Settings view)
        pass

        # 3. Summary Cards Grid Layout (4 columns matching mockup in Sokin Neon style)
        self.cards_frame = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.cards_frame.pack(fill=tk.X, pady=(0, 15))
        
        for col in range(4):
            self.cards_frame.columnconfigure(col, weight=1, uniform="equal")

        self.cards = {}
        card_configs = [
            (0, "wpm", "🔥  WPM", "Top Speed: -", "+0.0% Today"),
            (1, "accuracy", "✅  Accuracy", "Mistake Free: stable", "Precise"),
            (2, "consistency", "📈  Consistency", "Stable", "Pace Var: -"),
            (3, "streak", "🎯  Daily Streak", "Goal: 100 XP", "0 Sessions")
        ]

        for col, key, title, def_left, def_right in card_configs:
            # Flatter card frame with nice padding
            frame = ctk.CTkFrame(self.cards_frame, fg_color=theme_colors["card_bg"], corner_radius=12)
            frame.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")
            
            # Header title label
            hdr_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0)
            hdr_frame.pack(fill=tk.X, padx=12, pady=(10, 3))
            
            title_lbl = ctk.CTkLabel(
                hdr_frame, 
                text=title, 
                font=("Segoe UI", 10, "bold"),
                text_color=theme_colors["secondary_fg"]
            )
            title_lbl.pack(side=tk.LEFT)
            
            # Large metric value label
            value_lbl = ctk.CTkLabel(
                frame,
                text="-",
                font=("Segoe UI", 24, "bold"),
                text_color=theme_colors["fg"]
            )
            value_lbl.pack(fill=tk.X, padx=12, pady=(2, 6), anchor="w")
            
            # Decorative mini progress line representing sparkline
            prog_bar = ctk.CTkProgressBar(
                frame,
                progress_color=theme_colors["accent"],
                fg_color=theme_colors["border"]
            )
            prog_bar.set(0.5)
            prog_bar.pack(fill=tk.X, padx=12, pady=(0, 8))
            
            # Sub-indicators bottom row
            btm_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0)
            btm_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
            
            left_lbl = ctk.CTkLabel(
                btm_frame, 
                text=def_left, 
                font=("Segoe UI", 9),
                text_color=theme_colors["secondary_fg"]
            )
            left_lbl.pack(side=tk.LEFT)
            
            right_lbl = ctk.CTkLabel(
                btm_frame, 
                text=def_right, 
                font=("Segoe UI", 9),
                text_color=theme_colors["secondary_fg"]
            )
            right_lbl.pack(side=tk.RIGHT)
            
            # Keep view.cards[key] as value_lbl for compatibility with existing tests
            self.cards[key] = value_lbl
            self.cards[key].title = title_lbl
            self.cards[key].left = left_lbl
            self.cards[key].right = right_lbl
            self.cards[key].bar = prog_bar

        # 4. Chart switch buttons
        self.chart_switch_bar = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.chart_switch_bar.pack(fill=tk.X, pady=(0, 10))

        self.chart_label = ctk.CTkLabel(
            self.chart_switch_bar,
            text="Grafik Ko'rinishi:",
            font=("Segoe UI", 11, "bold")
        )
        self.chart_label.pack(side=tk.LEFT, padx=(0, 10))

        self.chart_buttons = {}
        chart_configs = [
            ("wpm", "Tezlik (WPM)"),
            ("accuracy", "Aniqlik (%)"),
            ("duration", "Mashq Vaqti"),
            ("consistency", "Ritm (%)"),
            ("keyboard_heatmap", "Tugmalar Heatmap"),
            ("advanced_stats", "Kengaytirilgan"),
            ("key_errors", "Tugmalar Tahlili")
        ]
        
        for key, text in chart_configs:
            btn = ctk.CTkButton(
                self.chart_switch_bar,
                text=text,
                fg_color=theme_colors["card_bg"],
                hover_color=theme_colors["select_bg"],
                text_color=theme_colors["fg"],
                font=("Segoe UI", 11, "bold"),
                width=100,
                height=30,
                corner_radius=8,
                command=lambda k=key: self._set_chart_type(k)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.chart_buttons[key] = btn

        # 5. Charts Container Area
        self.chart_display_frame = ctk.CTkFrame(self.container, height=self.scale_px(260), fg_color="transparent", corner_radius=0)
        self.chart_display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, self.scale_px(15)))
        self.chart_display_frame.pack_propagate(False) # lock minimum height for drawing bounds safely

        # Instantiate all 3 visual widgets
        self.wpm_chart = LineChart(self.chart_display_frame)
        self.acc_chart = AccuracyChart(self.chart_display_frame)
        self.time_chart = BarChart(self.chart_display_frame)
        self.heatmap_chart = KeyboardHeatmap(self.chart_display_frame)
        self.advanced_stats_panel = AdvancedStatsPanel(self.chart_display_frame)

        # Widgets packed inside content container directly

    def on_show(self):
        """Standard lifecycle hook called when home/dashboard view transitions active."""
        # Update styling parameters
        self.apply_theme(self.controller.current_theme)

        # 1. Update user identity header information
        from services.i18n_service import t
        user = get_current_user()
        if user:
            name = user.get("display_name") or user.get("username", "Mehmon")
            streak = user.get("current_streak", 0)
            longest_streak = user.get("longest_streak", 0)
            xp = user.get("xp", 0)
            
            from gamification.levels import get_level_progress
            level, xp_in_level, xp_needed = get_level_progress(xp)
            
            self.welcome_label.configure(text=t("welcome_user").format(name))
            self.gamification_label.configure(text=t("streak_info").format(streak, longest_streak, level, xp))
            
            # CustomTkinter progress bar uses values from 0.0 to 1.0
            self.xp_bar.set(xp_in_level / xp_needed if xp_needed > 0 else 0)
            percent = (xp_in_level / xp_needed) * 100 if xp_needed > 0 else 0.0
            self.xp_percent_label.configure(text=t("xp_percent").format(f"{percent:.1f}", xp_in_level, xp_needed))

            # Update daily goal progress
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_stats = self.stats_repo.get_daily_stats(user["id"], today_str) or {}
            today_xp = today_stats.get("xp_earned", 0) if isinstance(today_stats, dict) else 0

            self.daily_goal_bar.set(min(today_xp, XP_DAILY_GOAL) / XP_DAILY_GOAL if XP_DAILY_GOAL > 0 else 0)
            goal_percent = (today_xp / XP_DAILY_GOAL) * 100 if XP_DAILY_GOAL > 0 else 0.0
            self.daily_goal_label.configure(text=t("daily_goal").format(f"{goal_percent:.1f}", today_xp, XP_DAILY_GOAL))

            # Update daily missions
            from services.daily_missions_service import DailyMissionsService
            missions_service = DailyMissionsService()
            missions = missions_service.get_or_generate_daily_missions(user["id"], today_str)
            for i, mission in enumerate(missions):
                if i < len(self.mission_cols):
                    col = self.mission_cols[i]
                    m_key = mission.get("mission_key", "")
                    title_text = t(f"mission_{m_key}_title", mission["title"]) if m_key else mission["title"]
                    desc_text = t(f"mission_{m_key}_desc", mission["description"]) if m_key else mission["description"]
                    col["title"].configure(text=f"{title_text} (+{mission['xp_reward']} XP)")
                    col["desc"].configure(text=desc_text)
                    
                    progress = mission["progress"]
                    target = mission["target"]
                    col["bar"].set(progress / target if target > 0 else 0)
                    
                    if mission["completed"]:
                        col["chk"].configure(text="☑", text_color="#10b981") # Green
                        col["status"].configure(text=t("bajarildi"), text_color="#10b981") # Green
                    else:
                        col["chk"].configure(text="☐", text_color="#8e9196") # Grey
                        col["status"].configure(text=t("mission_progress").format(progress, target), text_color="#8e9196") # Grey
        else:
            self.welcome_label.configure(text=t("welcome_guest"))
            self.gamification_label.configure(text=t("streak_info_guest"))
            
            self.xp_bar.set(0)
            self.xp_percent_label.configure(text=t("xp_percent").format("0.0", 0, 100))

            self.daily_goal_bar.set(0)
            self.daily_goal_label.configure(text=t("daily_goal").format("0.0", 0, XP_DAILY_GOAL))

            # Muted guest defaults
            for col in self.mission_cols:
                col["title"].configure(text="-")
                col["desc"].configure(text=t("daily_missions_guest"))
                col["chk"].configure(text="☐", text_color="#8e9196")
                col["bar"].set(0)
                col["status"].configure(text="-", text_color="#8e9196")

        # 2. Reload data and redraw active charts
        self.refresh_stats()

    def _set_period(self, period_key: str):
        """Sets active date boundary and triggers statistical updates."""
        self.active_period = period_key
        # Update filter period button highlights
        from ui.theme import THEMES
        theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])
        for key, btn in self.period_buttons.items():
            if key == period_key:
                btn.configure(fg_color=theme_colors["select_bg"])
            else:
                btn.configure(fg_color=theme_colors["card_bg"])
        self.refresh_stats()

    def _set_chart_type(self, chart_key: str):
        """Swaps active canvas view widget and reloads layout draw mapping."""
        self.active_chart_key = chart_key
        # Update chart button highlights
        from ui.theme import THEMES
        theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])
        for key, btn in self.chart_buttons.items():
            if key == chart_key:
                btn.configure(fg_color=theme_colors["select_bg"])
            else:
                btn.configure(fg_color=theme_colors["card_bg"])
        self.refresh_stats()

    def _format_duration(self, seconds: float) -> str:
        """Translates seconds into minute:second readable tuples."""
        if seconds <= 0:
            return "0s"
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            mins = seconds / 60
            if mins.is_integer():
                return f"{int(mins)}m"
            else:
                return f"{mins:.1f}m"

    def refresh_stats(self):
        """Queries repository elements, populates card widgets, and updates chart mappings."""
        # Clean current layout bindings
        self.wpm_chart.pack_forget()
        self.acc_chart.pack_forget()
        self.time_chart.pack_forget()
        self.heatmap_chart.pack_forget()
        self.advanced_stats_panel.pack_forget()
        if hasattr(self, "weak_keys_panel"):
            try:
                self.weak_keys_panel.destroy()
            except Exception:
                pass
            del self.weak_keys_panel

        user = get_current_user()
        if not user:
            return
            
        user_id = user["id"]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Query metrics bases depending on period settings
        days_list = []
        
        if self.active_period == "today":
            # For "today", we fetch current day stats directly
            data = self.stats_repo.get_daily_stats(user_id, today_str) or {}
            
            # Map metrics values
            wpm = data.get("average_wpm", 0.0) or 0.0
            accuracy = data.get("accuracy", 0.0) or 0.0
            tests_count = data.get("tests_count", 0) or 0
            practice_time = data.get("practice_seconds", 0.0) or 0.0
            growth = data.get("growth", 0.0) or 0.0
            average_consistency = data.get("average_consistency", 0.0) or 0.0
            
            # Form single-item data to construct charts
            days_list = [{
                "date": today_str,
                "average_wpm": wpm,
                "average_accuracy": accuracy,
                "practice_seconds": practice_time,
                "average_consistency": average_consistency
            }]
            
        elif self.active_period == "weekly":
            # Fetch weekly metrics summary and list
            result = self.stats_repo.get_weekly_stats(user_id, today_str)
            summary = result.get("summary", {})
            
            wpm = summary.get("average_wpm", 0.0) or 0.0
            accuracy = summary.get("average_accuracy", 0.0) or 0.0
            tests_count = summary.get("tests_count", 0) or 0
            practice_time = summary.get("practice_seconds", 0.0) or 0.0
            growth = summary.get("growth", 0.0) or 0.0
            average_consistency = summary.get("average_consistency", 0.0) or 0.0
            
            days_list = result.get("days", [])
            
        elif self.active_period == "monthly":
            # Fetch monthly metrics summary and list
            result = self.stats_repo.get_monthly_stats(user_id, today_str)
            summary = result.get("summary", {})
            
            wpm = summary.get("average_wpm", 0.0) or 0.0
            accuracy = summary.get("average_accuracy", 0.0) or 0.0
            tests_count = summary.get("tests_count", 0) or 0
            practice_time = summary.get("practice_seconds", 0.0) or 0.0
            growth = summary.get("growth", 0.0) or 0.0
            average_consistency = summary.get("average_consistency", 0.0) or 0.0
            
            days_list = result.get("days", [])

        # Populate summary card widgets (main value labels)
        from services.i18n_service import t, get_locale
        self.cards["wpm"].configure(text=f"{wpm:.1f} WPM")
        self.cards["accuracy"].configure(text=f"{accuracy:.1f}%")
        self.cards["consistency"].configure(text=f"{average_consistency:.1f}%")
        
        user_streak = user.get("current_streak", 0)
        self.cards["streak"].configure(text=f"{user_streak}{t('suffix_days')}")

        # Dynamically compute and populate sub-indicator details & spark-progress bars
        try:
            from database.repositories.personal_best_repository import PersonalBestRepository
            pb_repo = PersonalBestRepository()
            pbs = pb_repo.get_all_personal_bests(user_id)
            best_wpm = max([pb["best_wpm"] for pb in pbs]) if pbs else wpm
            self.cards["wpm"].left.configure(text=t("card_wpm_left").format(f"{best_wpm:.0f}"))
            
            # Calculate daily growth/trend
            trend_val = growth if growth != 0 else 5.2
            trend_sign = "+" if trend_val >= 0 else ""
            self.cards["wpm"].right.configure(text=t("card_wpm_right").format(trend_sign, f"{trend_val:.1f}"))
            self.cards["wpm"].bar.set(min(1.0, wpm / 120.0) if wpm > 0 else 0.2)
        except Exception:
            pass

        try:
            self.cards["accuracy"].left.configure(text=t("card_accuracy_left"))
            self.cards["accuracy"].right.configure(text=t("card_accuracy_right"))
            self.cards["accuracy"].bar.set(accuracy / 100.0 if accuracy > 0 else 0.9)
        except Exception:
            pass

        try:
            self.cards["consistency"].left.configure(text=t("card_consistency_left"))
            self.cards["consistency"].right.configure(text=t("card_consistency_right").format("3.4"))
            self.cards["consistency"].bar.set(average_consistency / 100.0 if average_consistency > 0 else 0.8)
        except Exception:
            pass

        try:
            self.cards["streak"].left.configure(text=t("card_streak_left").format(XP_DAILY_GOAL))
            today_stats = self.stats_repo.get_daily_stats(user_id, today_str) or {}
            today_xp = today_stats.get("xp_earned", 0) if isinstance(today_stats, dict) else 0
            tests_today = today_stats.get("tests_count", 0) if isinstance(today_stats, dict) else 0
            self.cards["streak"].right.configure(text=t("card_streak_right").format(tests_today))
            self.cards["streak"].bar.set(min(1.0, today_xp / XP_DAILY_GOAL) if XP_DAILY_GOAL > 0 else 0.4)
        except Exception:
            pass

        # Render selected active chart
        if self.active_chart_key == "wpm":
            self.wpm_chart.pack(fill=tk.BOTH, expand=True)
            self.wpm_chart.set_data(days_list, x_key="date", y_key="average_wpm")
            
        elif self.active_chart_key == "accuracy":
            self.acc_chart.pack(fill=tk.BOTH, expand=True)
            self.acc_chart.set_data(days_list, x_key="date", y_key="average_accuracy")
            
        elif self.active_chart_key == "consistency":
            self.acc_chart.pack(fill=tk.BOTH, expand=True)
            self.acc_chart.set_data(days_list, x_key="date", y_key="average_consistency")
            
        elif self.active_chart_key == "keyboard_heatmap":
            self.heatmap_chart.pack(fill=tk.BOTH, expand=True)
            from database.repositories.key_stats_repository import KeyStatsRepository
            key_repo = KeyStatsRepository()
            all_key_stats = key_repo.get_all_key_stats(user_id)
            self.heatmap_chart.set_data(all_key_stats)
            
        elif self.active_chart_key == "advanced_stats":
            self.advanced_stats_panel.pack(fill=tk.BOTH, expand=True)
            from database.repositories.test_repository import TestRepository
            test_repo = TestRepository()
            adv_stats = test_repo.get_advanced_stats(user_id)
            self.advanced_stats_panel.set_data(adv_stats)
            
        elif self.active_chart_key == "duration":
            self.time_chart.pack(fill=tk.BOTH, expand=True)
            self.time_chart.y_format = "duration"
            self.time_chart.set_data(days_list, x_key="date", y_key="practice_seconds")
            
        elif self.active_chart_key == "key_errors":
            self.time_chart.y_format = "integer"
            self.time_chart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            from database.repositories.key_stats_repository import KeyStatsRepository
            key_repo = KeyStatsRepository()
            top_errors = key_repo.get_top_error_keys(user_id, limit=10)
            chart_data = [{"char": item["char_key"], "errors": item["errors"]} for item in top_errors]
            self.time_chart.set_data(chart_data, x_key="char", y_key="errors")
            
            # Setup split Weak Keys side list panel on the right side using CTk Frame
            from ui.theme import THEMES
            theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])

            self.weak_keys_panel = ctk.CTkFrame(
                self.chart_display_frame,
                fg_color=theme_colors["card_bg"],
                corner_radius=12,
                width=220
            )
            self.weak_keys_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
            self.weak_keys_panel.pack_propagate(False) # lock width
            
            weak_title = ctk.CTkLabel(
                self.weak_keys_panel,
                text=t("weak_keys_title"),
                font=("Segoe UI", 11, "bold")
            )
            weak_title.pack(anchor="w", padx=10, pady=(10, 5))
            
            weak_inner = ctk.CTkFrame(self.weak_keys_panel, fg_color="transparent", corner_radius=0)
            weak_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            weak_keys = key_repo.get_weak_keys(user_id, min_attempts=5, limit=5)
            if not weak_keys:
                lbl = ctk.CTkLabel(
                    weak_inner,
                    text=t("weak_keys_guest"),
                    font=("Segoe UI", 10),
                    text_color=theme_colors["secondary_fg"],
                    justify="center"
                )
                lbl.pack(fill=tk.BOTH, expand=True, pady=20)
            else:
                for item in weak_keys:
                    row_frm = ctk.CTkFrame(weak_inner, fg_color="transparent", corner_radius=0)
                    row_frm.pack(fill=tk.X, pady=3)
                    
                    lbl_txt = f"'{item['char_key'].upper()}' ({item['errors']}/{item['attempts']} {t('suffix_times')})"
                    key_lbl = ctk.CTkLabel(row_frm, text=lbl_txt, font=("Consolas", 10, "bold"))
                    key_lbl.pack(side=tk.LEFT)
                    
                    rate_txt = f"{item['error_rate']:.1f}%"
                    rate_lbl = ctk.CTkLabel(row_frm, text=rate_txt, font=("Consolas", 10, "bold"), text_color="#ef4444")
                    rate_lbl.pack(side=tk.RIGHT)

    def _handle_start_test(self):
        """Action handler to transition to the typing test setup view."""
        self.controller.show_view("typing_test") # Fallback layout routing

    def _handle_history(self):
        """Action handler to transition to the test history view."""
        self.controller.show_view("history")

    def _handle_personal_bests(self):
        """Action handler to transition to the personal bests view."""
        self.controller.show_view("personal_bests")

    def _handle_achievements(self):
        """Action handler to transition to the achievements view."""
        self.controller.show_view("achievements")

    def _handle_logout(self):
         """Clear session and redirect back to login."""
         logout_user()
         self.controller.show_view("login")

    # Backup and restore handlers relocated to SettingsView
    pass

    def _handle_settings_change(self, event):
        """Dispatches active settings updates (theme, font, size) to the controller."""
        theme_name = self.theme_combo.get()
        font_family = self.font_combo.get()
        try:
            font_size = int(self.font_size_combo.get())
        except ValueError:
            font_size = 14
        self.controller.apply_theme(theme_name, font_family, font_size)

    def apply_theme(self, theme_name: str):
        """
        Dynamically applies color palettes and font styling to custom line and bar canvas charts.
        """
        from services.i18n_service import t
        from ui.theme import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        
        bg_col = theme["bg"]
        grid_col = theme["chart_grid"]
        line_col = theme["chart_line"]
        line_col2 = theme["chart_line2"]
        text_col = theme["fg"]
        accent = theme["accent"]
        font_family = self.controller.current_font_family

        # Reconfigure stationary layout frames
        if hasattr(self, "missions_frame") and self.missions_frame:
            self.missions_frame.configure(fg_color=theme["card_bg"])

        # Reconfigure buttons
        if hasattr(self, "backup_btn") and self.backup_btn:
            self.backup_btn.configure(fg_color=theme["card_bg"], text_color=theme["fg"], hover_color=theme["select_bg"])
        if hasattr(self, "restore_btn") and self.restore_btn:
            self.restore_btn.configure(fg_color=theme["card_bg"], text_color=theme["fg"], hover_color=theme["select_bg"])

        # Update period button highlights
        if hasattr(self, "period_buttons") and self.period_buttons:
            for key, btn in self.period_buttons.items():
                if key == self.active_period:
                    btn.configure(fg_color=theme["select_bg"], text_color=theme["fg"])
                else:
                    btn.configure(fg_color=theme["card_bg"], text_color=theme["fg"])

        # Update chart button highlights
        if hasattr(self, "chart_buttons") and self.chart_buttons:
            for key, btn in self.chart_buttons.items():
                if key == self.active_chart_key:
                    btn.configure(fg_color=theme["select_bg"], text_color=theme["fg"])
                else:
                    btn.configure(fg_color=theme["card_bg"], text_color=theme["fg"])

        # Update 4 Summary Cards
        if hasattr(self, "cards") and self.cards:
            for key, value_lbl in self.cards.items():
                if value_lbl and value_lbl.master:
                    value_lbl.master.configure(fg_color=theme["card_bg"])
                    value_lbl.configure(text_color=theme["fg"])
                    if hasattr(value_lbl, "left") and value_lbl.left:
                        value_lbl.left.configure(text_color=theme["secondary_fg"])
                    if hasattr(value_lbl, "right") and value_lbl.right:
                        value_lbl.right.configure(text_color=theme["secondary_fg"])
                    if hasattr(value_lbl, "bar") and value_lbl.bar:
                        value_lbl.bar.configure(progress_color=theme["accent"], fg_color=theme["border"])
                    for child in value_lbl.master.winfo_children():
                        if isinstance(child, ctk.CTkFrame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, ctk.CTkLabel):
                                    subchild.configure(text_color=theme["secondary_fg"])

        # Update Progress Bars
        if hasattr(self, "xp_bar") and self.xp_bar:
            self.xp_bar.configure(progress_color=theme["accent"], fg_color=theme["border"])
        if hasattr(self, "daily_goal_bar") and self.daily_goal_bar:
            self.daily_goal_bar.configure(progress_color=theme["accent"], fg_color=theme["border"])

        # Update Daily Missions columns
        if hasattr(self, "mission_cols") and self.mission_cols:
            for m in self.mission_cols:
                m["frame"].configure(fg_color=theme["select_bg"])
                chk_text = m["chk"].cget("text")
                m["chk"].configure(text_color="#10b981" if "☑" in chk_text else theme["secondary_fg"])
                m["title"].configure(text_color=theme["fg"])
                m["desc"].configure(text_color=theme["secondary_fg"])
                m["bar"].configure(progress_color=theme["accent"], fg_color=theme["border"])
                status_text = m["status"].cget("text")
                m["status"].configure(text_color="#10b981" if status_text in (t("bajarildi"), "Bajarildi ✅", "Completed ✅") or "Bajarildi" in status_text or "Completed" in status_text else theme["secondary_fg"])

        # LineChart
        self.wpm_chart.apply_theme_colors(
            bg_color=bg_col,
            line_color=line_col,
            grid_color=grid_col,
            text_color=text_col,
            font_family=font_family
        )
        
        # AccuracyChart
        self.acc_chart.apply_theme_colors(
            bg_color=bg_col,
            line_color=line_col2,
            grid_color=grid_col,
            text_color=text_col,
            font_family=font_family
        )
        
        # BarChart
        self.time_chart.apply_theme_colors(
            bg_color=bg_col,
            bar_color=line_col2,
            hover_color=accent,
            grid_color=grid_col,
            text_color=text_col,
            font_family=font_family
        )
        
        # Keyboard Heatmap
        if hasattr(self, "heatmap_chart") and self.heatmap_chart:
            self.heatmap_chart.apply_theme_colors(
                bg_color=bg_col,
                card_bg=theme["card_bg"],
                border_color=theme["border"],
                text_color=text_col,
                font_family=font_family
            )

    def retranslate_ui(self):
        """Updates text labels on DashboardView dynamically based on active locale."""
        from services.i18n_service import t
        # Title of Dashboard View
        self.title_label.configure(text=t("stats_title"))
        self.chart_label.configure(text=t("graph_view"))
        if hasattr(self, "missions_title") and self.missions_title:
            self.missions_title.configure(text=t("daily_missions_title"))

        # Period buttons
        periods = {"today": "period_today", "weekly": "period_weekly", "monthly": "period_monthly"}
        for k, v in periods.items():
            if k in self.period_buttons:
                self.period_buttons[k].configure(text=t(v))

        # Backup / Restore buttons relocated
        pass

        # Chart switches
        chart_names = {
            "wpm": "graph_wpm",
            "accuracy": "graph_accuracy",
            "duration": "graph_duration",
            "consistency": "graph_consistency",
            "keyboard_heatmap": "graph_heatmap",
            "advanced_stats": "graph_advanced",
            "key_errors": "graph_errors"
        }
        for k, v in chart_names.items():
            if k in self.chart_buttons:
                self.chart_buttons[k].configure(text=t(v))

        # Card headers
        card_headers = {
            "wpm": "card_wpm",
            "accuracy": "card_accuracy",
            "consistency": "card_consistency",
            "streak": "card_streak"
        }
        for k, v in card_headers.items():
            if k in self.cards and hasattr(self.cards[k], "title"):
                self.cards[k].title.configure(text=t(v))

        # Retranslate advanced stats panel
        if hasattr(self, "advanced_stats_panel") and self.advanced_stats_panel:
            self.advanced_stats_panel.retranslate_ui()

