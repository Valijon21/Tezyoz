"""
Results display panel for TypeMaster typing test performance metrics.
"""
import tkinter as tk
from tkinter import ttk
from ui.base import BaseView

class ResultsView(BaseView):
    """
    Renders detailed performance statistics after a typing practice ends.
    Shows WPM, Raw WPM, Accuracy, Errors count, duration, XP, Level, and Personal Best status.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self._setup_ui()
        # Subscribe to typing test completion events
        self.controller.event_bus.subscribe("test:completed", self.set_results)


    def _setup_ui(self):
        # Master padding container with stylish padding
        self.container = ttk.Frame(self, padding=30)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Title block
        self.title_label = ttk.Label(
            self.container,
            text="Mashq Natijalari",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=(0, 20))

        # Personal Best Badge container
        self.pb_frame = ttk.Frame(self.container)
        self.pb_frame.pack(pady=(0, 15))
        self.pb_badge = ttk.Label(
            self.pb_frame,
            text="★ YANGI REKORD ★",
            font=("Helvetica", 14, "bold"),
            foreground="#d97706" # Elegant amber
        )
        self.streak_badge = ttk.Label(
            self.pb_frame,
            text="",
            font=("Helvetica", 14, "bold"),
            foreground="#f59e0b" # Orange/Gold color for flame
        )

        # Metrics layout frame - structured in a grid (2 rows, 4 columns)
        self.metrics_frame = ttk.Frame(self.container)

        # Configure weights for responsive grid centering
        for col in range(4):
            self.metrics_frame.columnconfigure(col, weight=1, uniform="equal")
        for row in range(2):
            self.metrics_frame.rowconfigure(row, weight=1, uniform="equal")

        # Metric Cards mapping references
        self.cards = {}
        metric_configs = [
            # (row, col, key, label_text, value_suffix)
            (0, 0, "wpm", "Net WPM (Tezlik)", ""),
            (0, 1, "raw_wpm", "Raw WPM (Jami)", ""),
            (0, 2, "accuracy", "Aniqlik", "%"),
            (0, 3, "consistency", "Ritm (Consistency)", "%"),
            (1, 0, "errors", "Xatolar", ""),
            (1, 1, "duration", "Vaqt", " soniya"),
            (1, 2, "xp_level", "XP / Bosqich", ""),
            (1, 3, "rhythm_rating", "Ritm Bahosi", "")
        ]

        for r, c, key, label_text, suffix in metric_configs:
            card = ttk.LabelFrame(self.metrics_frame, text=label_text, padding=15)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            
            val_lbl = ttk.Label(
                card,
                text="-",
                font=("Helvetica", 20, "bold"),
                anchor="center"
            )
            val_lbl.pack(fill=tk.BOTH, expand=True, pady=10)
            
            self.cards[key] = {
                "label": val_lbl,
                "suffix": suffix
            }

        # Navigation Action Buttons row
        self.buttons_frame = ttk.Frame(self.container)
        self.buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(20, 0))

        self.retry_btn = ttk.Button(
            self.buttons_frame,
            text="Qaytadan urinish (Retry)",
            command=self._handle_retry
        )
        self.retry_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.home_btn = ttk.Button(
            self.buttons_frame,
            text="Bosh sahifa (Home)",
            command=self._handle_home
        )
        self.home_btn.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)

        # Pack metrics_frame at the end to occupy the remaining center space
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def set_results(self, wpm: float, raw_wpm: float, accuracy: float, errors: int,
                    duration: int, xp_earned: int, level: int, is_pb: bool = False,
                    streak: int = 0, longest_streak: int = 0, consistency: float = 100.0):
        """
        Dynamically updates the UI card labels with final test results.
        """
        # Toggle PB Badge
        self.pb_badge.pack_forget()
        if is_pb:
            self.pb_badge.pack()

        # Toggle Streak Badge
        self.streak_badge.pack_forget()
        if streak > 0:
            flame_text = f"Joriy Streak: {streak} kun 🔥"
            if streak >= longest_streak and longest_streak > 0:
                flame_text = f"★ YANGI REKORD STREAK: {streak} kun 🔥 ★"
                self.streak_badge.config(foreground="#ea580c") # Darker orange for streak record
            else:
                self.streak_badge.config(foreground="#f59e0b") # Standard streak color
            self.streak_badge.config(text=flame_text)
            self.streak_badge.pack(pady=(5, 0))

        # Update cards values
        self.cards["wpm"]["label"].config(text=f"{wpm:.1f}")
        self.cards["raw_wpm"]["label"].config(text=f"{raw_wpm:.1f}")
        self.cards["accuracy"]["label"].config(text=f"{accuracy:.1f}%")
        self.cards["errors"]["label"].config(text=str(errors))
        self.cards["duration"]["label"].config(text=f"{duration}{self.cards['duration']['suffix']}")
        self.cards["xp_level"]["label"].config(text=f"+{xp_earned} XP (Lvl {level})")
        self.cards["consistency"]["label"].config(text=f"{consistency:.1f}%")

        # Set rhythm performance description and color
        if consistency >= 85.0:
            rating = "A'lo (Excellent) ⚡"
            color = "#10b981" # Emerald green
        elif consistency >= 75.0:
            rating = "Yaxshi (Good) 👍"
            color = "#3b82f6" # Blue
        elif consistency >= 60.0:
            rating = "O'rtacha (Decent) 😐"
            color = "#eab308" # Yellow
        else:
            rating = "Sust (Erratic) ⚠️"
            color = "#ef4444" # Red

        self.cards["rhythm_rating"]["label"].config(text=rating, foreground=color)

    def _handle_retry(self):
        """Action handler to restart a typing test practice session."""
        self.controller.show_view("typing_test")

    def _handle_home(self):
        """Action handler redirection back to main dashboard."""
        self.controller.show_view("home")

