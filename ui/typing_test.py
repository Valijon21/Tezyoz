"""
Typing test practice panel for TypeMaster application.
Provides interactive typing test interface with character highlight and live metrics.
Binds Escape / Tab shortcuts to quickly restart the typing session.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.base import BaseView
from engine.test_config import TestConfig
from engine.typing_engine import TypingEngine
from ui.theme import THEMES
from database.connection import db

class TypingTestView(BaseView):
    """
    Renders interactive typing test canvas.
    Listens to keyboard events to check correctness, update live indicators, and trigger restarts.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.engine = None
        self.timer_id = None
        
        # State variables for filters mapping
        self.lang_var = tk.StringVar(value="English")
        self.dur_var = tk.StringVar(value="60")
        
        self._setup_ui()

    def _setup_ui(self):
        # Container frame
        self.container = ttk.Frame(self, padding=30)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Title Block
        self.title_label = ttk.Label(
            self.container,
            text="Matn Terish Mashqi",
            style="Title.TLabel"
        )
        self.title_label.pack(pady=(0, 10))

        # Config Panel / Selectors
        self.config_frame = ttk.Frame(self.container)
        self.config_frame.pack(pady=5)

        ttk.Label(self.config_frame, text="Til:").pack(side=tk.LEFT, padx=(5, 3))
        self.lang_combo = ttk.Combobox(
            self.config_frame,
            textvariable=self.lang_var,
            values=["English", "Russian", "Uzbek"],
            width=10,
            state="readonly"
        )
        self.lang_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_config_change)

        ttk.Label(self.config_frame, text="Vaqt:").pack(side=tk.LEFT, padx=(5, 3))
        self.dur_combo = ttk.Combobox(
            self.config_frame,
            textvariable=self.dur_var,
            values=["15", "30", "60", "120"],
            width=6,
            state="readonly"
        )
        self.dur_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.dur_combo.bind("<<ComboboxSelected>>", self._on_config_change)

        # Metrics Display row
        self.metrics_frame = ttk.Frame(self.container)
        self.metrics_frame.pack(fill=tk.X, pady=10)

        self.time_lbl = ttk.Label(self.metrics_frame, text="Vaqt: 60s", font=("Helvetica", 14, "bold"))
        self.time_lbl.pack(side=tk.LEFT, expand=True)

        self.wpm_lbl = ttk.Label(self.metrics_frame, text="Tezlik: 0.0 WPM", font=("Helvetica", 14, "bold"))
        self.wpm_lbl.pack(side=tk.LEFT, expand=True)

        self.acc_lbl = ttk.Label(self.metrics_frame, text="Aniqlik: 0.0%", font=("Helvetica", 14, "bold"))
        self.acc_lbl.pack(side=tk.LEFT, expand=True)

        # Word-canvas board frame
        self.canvas_frame = ttk.LabelFrame(self.container, text=" Yozish maydoni ", padding=20)

        # tk.Text used as the word rander viewport
        self.text_widget = tk.Text(
            self.canvas_frame,
            wrap=tk.WORD,
            state="disabled",
            highlightthickness=0,
            bd=0,
            padx=10,
            pady=10,
            height=6
        )

        # Info & Instructions footer
        self.info_lbl = ttk.Label(
            self.container,
            text="Yozishni boshlang... (Qayta boshlash: Escape / Tab, Orqaga: Dashboard orqali)",
            style="Secondary.TLabel"
        )
        self.info_lbl.pack(side=tk.BOTTOM, pady=10)

        # Bottom Controller Controls
        self.button_frame = ttk.Frame(self.container)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.restart_btn = ttk.Button(
            self.button_frame,
            text="Qayta boshlash (Restart)",
            command=self.reset_test
        )
        self.restart_btn.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

        self.back_btn = ttk.Button(
            self.button_frame,
            text="Dashboardga qaytish",
            command=self._handle_back
        )
        self.back_btn.pack(side=tk.RIGHT, padx=10, expand=True, fill=tk.X)

        # Pack canvas frame at the end to occupy the remaining center space
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

    def _on_config_change(self, event=None):
        """Called when language or duration is changed."""
        self.reset_test()

    def reset_test(self):
        """Cancels current timer and builds a fresh TypingEngine instance."""
        self.cancel_timer()
        
        # Read parameters
        language = self.lang_var.get()
        try:
            duration = int(self.dur_var.get())
        except ValueError:
            duration = 60

        config = TestConfig(language, duration)
        self.engine = TypingEngine(config)
        self.engine.add_callback(self._on_engine_change)

        # Update input text displaying target text
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", self.engine.target_text)
        
        # Apply center alignment
        self.text_widget.tag_configure("center", justify="center")
        self.text_widget.tag_add("center", "1.0", "end")
        
        # Mark all as untyped
        self.text_widget.tag_add("untyped", "1.0", "end")
        self.text_widget.config(state="disabled")

        # Reset labels
        self.time_lbl.config(text=f"Vaqt: {duration}s")
        self.wpm_lbl.config(text="Tezlik: 0.0 WPM")
        self.acc_lbl.config(text="Aniqlik: 0.0%")
        self.info_lbl.config(text="Yozishni boshlang... (Qayta boshlash: Escape / Tab)", foreground="")

        # Refresh themes config
        self.apply_theme(self.controller.current_theme)

    def _on_key_press(self, event):
        """Intercepts keyboard inputs and routes to engine."""
        if not self.engine or self.engine.is_finished:
            return "break"

        # Intercept Escape & Tab for restarts
        if event.keysym in ("Escape", "Cancel", "Tab"):
            self.reset_test()
            return "break"

        from engine.keyboard_handler import process_key_event
        action, val = process_key_event(event)

        if action == "backspace":
            self.engine.backspace()
        elif action == "input" and val is not None:
            self.engine.input_character(val)

        return "break"

    def _on_engine_change(self, engine):
        """Observes character typed states and updates text highlights colors."""
        typed_len = len(engine.typed_text)
        
        self.text_widget.config(state="normal")
        
        # Clear caret tag
        self.text_widget.tag_remove("current", "1.0", "end")

        # Repaint local index buffers to ensure quick colorization
        for i in range(max(0, typed_len - 3), typed_len + 2):
            if i >= len(engine.target_text):
                continue
            char_pos = f"1.0 + {i} chars"
            char_pos_next = f"1.0 + {i+1} chars"

            self.text_widget.tag_remove("untyped", char_pos, char_pos_next)
            self.text_widget.tag_remove("correct", char_pos, char_pos_next)
            self.text_widget.tag_remove("incorrect", char_pos, char_pos_next)

            status = engine.get_char_status(i)
            if status == "correct":
                self.text_widget.tag_add("correct", char_pos, char_pos_next)
            elif status == "incorrect":
                self.text_widget.tag_add("incorrect", char_pos, char_pos_next)
            else:
                self.text_widget.tag_add("untyped", char_pos, char_pos_next)

        # Mark current caret letter
        if typed_len < len(engine.target_text):
            self.text_widget.tag_add("current", f"1.0 + {typed_len} chars", f"1.0 + {typed_len+1} chars")
            self.text_widget.see(f"1.0 + {typed_len} chars")

        self.text_widget.config(state="disabled")

        # Metrics updates
        self.wpm_lbl.config(text=f"Tezlik: {engine.get_wpm():.1f} WPM")
        self.acc_lbl.config(text=f"Aniqlik: {engine.get_accuracy():.1f}%")

        # Activate timer checking on first typed keystroke
        if engine.is_active and self.timer_id is None:
            self._start_timer_loop()

        if engine.is_finished:
            self._handle_test_completed()

    def _start_timer_loop(self):
        """Tick down remaining duration limit counts."""
        if not self.engine or not self.engine.is_active:
            return

        self.engine.tick()
        rem_sec = int(self.engine.get_remaining_time())
        self.time_lbl.config(text=f"Vaqt: {rem_sec}s")

        if self.engine.is_finished:
            self._handle_test_completed()
        else:
            self.timer_id = self.after(1000, self._start_timer_loop)

    def cancel_timer(self):
        """Stops active tkinter duration callback routines."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def _handle_test_completed(self):
        self.cancel_timer()

        from services.auth_service import get_current_user, refresh_current_user
        user = get_current_user()
        if not user:
            return

        user_id = user["id"]
        wpm = self.engine.get_wpm()
        raw_wpm = self.engine.get_raw_wpm()
        accuracy = self.engine.get_accuracy()
        errors = self.engine.error_count
        duration = self.engine.config.duration
        mode = f"{duration}s"
        language = self.engine.config.language
        characters = len(self.engine.typed_text)
        correct_characters = self.engine.get_correct_characters_count()
        incorrect_characters = errors
        consistency = self.engine.get_consistency()

        # 1. Update personal best in database
        from database.repositories.personal_best_repository import PersonalBestRepository
        pb_repo = PersonalBestRepository()
        is_pb = pb_repo.check_and_update_pb(user_id, mode, duration, wpm, accuracy)

        # 2. Calculate XP
        from gamification.xp_calculator import calculate_test_xp
        xp_earned = calculate_test_xp(duration, accuracy, is_pb)

        # 3. Save test result
        from database.repositories.test_repository import TestRepository
        test_repo = TestRepository()
        test_repo.save_test(
            user_id=user_id,
            mode=mode,
            duration=duration,
            language=language,
            wpm=wpm,
            raw_wpm=raw_wpm,
            accuracy=accuracy,
            characters=characters,
            correct_characters=correct_characters,
            incorrect_characters=incorrect_characters,
            xp_earned=xp_earned,
            is_pb=is_pb,
            consistency=consistency
        )

        # 4. Update daily statistics
        from database.repositories.daily_stats_repository import DailyStatsRepository
        daily_repo = DailyStatsRepository()
        daily_repo.update_daily_stats(user_id, datetime.now().strftime("%Y-%m-%d"))

        # 5. Update streak
        from services.streak_service import StreakService
        streak_service = StreakService()
        streak_data = streak_service.update_streak(user_id)
        current_streak = streak_data.get("current_streak", 0)
        longest_streak = streak_data.get("longest_streak", 0)

        # 6. Update user's aggregate XP and level in users table
        from gamification.levels import calculate_level
        with db.transaction() as conn:
            cursor = conn.execute("SELECT xp FROM users WHERE id = ?;", (user_id,))
            row = cursor.fetchone()
            current_xp = row["xp"] or 0
            
            new_xp = current_xp + xp_earned
            new_level = calculate_level(new_xp)
            
            conn.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?;", (new_xp, new_level, user_id))

        refresh_current_user()

        # 7. Publish results via EventBus
        self.controller.event_bus.publish(
            "test:completed",
            wpm=wpm,
            raw_wpm=raw_wpm,
            accuracy=accuracy,
            errors=errors,
            duration=duration,
            xp_earned=xp_earned,
            level=new_level,
            is_pb=is_pb,
            streak=current_streak,
            longest_streak=longest_streak,
            consistency=consistency
        )


        # 7.5 Record key attempts and errors for analytics
        char_attempts = {}
        typed_len = len(self.engine.typed_text)
        for i in range(typed_len):
            expected = self.engine.target_text[i].lower()
            if len(expected) == 1:
                char_attempts[expected] = char_attempts.get(expected, 0) + 1
        
        char_errors = getattr(self.engine, "character_errors", {})
        if char_attempts or char_errors:
            from database.repositories.key_stats_repository import KeyStatsRepository
            key_repo = KeyStatsRepository()
            key_repo.record_key_stats(user_id, char_attempts, char_errors)

        self.controller.show_view("results")

        # 8. Check and award achievements
        from services.achievements_service import AchievementsService
        ach_service = AchievementsService()
        new_achievements = ach_service.check_and_award_achievements(user_id)
        if new_achievements:
            from tkinter import messagebox
            for ach in new_achievements:
                messagebox.showinfo(
                    "Yangi Yutuq! 🎉",
                    f"Tabriklaymiz! Siz yangi yutuqqa erishdingiz:\n\n"
                    f"★ {ach['title']} ★\n"
                    f"Tavsif: {ach['description']}\n"
                    f"Mukofot: +{ach['xp_reward']} XP"
                )

        # 9. Update daily missions progress
        from services.daily_missions_service import DailyMissionsService
        missions_service = DailyMissionsService()
        today_str = datetime.now().strftime("%Y-%m-%d")
        newly_completed_missions = missions_service.update_mission_progress(
            user_id=user_id,
            date_str=today_str,
            wpm=wpm,
            accuracy=accuracy,
            duration=duration
        )
        if newly_completed_missions:
            from tkinter import messagebox
            for mission in newly_completed_missions:
                messagebox.showinfo(
                    "Kunlik Vazifa Bajarildi! 🏆",
                    f"Tabriklaymiz! Siz bugungi shaxsiy topshiriqni yakunladingiz:\n\n"
                    f"★ {mission['title']} ★\n"
                    f"Tavsif: {mission['description']}\n"
                    f"Mukofot: +{mission['xp_reward']} XP"
                )

    def _handle_back(self):
        """Action handler to exit back to dashboard."""
        self.cancel_timer()
        self.controller.show_view("home")

    def on_show(self):
        self.focus_set()
        
        # Default selectors to current user preferences if valid
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            setting = SettingsRepository().get_settings(user["id"])
            if setting:
                self.lang_var.set(setting.get("language", "English"))
        
        self.reset_test()
        
        # Bind keyboard events at window container level
        self.controller.root.bind("<Key>", self._on_key_press)
        self.bind("<Button-1>", lambda e: self.focus_set())

    def on_hide(self):
        self.controller.root.unbind("<Key>")
        self.cancel_timer()

    def apply_theme(self, theme_name: str):
        theme = THEMES.get(theme_name, THEMES["dark"])
        bg = theme["bg"]
        fg = theme["fg"]
        sec_fg = theme["secondary_fg"]
        accent = theme["accent"]

        # Text canvas config
        font_config = (self.controller.current_font_family, self.controller.current_font_size)
        self.text_widget.configure(bg=bg, insertbackground=accent, font=font_config)

        # Style tags mappings
        self.text_widget.tag_configure("untyped", foreground=sec_fg)
        self.text_widget.tag_configure("correct", foreground=fg)
        self.text_widget.tag_configure("incorrect", foreground="#ef4444", underline=True)
        self.text_widget.tag_configure("current", background=theme["select_bg"])
