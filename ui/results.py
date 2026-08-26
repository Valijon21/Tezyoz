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

        # Metrics layout frame - structured in a grid
        self.metrics_frame = ttk.Frame(self.container)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Configure weights for responsive grid centering
        for col in range(3):
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
            (1, 0, "errors", "Xatolar", ""),
            (1, 1, "duration", "Vaqt", " soniya"),
            (1, 2, "xp_level", "XP / Bosqich", "")
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
        self.buttons_frame.pack(fill=tk.X, pady=(20, 0))

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

    def set_results(self, wpm: float, raw_wpm: float, accuracy: float, errors: int,
                    duration: int, xp_earned: int, level: int, is_pb: bool = False):
        """
        Dynamically updates the UI card labels with final test results.
        """
        # Toggle PB Badge
        self.pb_badge.pack_forget()
        if is_pb:
            self.pb_badge.pack()

        # Update cards values
        self.cards["wpm"]["label"].config(text=f"{wpm:.1f}")
        self.cards["raw_wpm"]["label"].config(text=f"{raw_wpm:.1f}")
        self.cards["accuracy"]["label"].config(text=f"{accuracy:.1f}%")
        self.cards["errors"]["label"].config(text=str(errors))
        self.cards["duration"]["label"].config(text=f"{duration}{self.cards['duration']['suffix']}")
        self.cards["xp_level"]["label"].config(text=f"+{xp_earned} XP (Lvl {level})")

    def _handle_retry(self):
        """Action handler to restart a typing test practice session."""
        self.controller.show_view("home")

    def _handle_home(self):
        """Action handler redirection back to main dashboard."""
        self.controller.show_view("home")
