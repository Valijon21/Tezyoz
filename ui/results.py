"""
Results display panel for TypeMaster typing test performance metrics.
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
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
        self.pb_frame.pack(pady=(0, 10))
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

        from services.i18n_service import t

        # Developer Contact Header Frame (Clean container without top title label)
        self.dev_info_card = ttk.Frame(
            self.container,
            padding=(15, 10)
        )
        self.dev_info_card.pack(fill=tk.X, pady=(0, 15))

        dev_inner = ttk.Frame(self.dev_info_card)
        dev_inner.pack(fill=tk.X, expand=True)

        self.dev_info_text = ttk.Label(
            dev_inner,
            text=f"{t('dev_info_name')}   •   {t('dev_info_phone')}\n{t('dev_info_services')}",
            font=("Helvetica", 13, "bold"),
            justify="left"
        )
        self.dev_info_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.dev_contact_btn = ttk.Button(
            dev_inner,
            text=t("dev_info_contact"),
            command=self._open_telegram
        )
        self.dev_contact_btn.pack(side=tk.RIGHT, padx=5)

        # Metrics layout frame - structured in a grid (3 rows, 3 columns)
        self.metrics_frame = ttk.Frame(self.container)

        # Configure weights for responsive grid centering
        for col in range(3):
            self.metrics_frame.columnconfigure(col, weight=1, uniform="equal")
        for row in range(3):
            self.metrics_frame.rowconfigure(row, weight=1, uniform="equal")

        # Metric Cards mapping references
        self.cards = {}
        metric_configs = [
            # (row, col, key)
            (0, 0, "wpm"),
            (0, 1, "raw_wpm"),
            (0, 2, "accuracy"),
            
            (1, 0, "consistency"),
            (1, 1, "rhythm_rating"),
            (1, 2, "errors"),
            
            (2, 0, "duration"),
            (2, 1, "xp_level"),
            (2, 2, "total_chars")
        ]

        card_keys = {
            "wpm": "results_wpm",
            "raw_wpm": "results_raw_wpm",
            "accuracy": "results_accuracy",
            "consistency": "results_consistency",
            "rhythm_rating": "results_rhythm_rating",
            "errors": "results_errors",
            "duration": "results_duration",
            "xp_level": "results_xp_level",
            "total_chars": "results_total_chars"
        }

        for r, c, key in metric_configs:
            label_text = t(card_keys[key])
            card = ttk.LabelFrame(self.metrics_frame, text=label_text, padding=15)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            
            val_lbl = ttk.Label(
                card,
                text="-",
                font=("Helvetica", 22, "bold"),
                anchor="center"
            )
            val_lbl.pack(fill=tk.BOTH, expand=True, pady=10)
            
            self.cards[key] = {
                "card": card,
                "label": val_lbl
            }

        # Navigation Action Buttons row
        self.buttons_frame = ttk.Frame(self.container)
        self.buttons_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))

        self.retry_btn = ttk.Button(
            self.buttons_frame,
            text=t("results_btn_retry") or "Qaytadan urinish (Retry)",
            command=self._handle_retry
        )
        self.retry_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.home_btn = ttk.Button(
            self.buttons_frame,
            text=t("results_btn_home") or "Bosh sahifa (Home)",
            command=self._handle_home
        )
        self.home_btn.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)

        # Pack metrics_frame at the end to occupy the remaining center space
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    def set_results(self, wpm: float, raw_wpm: float, accuracy: float, errors: int,
                    duration: int, xp_earned: int, level: int, is_pb: bool = False,
                    streak: int = 0, longest_streak: int = 0, consistency: float = 100.0,
                    total_chars: int = 0):
        """
        Dynamically updates the UI card labels with final test results.
        """
        self._last_results = (wpm, raw_wpm, accuracy, errors, duration, xp_earned, level,
                              is_pb, streak, longest_streak, consistency, total_chars)
        from services.i18n_service import t

        # Toggle PB Badge
        self.pb_badge.pack_forget()
        if is_pb:
            self.pb_badge.config(text=t("results_pb_badge"))
            self.pb_badge.pack()

        # Toggle Streak Badge
        self.streak_badge.pack_forget()
        if streak > 0:
            if streak >= longest_streak and longest_streak > 0:
                flame_text = t("results_streak_record_badge").format(streak)
                self.streak_badge.config(foreground="#ea580c") # Darker orange for streak record
            else:
                flame_text = t("results_streak_badge").format(streak)
                self.streak_badge.config(foreground="#f59e0b") # Standard streak color
            self.streak_badge.config(text=flame_text)
            self.streak_badge.pack(pady=(5, 0))

        # Update cards values
        duration_suffix = t("results_suffix_seconds")
        char_suffix = t("results_suffix_chars")

        self.cards["wpm"]["label"].config(text=f"{wpm:.1f}")
        self.cards["raw_wpm"]["label"].config(text=f"{raw_wpm:.1f}")
        self.cards["accuracy"]["label"].config(text=f"{accuracy:.1f}%")
        self.cards["errors"]["label"].config(text=str(errors))
        self.cards["duration"]["label"].config(text=f"{duration}{duration_suffix}")
        self.cards["xp_level"]["label"].config(text=f"+{xp_earned} XP (Lvl {level})")
        self.cards["consistency"]["label"].config(text=f"{consistency:.1f}%")
        self.cards["total_chars"]["label"].config(text=f"{total_chars}{char_suffix}")

        # Set rhythm performance description and color
        if consistency >= 85.0:
            rating = t("results_rating_excellent")
            color = "#10b981" # Emerald green
        elif consistency >= 75.0:
            rating = t("results_rating_good")
            color = "#3b82f6" # Blue
        elif consistency >= 60.0:
            rating = t("results_rating_decent")
            color = "#eab308" # Yellow
        else:
            rating = t("results_rating_erratic")
            color = "#ef4444" # Red

        self.cards["rhythm_rating"]["label"].config(text=rating, foreground=color)

    def _handle_retry(self):
        """Action handler to restart a typing test practice session."""
        self.controller.show_view("typing_test")

    def _handle_home(self):
        """Action handler redirection back to main dashboard."""
        self.controller.show_view("home")

    def _open_telegram(self):
        """Opens Telegram contact link in user's default browser."""
        webbrowser.open("https://t.me/valijon2107")

    def retranslate_ui(self):
        """Translates all text elements to the current active locale."""
        from services.i18n_service import t
        self.title_label.config(text=t("results_title"))
        self.retry_btn.config(text=t("results_btn_retry"))
        self.home_btn.config(text=t("results_btn_home"))

        if hasattr(self, "dev_info_text") and self.dev_info_text:
            self.dev_info_text.config(
                text=f"{t('dev_info_name')}  •  {t('dev_info_phone')}\n{t('dev_info_services')}"
            )
            self.dev_contact_btn.config(text=t("dev_info_contact"))

        card_keys = {
            "wpm": "results_wpm",
            "raw_wpm": "results_raw_wpm",
            "accuracy": "results_accuracy",
            "consistency": "results_consistency",
            "rhythm_rating": "results_rhythm_rating",
            "errors": "results_errors",
            "duration": "results_duration",
            "xp_level": "results_xp_level",
            "total_chars": "results_total_chars"
        }
        for key, t_key in card_keys.items():
            if key in self.cards:
                self.cards[key]["card"].config(text=t(t_key))

        # Re-apply current results values to refresh suffixes and ratings
        if hasattr(self, "_last_results"):
            self.set_results(*self._last_results)

