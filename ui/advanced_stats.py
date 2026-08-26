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
        self._setup_ui()

    def _setup_ui(self):
        # 1. Level rank banner container
        self.banner_frame = ttk.LabelFrame(self, text="Sizning Toifangiz (Typing Rank)", padding=10)
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
        self.left_panel = ttk.LabelFrame(self.grid_frame, text="Umumiy Ko'rsatkichlar (Lifetime)", padding=10)
        self.left_panel.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Column 2: Recent Trends & Habits Frame
        self.right_panel = ttk.LabelFrame(self.grid_frame, text="Tendensiyalar & Odatlar (Trends)", padding=10)
        self.right_panel.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Labels references map
        self.metric_labels = {}
        
        # Add metrics labels to Left Panel (Lifetime)
        left_metrics = [
            ("total_tests", "Jami testlar soni:"),
            ("cumulative_accuracy", "Umumiy aniqlik (harfma-harf):"),
            ("avg_wpm", "O'rtacha tezlik (WPM):"),
            ("max_wpm", "Maksimal tezlik (WPM):"),
            ("avg_consistency", "O'rtacha Ritm (Consistency):"),
            ("total_duration", "Jami mashq vaqti:")
        ]
        self._build_metric_grid(self.left_panel, left_metrics)

        # Add metrics labels to Right Panel (Trends & Cumulative Characters)
        right_metrics = [
            ("last_10_avg_wpm", "Oxirgi 10 test tezligi (WPM):"),
            ("last_10_avg_accuracy", "Oxirgi 10 test aniqligi (%):"),
            ("last_10_avg_consistency", "Oxirgi 10 test ritmi (%):"),
            ("time_of_day_habit", "Ko'p mashq qilish vaqti:"),
            ("total_characters", "Jami yozilgan harflar:"),
            ("total_errors", "Jami xatoliklar soni:")
        ]
        self._build_metric_grid(self.right_panel, right_metrics)

    def _build_metric_grid(self, parent_frame, metrics_config):
        for idx, (key, label_text) in enumerate(metrics_config):
            row_frm = ttk.Frame(parent_frame)
            row_frm.pack(fill=tk.X, pady=4)
            
            lbl = ttk.Label(row_frm, text=label_text, style="Secondary.TLabel", font=("Helvetica", 10))
            lbl.pack(side=tk.LEFT)
            
            val_lbl = ttk.Label(row_frm, text="-", font=("Helvetica", 10, "bold"))
            val_lbl.pack(side=tk.RIGHT)
            
            self.metric_labels[key] = val_lbl

    def set_data(self, stats: dict):
        """
        Populates aggregate metrics inside widgets labels.
        """
        if not stats:
            return

        # Update Typing Rank label banner
        self.rank_label.config(text=stats.get("typing_rank", "-").upper())

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
        
        self.metric_labels["time_of_day_habit"].config(text=stats.get("time_of_day_habit", "-"))
        self.metric_labels["total_characters"].config(text=str(stats.get("total_characters", 0)))
        self.metric_labels["total_errors"].config(text=str(stats.get("total_errors", 0)))

    def _format_duration(self, seconds: float) -> str:
        if seconds <= 0:
            return "0s"
        if seconds < 60:
            return f"{int(seconds)} soniya"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{int(mins)} daqiqa"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            if mins > 0:
                return f"{hours} soat {mins} daqiqa"
            return f"{hours} soat"
