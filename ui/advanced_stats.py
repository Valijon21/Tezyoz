"""
Advanced statistics display panel widget for TypeMaster.
Presents lifetime aggregate metrics, recent trends, dial behavior, and speed-ranking categories.
"""
import tkinter as tk
from tkinter import ttk

class AdvancedStatsPanel(ttk.Frame):
    """
    Renders detailed performance insights and habits inside the dashboard area.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._last_stats = None
        self._setup_ui()

    def _setup_ui(self):
        from services.i18n_service import t
        # 1. Level rank banner container
        self.banner_frame = ttk.LabelFrame(self, text=t("adv_rank_title"), padding=10)
        self.banner_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.rank_label = ttk.Label(
            self.banner_frame,
            text="-",
            font=("Helvetica", 14, "bold"),
            foreground="#d97706", # Elegant amber rank status
            anchor="center"
        )
        self.rank_label.pack(fill=tk.X)

        # 2. Main split body container (2 columns)
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure uniform columns
        self.grid_frame.columnconfigure(0, weight=1, uniform="equal")
        self.grid_frame.columnconfigure(1, weight=1, uniform="equal")

        # Column 1: Lifetime Stats Frame
        self.left_panel = ttk.LabelFrame(self.grid_frame, text=t("adv_lifetime_title"), padding=10)
        self.left_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Column 2: Recent Trends & Habits Frame
        self.right_panel = ttk.LabelFrame(self.grid_frame, text=t("adv_trends_title"), padding=10)
        self.right_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Labels references map
        self.metric_labels = {}
        self.metric_label_headers = {}
        
        # Add metrics labels to Left Panel (Lifetime)
        left_metrics = [
            ("total_tests", "adv_total_tests"),
            ("cumulative_accuracy", "adv_cumulative_accuracy"),
            ("avg_wpm", "adv_avg_wpm"),
            ("max_wpm", "adv_max_wpm"),
            ("avg_consistency", "adv_avg_consistency"),
            ("total_duration", "adv_total_duration")
        ]
        self._build_metric_grid(self.left_panel, left_metrics)

        # Add metrics labels to Right Panel (Trends & Cumulative Characters)
        right_metrics = [
            ("last_10_avg_wpm", "adv_last_10_avg_wpm"),
            ("last_10_avg_accuracy", "adv_last_10_avg_accuracy"),
            ("last_10_avg_consistency", "adv_last_10_avg_consistency"),
            ("time_of_day_habit", "adv_time_of_day_habit"),
            ("total_characters", "adv_total_characters"),
            ("total_errors", "adv_total_errors")
        ]
        self._build_metric_grid(self.right_panel, right_metrics)

    def _build_metric_grid(self, parent_frame, metrics_config):
        from services.i18n_service import t
        for idx, (key, i18n_key) in enumerate(metrics_config):
            row_frm = ttk.Frame(parent_frame)
            row_frm.pack(fill=tk.X, pady=4)
            
            lbl = ttk.Label(row_frm, text=t(i18n_key), style="Secondary.TLabel", font=("Helvetica", 10))
            lbl.pack(side=tk.LEFT)
            
            val_lbl = ttk.Label(row_frm, text="-", font=("Helvetica", 10, "bold"))
            val_lbl.pack(side=tk.RIGHT)
            
            self.metric_labels[key] = val_lbl
            self.metric_label_headers[key] = (lbl, i18n_key)

    def retranslate_ui(self):
        from services.i18n_service import t
        self.banner_frame.configure(text=t("adv_rank_title"))
        self.left_panel.configure(text=t("adv_lifetime_title"))
        self.right_panel.configure(text=t("adv_trends_title"))
        
        for key, (lbl, i18n_key) in self.metric_label_headers.items():
            lbl.configure(text=t(i18n_key))
            
        if self._last_stats:
            self.set_data(self._last_stats)

    def set_data(self, stats: dict):
        """
        Populates aggregate metrics inside widgets labels.
        """
        if not stats:
            return
        
        self._last_stats = stats
        from services.i18n_service import t

        # Update Typing Rank label banner
        rank_key = stats.get("typing_rank", "beginner")
        translated_rank = t(f"rank_{rank_key}") or rank_key
        self.rank_label.config(text=translated_rank.upper())

        # Update lifetime and behavior metric cards text fields
        self.metric_labels["total_tests"].config(text=str(stats.get("total_tests", 0)))
        
        cum_acc = stats.get("cumulative_accuracy", 0.0)
        self.metric_labels["cumulative_accuracy"].config(text=f"{cum_acc:.1f}%")
        
        self.metric_labels["avg_wpm"].config(text=f"{stats.get('avg_wpm', 0.0):.1f} WPM")
        self.metric_labels["max_wpm"].config(text=f"{stats.get('max_wpm', 0.0):.1f} WPM")
        
        avg_cons = stats.get("avg_consistency", 0.0)
        self.metric_labels["avg_consistency"].config(text=f"{avg_cons:.1f}%")
        
        # Format lifetime practice seconds (hours vs minutes vs seconds)
        duration_sec = stats.get("total_duration", 0)
        self.metric_labels["total_duration"].config(text=self._format_duration(duration_sec))

        # Update Trends
        self.metric_labels["last_10_avg_wpm"].config(text=f"{stats.get('last_10_avg_wpm', 0.0):.1f} WPM")
        self.metric_labels["last_10_avg_accuracy"].config(text=f"{stats.get('last_10_avg_accuracy', 0.0):.1f}%")
        self.metric_labels["last_10_avg_consistency"].config(text=f"{stats.get('last_10_avg_consistency', 0.0):.1f}%")
        
        habit_key = stats.get("time_of_day_habit", "evening")
        translated_habit = t(f"habit_{habit_key}") or habit_key
        self.metric_labels["time_of_day_habit"].config(text=translated_habit)
        
        self.metric_labels["total_characters"].config(text=str(stats.get("total_characters", 0)))
        self.metric_labels["total_errors"].config(text=str(stats.get("total_errors", 0)))

    def _format_duration(self, seconds: float) -> str:
        from services.i18n_service import t
        if seconds <= 0:
            return "0s"
        if seconds < 60:
            return f"{int(seconds)} {t('dur_word_second')}"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{int(mins)} {t('dur_word_minute')}"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            if mins > 0:
                hours_mins_fmt = t("dur_word_hours_mins") or "{} hours {} minutes"
                return hours_mins_fmt.format(hours, mins)
            return f"{hours} {t('dur_word_hour')}"
