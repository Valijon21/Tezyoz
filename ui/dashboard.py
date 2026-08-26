"""
Dashboard view displaying summary cards (WPM, Accuracy, Practice Time, Growth)
and integrated interactive charts (WPM, Accuracy, Duration).
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
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
    and canvas charts widgets.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.stats_repo = DailyStatsRepository()
        self.active_period = "weekly"      # default period
        self.active_chart_key = "wpm"      # default chart key

        self._setup_ui()

    def _setup_ui(self):
        # Base container pad
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        # 1. Profile information Bar
        self.profile_bar = ttk.Frame(self.container)
        self.profile_bar.pack(fill=tk.X, pady=(0, 15))

        self.welcome_label = ttk.Label(
            self.profile_bar,
            text="Foydalanuvchi: Mehmon",
            style="Title.TLabel"
        )
        self.welcome_label.pack(side=tk.LEFT)

        self.gamification_label = ttk.Label(
            self.profile_bar,
            text="Joriy Streak: 0 🔥 | Rekord: 0 kun | Bosqich: 1 (0 XP)",
            style="Secondary.TLabel"
        )
        self.gamification_label.pack(side=tk.RIGHT)

        # 1b. XP Progress Bar Area
        self.xp_container = ttk.Frame(self.container)
        self.xp_container.pack(fill=tk.X, pady=(5, 5))

        self.xp_bar = ttk.Progressbar(
            self.xp_container,
            orient="horizontal",
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.xp_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.xp_percent_label = ttk.Label(
            self.xp_container,
            text="0.0% (0/100 XP)",
            style="Secondary.TLabel"
        )
        self.xp_percent_label.pack(side=tk.RIGHT)

        # 1c. Daily Goal Progress Bar Area
        self.daily_goal_container = ttk.Frame(self.container)
        self.daily_goal_container.pack(fill=tk.X, pady=(2, 5))

        self.daily_goal_bar = ttk.Progressbar(
            self.daily_goal_container,
            orient="horizontal",
            mode="determinate",
            style="Horizontal.TProgressbar"
        )
        self.daily_goal_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.daily_goal_label = ttk.Label(
            self.daily_goal_container,
            text="Bugungi Maqsad: 0.0% (0/100 XP)",
            style="Secondary.TLabel"
        )
        self.daily_goal_label.pack(side=tk.RIGHT)

        # Separator line
        ttk.Separator(self.container, orient="horizontal").pack(fill=tk.X, pady=(0, 15))

        # Daily Missions Group
        self.missions_frame = ttk.LabelFrame(
            self.container, 
            text="Bugungi Vazifalar (Daily Missions)", 
            padding=10
        )
        self.missions_frame.pack(fill=tk.X, pady=(0, 15))

        self.mission_cols = []
        for i in range(3):
            col_frame = ttk.Frame(self.missions_frame)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)

            title_lbl = ttk.Label(col_frame, text="-", font=("Helvetica", 10, "bold"))
            title_lbl.pack(anchor="w")

            desc_lbl = ttk.Label(col_frame, text="-", style="Secondary.TLabel", wraplength=220)
            desc_lbl.pack(anchor="w", pady=2)

            progress_bar = ttk.Progressbar(col_frame, orient="horizontal", mode="determinate")
            progress_bar.pack(fill=tk.X, pady=2)

            status_lbl = ttk.Label(col_frame, text="-", font=("Helvetica", 9, "italic"))
            status_lbl.pack(anchor="w")

            self.mission_cols.append({
                "frame": col_frame,
                "title": title_lbl,
                "desc": desc_lbl,
                "bar": progress_bar,
                "status": status_lbl
            })

        # 2. Statistics Period Filters & Title
        self.filter_bar = ttk.Frame(self.container)
        self.filter_bar.pack(fill=tk.X, pady=(0, 15))

        self.title_label = ttk.Label(
            self.filter_bar,
            text="Statistika Tahlili",
            style="Title.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)

        self.period_buttons = {}
        periods_config = [("today", "Bugun"), ("weekly", "Haftalik"), ("monthly", "Oylik")]
        
        # Period picker controls (arranged right to left)
        period_frame = ttk.Frame(self.filter_bar)
        period_frame.pack(side=tk.RIGHT)
        
        for key, text in periods_config:
            btn = ttk.Button(
                period_frame,
                text=text,
                command=lambda k=key: self._set_period(k),
                width=10
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.period_buttons[key] = btn

        # 3. Summary Cards Grid Layout
        self.cards_frame = ttk.Frame(self.container)
        self.cards_frame.pack(fill=tk.X, pady=(0, 15))
        
        for col in range(6):
            self.cards_frame.columnconfigure(col, weight=1, uniform="equal")

        self.cards = {}
        card_configs = [
            (0, "wpm", "Tezlik (WPM)"),
            (1, "accuracy", "Aniqlik (%)"),
            (2, "tests_count", "Testlar Soni"),
            (3, "practice_time", "Mashq Vaqti"),
            (4, "consistency", "Ritm (Consistency)"),
            (5, "growth", "O'sish (Tezlik)")
        ]

        for col, key, title in card_configs:
            frame = ttk.LabelFrame(self.cards_frame, text=title, padding=10)
            frame.grid(row=0, column=col, padx=4, sticky="nsew")
            
            value_lbl = ttk.Label(
                frame,
                text="-",
                style="CardValue.TLabel",
                anchor="center"
            )
            value_lbl.pack(fill=tk.X, expand=True, pady=5)
            self.cards[key] = value_lbl

        # 4. Chart switch buttons
        self.chart_switch_bar = ttk.Frame(self.container)
        self.chart_switch_bar.pack(fill=tk.X, pady=(0, 10))

        self.chart_label = ttk.Label(
            self.chart_switch_bar,
            text="Grafik Ko'rinishi:"
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
            btn = ttk.Button(
                self.chart_switch_bar,
                text=text,
                command=lambda k=key: self._set_chart_type(k),
                width=17
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.chart_buttons[key] = btn

        # 6. Bottom Navigation Controls
        self.nav_bar = ttk.Frame(self.container)
        self.nav_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # 5. Charts Container Area
        self.chart_display_frame = ttk.Frame(self.container, height=self.scale_px(260))
        self.chart_display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, self.scale_px(15)))
        self.chart_display_frame.pack_propagate(False) # lock minimum height for drawing bounds safely


        # Instantiate all 3 visual widgets
        self.wpm_chart = LineChart(self.chart_display_frame)
        self.acc_chart = AccuracyChart(self.chart_display_frame)
        self.time_chart = BarChart(self.chart_display_frame)
        self.heatmap_chart = KeyboardHeatmap(self.chart_display_frame)
        self.advanced_stats_panel = AdvancedStatsPanel(self.chart_display_frame)

        self.start_test_btn = ttk.Button(
            self.nav_bar,
            text="★ Mashqni Boshlash (Start Test) ★",
            style="Accent.TButton", # optional fallback
            command=self._handle_start_test
        )
        self.start_test_btn.pack(side=tk.LEFT, ipadx=10, ipady=5)

        self.history_btn = ttk.Button(
            self.nav_bar,
            text="Tarix (History)",
            command=self._handle_history
        )
        self.history_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=5)

        self.pb_btn = ttk.Button(
            self.nav_bar,
            text="Rekordlar (PBs)",
            command=self._handle_personal_bests
        )
        self.pb_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=5)

        self.achievements_btn = ttk.Button(
            self.nav_bar,
            text="Yutuqlar (Achievements)",
            command=self._handle_achievements
        )
        self.achievements_btn.pack(side=tk.LEFT, padx=(10, 0), ipady=5)

        self.logout_btn = ttk.Button(
            self.nav_bar,
            text="Chiqish (Logout)",
            command=self._handle_logout
        )
        self.logout_btn.pack(side=tk.RIGHT, ipady=5)

        # Settings Toolbar on the right side next to logout
        self.settings_frame = ttk.Frame(self.nav_bar)
        self.settings_frame.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Theme dropdown
        ttk.Label(self.settings_frame, text="Mavzu:").pack(side=tk.LEFT, padx=(5, 3))
        self.theme_combo = ttk.Combobox(
            self.settings_frame,
            values=["dark", "light", "cyberpunk"],
            width=10,
            state="readonly"
        )
        self.theme_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.theme_combo.bind("<<ComboboxSelected>>", self._handle_settings_change)

        # Font family dropdown
        ttk.Label(self.settings_frame, text="Shrift:").pack(side=tk.LEFT, padx=(5, 3))
        self.font_combo = ttk.Combobox(
            self.settings_frame,
            values=["Consolas", "Courier New", "Arial", "Trebuchet MS"],
            width=12,
            state="readonly"
        )
        self.font_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.font_combo.bind("<<ComboboxSelected>>", self._handle_settings_change)

        # Font size dropdown
        ttk.Label(self.settings_frame, text="O'lcham:").pack(side=tk.LEFT, padx=(5, 3))
        self.font_size_combo = ttk.Combobox(
            self.settings_frame,
            values=["10", "12", "14", "16", "18", "20"],
            width=5,
            state="readonly"
        )
        self.font_size_combo.pack(side=tk.LEFT)
        self.font_size_combo.bind("<<ComboboxSelected>>", self._handle_settings_change)

        # Backup button
        self.backup_btn = ttk.Button(
            self.settings_frame,
            text="Zaxiralash",
            command=self._handle_backup,
            width=10
        )
        self.backup_btn.pack(side=tk.LEFT, padx=(10, 3))

        # Restore button
        self.restore_btn = ttk.Button(
            self.settings_frame,
            text="Tiklash",
            command=self._handle_restore,
            width=10
        )
        self.restore_btn.pack(side=tk.LEFT, padx=3)

    def on_show(self):
        """Standard lifecycle hook called when home/dashboard view transitions active."""
        # Sync settings combobox values
        if hasattr(self, "theme_combo"):
            self.theme_combo.set(self.controller.current_theme)
        if hasattr(self, "font_combo"):
            self.font_combo.set(self.controller.current_font_family)
        if hasattr(self, "font_size_combo"):
            self.font_size_combo.set(str(self.controller.current_font_size))
            
        # Update styling parameters
        self.apply_theme(self.controller.current_theme)

        # 1. Update user identity header information
        user = get_current_user()
        if user:
            name = user.get("display_name") or user.get("username", "Mehmon")
            streak = user.get("current_streak", 0)
            longest_streak = user.get("longest_streak", 0)
            xp = user.get("xp", 0)
            
            from gamification.levels import get_level_progress
            level, xp_in_level, xp_needed = get_level_progress(xp)
            
            self.welcome_label.config(text=f"Foydalanuvchi: {name}")
            self.gamification_label.config(text=f"Joriy Streak: {streak} 🔥 | Rekord: {longest_streak} kun | Bosqich: {level} ({xp} XP)")
            
            self.xp_bar["maximum"] = xp_needed
            self.xp_bar["value"] = xp_in_level
            percent = (xp_in_level / xp_needed) * 100
            self.xp_percent_label.config(text=f"{percent:.1f}% ({xp_in_level}/{xp_needed} XP)")

            # Update daily goal progress
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_stats = self.stats_repo.get_daily_stats(user["id"], today_str)
            today_xp = today_stats.get("xp_earned", 0) if isinstance(today_stats, dict) else 0

            self.daily_goal_bar["maximum"] = XP_DAILY_GOAL
            self.daily_goal_bar["value"] = min(today_xp, XP_DAILY_GOAL)
            goal_percent = (today_xp / XP_DAILY_GOAL) * 100
            self.daily_goal_label.config(text=f"Bugungi Maqsad: {goal_percent:.1f}% ({today_xp}/{XP_DAILY_GOAL} XP)")

            # Update daily missions
            from services.daily_missions_service import DailyMissionsService
            missions_service = DailyMissionsService()
            missions = missions_service.get_or_generate_daily_missions(user["id"], today_str)
            for i, mission in enumerate(missions):
                if i < len(self.mission_cols):
                    col = self.mission_cols[i]
                    col["title"].config(text=f"{mission['title']} (+{mission['xp_reward']} XP)")
                    col["desc"].config(text=mission["description"])
                    
                    progress = mission["progress"]
                    target = mission["target"]
                    col["bar"]["maximum"] = target
                    col["bar"]["value"] = progress
                    
                    if mission["completed"]:
                        status_text = "Bajarildi ✅"
                        col["status"].config(text=status_text, foreground="#10b981") # Green
                    else:
                        status_text = f"Progress: {progress}/{target}"
                        col["status"].config(text=status_text, foreground="#8e9196") # Grey
        else:
            self.welcome_label.config(text="Foydalanuvchi: Mehmon")
            self.gamification_label.config(text="Joriy Streak: 0 🔥 | Rekord: 0 kun | Bosqich: 1 (0 XP)")
            
            self.xp_bar["maximum"] = 100
            self.xp_bar["value"] = 0
            self.xp_percent_label.config(text="0.0% (0/100 XP)")

            self.daily_goal_bar["maximum"] = XP_DAILY_GOAL
            self.daily_goal_bar["value"] = 0
            self.daily_goal_label.config(text=f"Bugungi Maqsad: 0.0% (0/{XP_DAILY_GOAL} XP)")

            # Muted guest defaults
            for col in self.mission_cols:
                col["title"].config(text="-")
                col["desc"].config(text="Kirib, vazifalarni ochish mumkin")
                col["bar"]["value"] = 0
                col["status"].config(text="-", foreground="#8e9196")

        # 2. Reload data and redraw active charts
        self.refresh_stats()

    def _set_period(self, period_key: str):
        """Sets active date boundary and triggers statistical updates."""
        self.active_period = period_key
        self.refresh_stats()

    def _set_chart_type(self, chart_key: str):
        """Swaps active canvas view widget and reloads layout draw mapping."""
        self.active_chart_key = chart_key
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

        # Populate summary card widgets
        self.cards["wpm"].config(text=f"{wpm:.1f} WPM")
        self.cards["accuracy"].config(text=f"{accuracy:.1f}%")
        self.cards["tests_count"].config(text=str(tests_count))
        self.cards["practice_time"].config(text=self._format_duration(practice_time))
        self.cards["consistency"].config(text=f"{average_consistency:.1f}%")
        
        # Color growth card depending on value
        growth_text = f"{growth:+.1f}%"
        if growth > 0:
            self.cards["growth"].config(text=growth_text, foreground="#10b981") # emerald green
        elif growth < 0:
            self.cards["growth"].config(text=growth_text, foreground="#ef4444") # red
        else:
            self.cards["growth"].config(text=growth_text, foreground="#646669") # gray

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
            
            # Setup split Weak Keys side list panel on the right side
            self.weak_keys_panel = ttk.LabelFrame(
                self.chart_display_frame,
                text="Zaif Tugmalar (Xatolik %)",
                padding=10,
                width=220
            )
            self.weak_keys_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(15, 0))
            
            weak_keys = key_repo.get_weak_keys(user_id, min_attempts=5, limit=5)
            if not weak_keys:
                lbl = ttk.Label(
                    self.weak_keys_panel,
                    text="Tugmalar tahlili uchun matn\nyozish mashqlarini bajaring\n(kamida 5 ta urinish)",
                    style="Secondary.TLabel",
                    justify="center"
                )
                lbl.pack(fill=tk.BOTH, expand=True, pady=20)
            else:
                for item in weak_keys:
                    row_frm = ttk.Frame(self.weak_keys_panel)
                    row_frm.pack(fill=tk.X, pady=3)
                    
                    lbl_txt = f"'{item['char_key'].upper()}' ({item['errors']}/{item['attempts']} marta)"
                    key_lbl = ttk.Label(row_frm, text=lbl_txt, font=("Consolas", 10, "bold"))
                    key_lbl.pack(side=tk.LEFT)
                    
                    rate_txt = f"{item['error_rate']:.1f}%"
                    rate_lbl = ttk.Label(row_frm, text=rate_txt, font=("Consolas", 10, "bold"), foreground="#ef4444")
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

    def _handle_backup(self):
        """Creates a safe database backup using SQLite connection backup API."""
        from tkinter import filedialog, messagebox
        import sqlite3
        from database.connection import db

        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            initialfile="typemaster_backup.db",
            title="Ma'lumotlar bazasini zaxiralash"
        )
        if not file_path:
            return

        try:
            src_conn = sqlite3.connect(str(db.database_path))
            dst_conn = sqlite3.connect(file_path)
            with src_conn, dst_conn:
                src_conn.backup(dst_conn)
            src_conn.close()
            dst_conn.close()
            messagebox.showinfo("Zaxiralash", "Ma'lumotlar bazasi zaxira nusxasi muvaffaqiyatli saqlandi!")
        except Exception as err:
            messagebox.showerror("Xato", f"Zaxiralashda xatolik yuz berdi: {err}")

    def _handle_restore(self):
        """Restores database content from file copy and reloads current views."""
        from tkinter import filedialog, messagebox
        import sqlite3
        from database.connection import db

        file_path = filedialog.askopenfilename(
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            title="Tiklash uchun zaxira faylini tanlang"
        )
        if not file_path:
            return

        if not messagebox.askyesno("Tasdiqlash", "Tizim ma'lumotlarini ushbu zaxira faylidan tiklamoqchimisiz? Joriy ma'lumotlar o'chib ketadi!"):
            return

        try:
            # Validate selected file is a valid database containing users table
            check_conn = sqlite3.connect(file_path)
            cursor = check_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            has_users = cursor.fetchone()
            check_conn.close()

            if not has_users:
                messagebox.showerror("Xato", "Tanlangan fayl yaroqli TypeMaster zaxira fayli emas!")
                return

            src_conn = sqlite3.connect(file_path)
            dst_conn = sqlite3.connect(str(db.database_path))
            with src_conn, dst_conn:
                src_conn.backup(dst_conn)
            src_conn.close()
            dst_conn.close()

            messagebox.showinfo("Tiklash", "Ma'lumotlar muvaffaqiyatli tiklandi!\nO'zgarishlarni ko'rish uchun ilovani qayta ishga tushiring yoki statsni yangilang.")
            self.refresh_stats()
        except Exception as err:
            messagebox.showerror("Xato", f"Ma'lumotlarni tiklashda xatolik yuz berdi: {err}")

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
        from ui.theme import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        
        bg_col = theme["bg"]
        grid_col = theme["chart_grid"]
        line_col = theme["chart_line"]
        line_col2 = theme["chart_line2"]
        text_col = theme["fg"]
        accent = theme["accent"]
        font_family = self.controller.current_font_family
        
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

