"""
Settings view panel for TypeMaster application.
Provides system preferences configuration for visuals, audio, and databases.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import sqlite3
from ui.base import BaseView
from services.i18n_service import t, get_locale
from ui.theme import THEMES

class SettingsView(BaseView):
    """
    Dedicated view for configuring application parameters (theme, fonts, audio, and database backups).
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        
        self.theme_var = tk.StringVar(value="dark")
        self.font_var = tk.StringVar(value="Consolas")
        self.size_var = tk.StringVar(value="14")
        self.lang_var = tk.StringVar(value="O'zbekcha")
        
        self._setup_ui()

    def _setup_ui(self):
        # Outer container with padding
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header / Title Block
        self.title_label = ctk.CTkLabel(
            self.container,
            text=t("settings_title"),
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 20))
        
        # Card Layout containing three segmented boxes
        self.cards_scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.cards_scroll.pack(fill=tk.BOTH, expand=True)

        self._build_visual_card()
        self._build_audio_lang_card()
        self._build_data_card()
        
        # Save & Navigation Controls
        self.action_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.action_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        
        self.back_btn = ctk.CTkButton(
            self.action_frame,
            text=t("btn_back_to_dashboard") or "Orqaga",
            font=("Segoe UI", 12, "bold"),
            height=36,
            command=self._handle_back
        )
        self.back_btn.pack(side=tk.LEFT)
        
    def _build_visual_card(self):
        theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])
        
        self.visual_frame = ctk.CTkFrame(self.cards_scroll, fg_color=theme_colors["card_bg"], corner_radius=12)
        self.visual_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner = ctk.CTkFrame(self.visual_frame, fg_color="transparent")
        inner.pack(fill=tk.X, padx=15, pady=15)
        
        self.visual_title = ctk.CTkLabel(
            inner,
            text=t("settings_visual_section"),
            font=("Segoe UI", 14, "bold"),
            text_color=theme_colors["accent"]
        )
        self.visual_title.pack(anchor="w", pady=(0, 15))
        
        # Grid layout for settings keys
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill=tk.X)
        grid.columnconfigure(1, weight=1)
        
        # 1. Theme
        self.theme_lbl = ctk.CTkLabel(grid, text=t("theme"), font=("Segoe UI", 12))
        self.theme_lbl.grid(row=0, column=0, sticky="w", pady=6)
        self.theme_combo = ctk.CTkOptionMenu(
            grid,
            values=["dark", "light", "cyberpunk"],
            variable=self.theme_var,
            command=self._on_settings_change,
            font=("Segoe UI", 11)
        )
        self.theme_combo.grid(row=0, column=1, sticky="e", pady=6)
        
        # 2. Font family
        self.font_lbl = ctk.CTkLabel(grid, text=t("font"), font=("Segoe UI", 12))
        self.font_lbl.grid(row=1, column=0, sticky="w", pady=6)
        self.font_combo = ctk.CTkOptionMenu(
            grid,
            values=["Segoe UI", "Consolas", "Courier New", "Arial"],
            variable=self.font_var,
            command=self._on_settings_change,
            font=("Segoe UI", 11)
        )
        self.font_combo.grid(row=1, column=1, sticky="e", pady=6)
        
        # 3. Font Size
        self.size_lbl = ctk.CTkLabel(grid, text=t("size"), font=("Segoe UI", 12))
        self.size_lbl.grid(row=2, column=0, sticky="w", pady=6)
        self.size_combo = ctk.CTkOptionMenu(
            grid,
            values=["11", "12", "13", "14", "15", "16", "18"],
            variable=self.size_var,
            command=self._on_settings_change,
            font=("Segoe UI", 11)
        )
        self.size_combo.grid(row=2, column=1, sticky="e", pady=6)

        # 4. Keyboard Helper
        self.keyboard_lbl = ctk.CTkLabel(grid, text=t("settings_keyboard_helper") or "Keyboard Helper", font=("Segoe UI", 12))
        self.keyboard_lbl.grid(row=3, column=0, sticky="w", pady=6)
        self.keyboard_switch = ctk.CTkSwitch(
            grid,
            text="",
            command=self._on_keyboard_toggle,
            font=("Segoe UI", 11)
        )
        self.keyboard_switch.grid(row=3, column=1, sticky="e", pady=6)

    def _build_audio_lang_card(self):
        theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])
        
        self.audio_frame = ctk.CTkFrame(self.cards_scroll, fg_color=theme_colors["card_bg"], corner_radius=12)
        self.audio_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner = ctk.CTkFrame(self.audio_frame, fg_color="transparent")
        inner.pack(fill=tk.X, padx=15, pady=15)
        
        self.audio_title = ctk.CTkLabel(
            inner,
            text=t("settings_audio_section"),
            font=("Segoe UI", 14, "bold"),
            text_color=theme_colors["accent"]
        )
        self.audio_title.pack(anchor="w", pady=(0, 15))
        
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill=tk.X)
        grid.columnconfigure(1, weight=1)
        
        # 1. Language
        self.lang_lbl = ctk.CTkLabel(grid, text=t("language"), font=("Segoe UI", 12))
        self.lang_lbl.grid(row=0, column=0, sticky="w", pady=6)
        self.lang_combo = ctk.CTkOptionMenu(
            grid,
            values=["O'zbekcha", "English"],
            variable=self.lang_var,
            command=self._on_language_change,
            font=("Segoe UI", 11)
        )
        self.lang_combo.grid(row=0, column=1, sticky="e", pady=6)
        
        # 2. Sound Switch Toggle
        self.sound_lbl = ctk.CTkLabel(grid, text=t("sound") or "Ovozlar", font=("Segoe UI", 12))
        self.sound_lbl.grid(row=1, column=0, sticky="w", pady=6)
        self.sound_switch = ctk.CTkSwitch(
            grid,
            text="",
            command=self._on_sound_toggle,
            font=("Segoe UI", 11)
        )
        self.sound_switch.grid(row=1, column=1, sticky="e", pady=6)

    def _build_data_card(self):
        theme_colors = THEMES.get(self.controller.current_theme, THEMES["dark"])
        
        self.data_frame = ctk.CTkFrame(self.cards_scroll, fg_color=theme_colors["card_bg"], corner_radius=12)
        self.data_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner = ctk.CTkFrame(self.data_frame, fg_color="transparent")
        inner.pack(fill=tk.X, padx=15, pady=15)
        
        self.data_title = ctk.CTkLabel(
            inner,
            text=t("settings_data_section"),
            font=("Segoe UI", 14, "bold"),
            text_color=theme_colors["accent"]
        )
        self.data_title.pack(anchor="w", pady=(0, 15))
        
        # Backup panel block
        bk_block = ctk.CTkFrame(inner, fg_color="transparent")
        bk_block.pack(fill=tk.X, pady=4)
        bk_block.columnconfigure(0, weight=1)
        
        self.bk_lbl = ctk.CTkLabel(
            bk_block,
            text=t("settings_backup_desc"),
            font=("Segoe UI", 11),
            text_color=theme_colors["secondary_fg"],
            justify="left",
            wraplength=350
        )
        self.bk_lbl.grid(row=0, column=0, sticky="w", pady=4)
        
        self.bk_btn = ctk.CTkButton(
            bk_block,
            text=t("settings_btn_backup"),
            font=("Segoe UI", 11, "bold"),
            width=140,
            command=self._handle_backup
        )
        self.bk_btn.grid(row=0, column=1, sticky="e", padx=(10, 0), pady=4)
        
        # Restore panel block
        rst_block = ctk.CTkFrame(inner, fg_color="transparent")
        rst_block.pack(fill=tk.X, pady=4)
        rst_block.columnconfigure(0, weight=1)
        
        self.rst_lbl = ctk.CTkLabel(
            rst_block,
            text=t("settings_restore_desc"),
            font=("Segoe UI", 11),
            text_color=theme_colors["secondary_fg"],
            justify="left",
            wraplength=350
        )
        self.rst_lbl.grid(row=0, column=0, sticky="w", pady=4)
        
        self.rst_btn = ctk.CTkButton(
            rst_block,
            text=t("settings_btn_restore"),
            font=("Segoe UI", 11, "bold"),
            width=140,
            command=self._handle_restore
        )
        self.rst_btn.grid(row=0, column=1, sticky="e", padx=(10, 0), pady=4)

    def _on_settings_change(self, choice=None):
        theme_name = self.theme_var.get()
        font_family = self.font_var.get()
        try:
            font_size = int(self.size_var.get())
        except ValueError:
            font_size = 14
        self.controller.apply_theme(theme_name, font_family, font_size)

    def _on_sound_toggle(self):
        from services.sound_service import sound_player
        enabled = sound_player.toggle_sound()
        if enabled:
            sound_player.play_click()

    def _on_keyboard_toggle(self):
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            val = 1 if self.keyboard_switch.get() else 0
            from database.repositories.settings_repository import SettingsRepository
            SettingsRepository().update_setting(user["id"], "show_keyboard_helper", val)
            from services.sound_service import sound_player
            if sound_player._is_sound_enabled():
                sound_player.play_click()

    def _on_language_change(self, choice):
        from services.i18n_service import set_locale
        lang_code = "uz" if choice == "O'zbekcha" else "en"
        set_locale(lang_code)
        self.controller.current_ui_language = lang_code
        
        # Save preference in DB
        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            SettingsRepository().update_setting(user["id"], "ui_language", lang_code)
            
        self.controller.retranslate_ui()
        self.retranslate_ui()

    def _handle_back(self):
        self.controller.show_view("home")

    def _handle_backup(self):
        from tkinter import filedialog, messagebox
        from database.connection import db
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            initialfile="typemaster_backup.db",
            title=t("settings_btn_backup")
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
            messagebox.showinfo(
                "Export Backup" if get_locale() == "en" else "Zaxiralash",
                t("settings_saved_alert")
            )
        except Exception as err:
            messagebox.showerror("Error" if get_locale() == "en" else "Xatolik", str(err))

    def _handle_restore(self):
        from tkinter import filedialog, messagebox
        from database.connection import db
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            title=t("settings_btn_restore")
        )
        if not file_path:
            return

        confirm_msg = (
            "Restore data from this file? Custom settings and metrics will be overwritten!" 
            if get_locale() == "en" else 
            "Tizim ma'lumotlarini ushbu zaxira faylidan tiklamoqchimisiz? Joriy natijalar o'chib ketadi!"
        )
        if not messagebox.askyesno("Confirm" if get_locale() == "en" else "Tasdiqlash", confirm_msg):
            return

        try:
            # Check users table
            check_conn = sqlite3.connect(file_path)
            cursor = check_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            has_users = cursor.fetchone()
            check_conn.close()

            if not has_users:
                err_msg = "Selected file is not a valid TypeMaster backup database!" if get_locale() == "en" else "Tanlangan faylda users jadvali mavjud emas (noto'g'ri db)!"
                messagebox.showerror("Error", err_msg)
                return

            src_conn = sqlite3.connect(file_path)
            dst_conn = sqlite3.connect(str(db.database_path))
            with src_conn, dst_conn:
                src_conn.backup(dst_conn)
            src_conn.close()
            dst_conn.close()

            finished_msg = (
                "Data restored custom backup successfully! Restart app to apply all settings."
                if get_locale() == "en" else
                "Ma'lumotlar zaxiradan muvaffaqiyatli tiklandi!\nSozlamalarni joriy qilish uchun ilovani qayta ishga tushiring."
            )
            messagebox.showinfo("Restore" if get_locale() == "en" else "Tiklash", finished_msg)
        except Exception as err:
            messagebox.showerror("Error", str(err))

    def on_show(self):
        # Sync values on showing
        self.theme_var.set(self.controller.current_theme)
        self.font_var.set(self.controller.current_font_family)
        self.size_var.set(str(self.controller.current_font_size))
        
        lang_label = "O'zbekcha" if self.controller.current_ui_language == "uz" else "English"
        self.lang_var.set(lang_label)
        
        from services.sound_service import sound_player
        if sound_player._is_sound_enabled():
            self.sound_switch.select()
        else:
            self.sound_switch.deselect()

        from services.auth_service import get_current_user
        user = get_current_user()
        if user:
            from database.repositories.settings_repository import SettingsRepository
            setting = SettingsRepository().get_settings(user["id"])
            if setting and setting.get("show_keyboard_helper", 0):
                self.keyboard_switch.select()
            else:
                self.keyboard_switch.deselect()
        else:
            self.keyboard_switch.deselect()
            
        self.apply_theme(self.controller.current_theme)

    def apply_theme(self, theme_name: str):
        theme_colors = THEMES.get(theme_name, THEMES["dark"])
        fg = theme_colors["fg"]
        bg = theme_colors["bg"]
        card_bg = theme_colors["card_bg"]
        sec_fg = theme_colors["secondary_fg"]
        accent = theme_colors["accent"]
        border = theme_colors["border"]
        
        # Color updates
        if hasattr(self, "cards_scroll") and self.cards_scroll:
            self.cards_scroll.configure(fg_color=bg, bg_color=bg)
            
        self.title_label.configure(text_color=fg)
        
        card_panels = [self.visual_frame, self.audio_frame, self.data_frame]
        for f in card_panels:
            f.configure(fg_color=card_bg)
            
        lbl_list = [self.theme_lbl, self.font_lbl, self.size_lbl, self.lang_lbl, self.sound_lbl, self.keyboard_lbl]
        for l in lbl_list:
            l.configure(text_color=fg)
            
        sec_lbl_list = [self.bk_lbl, self.rst_lbl]
        for sl in sec_lbl_list:
            sl.configure(text_color=sec_fg)
            
        title_list = [self.visual_title, self.audio_title, self.data_title]
        for tl in title_list:
            tl.configure(text_color=accent)
            
        # Update dropdown styles
        menus = [self.theme_combo, self.font_combo, self.size_combo, self.lang_combo]
        for m in menus:
            m.configure(
                fg_color=theme_colors["bg"],
                text_color=fg,
                button_color=theme_colors["select_bg"],
                button_hover_color=accent
            )
            
        self.sound_switch.configure(
            text_color=fg,
            progress_color=accent,
            fg_color=border
        )

        self.keyboard_switch.configure(
            text_color=fg,
            progress_color=accent,
            fg_color=border
        )
        
        # Save & data action buttons
        self.back_btn.configure(
            fg_color=theme_colors["card_bg"],
            text_color=fg,
            hover_color=theme_colors["select_bg"]
        )
        
        self.bk_btn.configure(
            fg_color=accent,
            text_color=theme_colors["bg"],
            hover_color=theme_colors["select_bg"]
        )
        
        self.rst_btn.configure(
            fg_color="#ef4444" if theme_name == "light" else theme_colors["card_bg"],
            text_color="#ef4444" if theme_name != "light" else "#ffffff",
            hover_color="#dc2626"
        )

    def retranslate_ui(self):
        self.title_label.configure(text=t("settings_title"))
        self.visual_title.configure(text=t("settings_visual_section"))
        self.theme_lbl.configure(text=t("theme"))
        self.font_lbl.configure(text=t("font"))
        self.size_lbl.configure(text=t("size"))
        self.keyboard_lbl.configure(text=t("settings_keyboard_helper") or "Keyboard Helper")
        
        self.audio_title.configure(text=t("settings_audio_section"))
        self.lang_lbl.configure(text=t("language"))
        self.sound_lbl.configure(text=t("sound") or "Ovozlar")
        
        self.data_title.configure(text=t("settings_data_section"))
        self.bk_lbl.configure(text=t("settings_backup_desc"))
        self.bk_btn.configure(text=t("settings_btn_backup"))
        self.rst_lbl.configure(text=t("settings_restore_desc"))
        self.rst_btn.configure(text=t("settings_btn_restore"))
        
        self.back_btn.configure(text=t("btn_back_to_dashboard") or "Orqaga")
