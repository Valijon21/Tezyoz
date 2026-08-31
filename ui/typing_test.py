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

        self.lang_name_lbl = ttk.Label(self.config_frame, text="Til:")
        self.lang_name_lbl.pack(side=tk.LEFT, padx=(5, 3))
        self.lang_combo = ttk.Combobox(
            self.config_frame,
            textvariable=self.lang_var,
            values=["English", "Russian", "Uzbek"],
            width=10,
            state="readonly"
        )
        self.lang_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_config_change)

        self.time_name_lbl = ttk.Label(self.config_frame, text="Vaqt:")
        self.time_name_lbl.pack(side=tk.LEFT, padx=(5, 3))
        self.dur_combo = ttk.Combobox(
            self.config_frame,
            textvariable=self.dur_var,
            values=["15", "30", "60", "120"],
            width=6,
            state="normal"
        )
        self.dur_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.dur_combo.bind("<<ComboboxSelected>>", self._on_config_change)
        self.dur_combo.bind("<Return>", self._on_config_change)
        self.dur_combo.bind("<FocusOut>", self._on_config_change)

        # Custom file upload button (styled to match theme)
        import customtkinter as ctk
        self.upload_btn = ctk.CTkButton(
            self.config_frame,
            text="Fayl yuklash 📁",
            width=100,
            height=28,
            font=("Segoe UI", 11, "bold"),
            command=self._handle_file_upload
        )
        self.upload_btn.pack(side=tk.LEFT, padx=(15, 0))

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

        from ui.keyboard_visualizer import KeyboardVisualizer
        self.keyboard_visualizer = KeyboardVisualizer(self.container, self.controller)

        # Pack canvas frame at the end to occupy the remaining center space
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

    def _on_config_change(self, event=None):
        # Validate typed duration if normal state
        import re
        val_str = self.dur_var.get().strip()
        val_str = re.sub(r"[^\d]", "", val_str)
        if not val_str:
            val_str = "60"
        
        # update current select values
        defaults = {15, 30, 60, 120}
        try:
            val = int(val_str)
            if val > 0:
                defaults.add(val)
        except ValueError:
            pass
        sorted_vals = [str(x) for x in sorted(list(defaults))]
        self.dur_combo.configure(values=sorted_vals)
        
        self.dur_var.set(val_str)
        
        # Called when language or duration is changed.
        language = self.lang_var.get()
        # If the user switched to a standard language, clear custom settings
        if not (language.startswith("Fayl:") or language.startswith("File:")):
            self.custom_file_text = None
            self.custom_file_name = None
            
        # Also save this changed duration back to settings if user logged in
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            try:
                dur_int = int(val_str)
                if dur_int > 0:
                    from database.repositories.settings_repository import SettingsRepository
                    SettingsRepository().update_setting(user["id"], "custom_duration", dur_int)
            except ValueError:
                pass
                
        self.reset_test()
        self.text_widget.focus_force()

    def _handle_file_upload(self):
        """Opens file dialog, extracts first 200 words, and resets active engine."""
        from tkinter import filedialog, messagebox
        import os
        
        file_path = filedialog.askopenfilename(
            title="Matn faylini tanlang",
            filetypes=[("Hujjatlar", "*.txt *.docx *.md")]
        )
        if not file_path:
            return
            
        try:
            from services.file_parser import extract_typing_text
            self.custom_file_text = extract_typing_text(file_path, max_words=200)
            self.custom_file_name = os.path.basename(file_path)
            
            # Update display state
            self.lang_var.set(f"Fayl: {self.custom_file_name}")
            self.reset_test()
            
            messagebox.showinfo(
                "Muvaffaqiyatli",
                f"Foydalanuvchi fayli muvaffaqiyatli yuklandi!\nFayl nomi: {self.custom_file_name}"
            )
        except Exception as err:
            messagebox.showerror("Xatolik", str(err))

    def reset_test(self):
        """Cancels current timer and builds a fresh TypingEngine instance."""
        self.cancel_timer()
        
        # Read parameters
        language = self.lang_var.get()
        try:
            duration = int(self.dur_var.get())
        except ValueError:
            duration = 60

        custom_text = None
        if hasattr(self, "custom_file_text") and self.custom_file_text:
            custom_text = self.custom_file_text

        config = TestConfig(language, duration)
        self.engine = TypingEngine(config, custom_text=custom_text)
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
        from services.i18n_service import t
        self.time_lbl.config(text=f"{t('practice_time')} {duration}s")
        self.wpm_lbl.config(text=f"{t('practice_speed')} 0.0 WPM")
        self.acc_lbl.config(text=f"{t('practice_accuracy')} 0.0%")
        self.info_lbl.config(text=f"{t('practice_start_instruction')} ({t('practice_restart_kbd')})", foreground="")

        # Check show_keyboard_helper setting and pack visualizer accordingly
        show_kb = False
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            setting = SettingsRepository().get_settings(user["id"])
            if setting and setting.get("show_keyboard_helper", 0):
                show_kb = True
        
        if show_kb:
            self.keyboard_visualizer.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 5))
            self.keyboard_visualizer.set_practice_language(self.lang_var.get())
            if self.engine and len(self.engine.target_text) > 0:
                self.keyboard_visualizer.highlight_key(self.engine.target_text[0])
            else:
                self.keyboard_visualizer.highlight_key(None)
        else:
            self.keyboard_visualizer.pack_forget()

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

        from services.sound_service import sound_player
        if action == "backspace":
            self.engine.backspace()
            sound_player.play_click()
            if hasattr(self, "keyboard_visualizer") and self.keyboard_visualizer:
                self.keyboard_visualizer.visualize_press("BACKSPACE")
        elif action == "input" and val is not None:
            # Check typing accuracy before sending to engine for audio cue selection
            typed_len = len(self.engine.typed_text)
            if typed_len < len(self.engine.target_text):
                expected_char = self.engine.target_text[typed_len]
                if val == expected_char:
                    sound_player.play_click()
                else:
                    sound_player.play_error()
            self.engine.input_character(val)
            if hasattr(self, "keyboard_visualizer") and self.keyboard_visualizer:
                self.keyboard_visualizer.visualize_press(val)

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
            self.keyboard_visualizer.highlight_key(engine.target_text[typed_len])
        else:
            self.keyboard_visualizer.highlight_key(None)

        self.text_widget.config(state="disabled")

        # Metrics updates
        from services.i18n_service import t
        self.wpm_lbl.config(text=f"{t('practice_speed')} {engine.get_wpm():.1f} WPM")
        self.acc_lbl.config(text=f"{t('practice_accuracy')} {engine.get_accuracy():.1f}%")

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
        rem_sec = int(self.engine.get_remaining_time() + 0.5)
        from services.i18n_service import t
        self.time_lbl.config(text=f"{t('practice_time')} {rem_sec}s")

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
        language = self.engine.config.language
        if language.startswith("Fayl:") or language.startswith("File:"):
            mode = "file"
        else:
            mode = f"{duration}s"
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
            cursor = conn.execute("SELECT xp, level FROM users WHERE id = ?;", (user_id,))
            row = cursor.fetchone()
            current_xp = row["xp"] or 0
            old_level = row["level"] or 1
            
            new_xp = current_xp + xp_earned
            new_level = calculate_level(new_xp)
            
            conn.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?;", (new_xp, new_level, user_id))

        if new_level > old_level:
            from services.sound_service import sound_player
            sound_player.play_level_up()

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
            consistency=consistency,
            total_chars=len(self.engine.typed_text)
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
            from services.i18n_service import t
            for ach in new_achievements:
                ach_key = ach.get("key", "")
                title_text = t(f"ach_{ach_key}_title", ach.get("title", ""))
                desc_text = t(f"ach_{ach_key}_desc", ach.get("description", ""))
                messagebox.showinfo(
                    t("ach_popup_title"),
                    t("ach_popup_body").format(title_text, desc_text, ach['xp_reward'])
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
            from services.i18n_service import t
            for mission in newly_completed_missions:
                m_key = mission.get("mission_key", "")
                title_text = t(f"mission_{m_key}_title", mission.get("title", ""))
                desc_text = t(f"mission_{m_key}_desc", mission.get("description", ""))
                messagebox.showinfo(
                    t("mission_popup_title"),
                    t("mission_popup_body").format(title_text, desc_text, mission['xp_reward'])
                )

    def _handle_back(self):
        """Action handler to exit back to dashboard."""
        self.cancel_timer()
        self.controller.show_view("home")

    def _bind_clicks_recursively(self, widget):
        w_class = widget.winfo_class() if hasattr(widget, "winfo_class") else ""
        if "Combobox" not in w_class and "Entry" not in w_class and "Button" not in w_class:
            widget.bind("<Button-1>", lambda e: self.text_widget.focus_force(), add="+")
        for child in widget.winfo_children():
            self._bind_clicks_recursively(child)

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
                custom_dur = setting.get("custom_duration", 60)
                defaults = {15, 30, 60, 120}
                try:
                    val = int(custom_dur)
                    if val > 0:
                        defaults.add(val)
                except ValueError:
                    pass
                sorted_vals = [str(x) for x in sorted(list(defaults))]
                self.dur_combo.configure(values=sorted_vals)
                self.dur_var.set(str(custom_dur))
        
        self.reset_test()
        
        # Bind keyboard events directly to the Text widget
        self.text_widget.bind("<Key>", self._on_key_press)
        
        # Recursively bind click handlers to redirect focus to text_widget
        self._bind_clicks_recursively(self)
        
        # Natively grab keyboard focus with multiple deferred attempts after view is mapped
        def grab_focus():
            self.text_widget.focus_force()
            
        grab_focus()
        self.after(50, grab_focus)
        self.after(150, grab_focus)

    def on_hide(self):
        self.text_widget.unbind("<Key>")
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
        self.text_widget.tag_configure("current", background="#00ffff", foreground="#000000")

        if hasattr(self, "keyboard_visualizer") and self.keyboard_visualizer:
            self.keyboard_visualizer.apply_theme(theme_name)

        if hasattr(self, "upload_btn") and self.upload_btn:
            try:
                self.upload_btn.configure(
                    fg_color=theme["card_bg"],
                    text_color=theme["accent"],
                    hover_color=theme["select_bg"]
                )
            except Exception:
                pass

    def retranslate_ui(self):
        """Translates all text elements to the current active locale."""
        from services.i18n_service import t, get_locale
        # Title
        self.title_label.configure(text=t("practice_title"))
        
        # Selectors labels
        if hasattr(self, "lang_name_lbl") and self.lang_name_lbl:
            self.lang_name_lbl.configure(text=t("practice_lang"))
        if hasattr(self, "time_name_lbl") and self.time_name_lbl:
            self.time_name_lbl.configure(text=t("practice_time"))
            
        # Upload Button
        if hasattr(self, "upload_btn") and self.upload_btn:
            self.upload_btn.configure(text="Fayl yuklash 📁" if get_locale() == "uz" else "File Upload 📁")
            
        # Canvas Frame Label
        if hasattr(self, "canvas_frame") and self.canvas_frame:
            self.canvas_frame.configure(text=" Yozish maydoni " if get_locale() == "uz" else " Typing Area ")
            
        # Restart & Back Buttons
        if hasattr(self, "restart_btn") and self.restart_btn:
            self.restart_btn.configure(text=t("btn_restart"))
        if hasattr(self, "back_btn") and self.back_btn:
            self.back_btn.configure(text=t("btn_back_to_dashboard"))
            
        # Info Label (Yozishni boshlang...)
        if hasattr(self, "info_lbl") and self.info_lbl:
            self.info_lbl.configure(text=f"{t('practice_start_instruction')} ({t('practice_restart_kbd')})")
