"""
History display panel listing completed typing test records.
Features a modern split-pane CustomTkinter interface with WPM/Accuracy line charts.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import customtkinter as ctk
from ui.base import BaseView
from database.repositories.test_repository import TestRepository
from services.auth_service import get_current_user
from ui.theme import THEMES
from charts.line_chart import LineChart, AccuracyChart

class HistoryView(BaseView):
    """
    Renders user's typing history records in a split layout with table and line charts.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.test_repo = TestRepository()
        self.active_chart_key = "wpm" # default to wpm chart
        self.current_page = 0
        self.page_size = 10
        self._setup_ui()

    def _setup_ui(self):
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Base container pad
        self.container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title block
        self.title_label = ctk.CTkLabel(
            self.container,
            text="Mashqlar Tarixi",
            font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))

        # Filter bar toolbar frame layout
        self.filter_bar = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.filter_bar.pack(fill=tk.X, pady=(0, 15))

        # Category Combobox
        self.category_lbl = ctk.CTkLabel(self.filter_bar, text="Kategoriya:", font=("Segoe UI", 11, "bold"))
        self.category_lbl.pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo = ctk.CTkComboBox(
            self.filter_bar,
            values=["Barchasi", "words", "time", "quotes", "file"],
            width=100,
            state="readonly"
        )
        self.mode_combo.set("Barchasi")
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Difficulty Combobox
        self.difficulty_lbl = ctk.CTkLabel(self.filter_bar, text="Qiyinchilik:", font=("Segoe UI", 11, "bold"))
        self.difficulty_lbl.pack(side=tk.LEFT, padx=(0, 5))
        self.diff_combo = ctk.CTkComboBox(
            self.filter_bar,
            values=["Barchasi", "normal", "expert", "master"],
            width=100,
            state="readonly"
        )
        self.diff_combo.set("Barchasi")
        self.diff_combo.pack(side=tk.LEFT, padx=(0, 15))

        # FAqat PB checkbox
        self.pb_var = tk.BooleanVar(value=False)
        self.pb_check = ctk.CTkCheckBox(
            self.filter_bar,
            text="Faqat shaxsiy rekordlar",
            variable=self.pb_var,
            font=("Segoe UI", 11, "bold")
        )
        self.pb_check.pack(side=tk.LEFT, padx=(0, 5))

        # Event triggers back-binding (bind standard Tkinter ComboboxSelected event + CustomTkinter command)
        self.mode_combo.configure(command=lambda e: self.on_show())
        self.diff_combo.configure(command=lambda e: self.on_show())
        self.pb_var.trace_add("write", lambda *args: self.on_show())

        # Monkey-patch event_generate of CTkComboBox to support test-triggered "<<ComboboxSelected>>" sequence
        def patch_combobox_event(combo):
            original_event_generate = combo.event_generate
            def custom_event_generate(sequence, **kwargs):
                if sequence == "<<ComboboxSelected>>":
                    self.on_show()
                return original_event_generate(sequence, **kwargs)
            combo.event_generate = custom_event_generate

        patch_combobox_event(self.mode_combo)
        patch_combobox_event(self.diff_combo)

        # Bottom navigation controls (packed first to slice bottom space before layout split)
        self.nav_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        self.nav_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))

        self.back_btn = ctk.CTkButton(
            self.nav_bar,
            text="Orqaga (Dashboard)",
            font=("Segoe UI", 12, "bold"),
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"],
            command=self._handle_back
        )
        self.back_btn.pack(side=tk.LEFT, ipady=4)

        # Pagination Controls
        self.page_controls = ctk.CTkFrame(self.nav_bar, fg_color="transparent")
        self.page_controls.pack(side=tk.RIGHT)

        self.prev_btn = ctk.CTkButton(
            self.page_controls,
            text="< Oldingi",
            width=80,
            font=("Segoe UI", 12, "bold"),
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"],
            command=self._prev_page
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.page_lbl = ctk.CTkLabel(
            self.page_controls,
            text="Sahifa 1 / 1",
            font=("Segoe UI", 12, "bold"),
            text_color=theme_colors["fg"]
        )
        self.page_lbl.pack(side=tk.LEFT, padx=10)

        self.next_btn = ctk.CTkButton(
            self.page_controls,
            text="Keyingi >",
            width=80,
            font=("Segoe UI", 12, "bold"),
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"],
            command=self._next_page
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Left Panel (Table) - direct container child
        self.table_frame = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right Panel (Chart Container) - direct container child
        self.chart_panel = ctk.CTkFrame(
            self.container, 
            fg_color=theme_colors["card_bg"], 
            corner_radius=12,
            width=380
        )
        self.chart_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        self.chart_panel.pack_propagate(False)

        # Toggle Button Header for Charts
        self.chart_header = ctk.CTkFrame(self.chart_panel, fg_color="transparent", corner_radius=0)
        self.chart_header.pack(fill=tk.X, padx=15, pady=(15, 5))

        # Metric Select buttons
        self.toggle_buttons = {}
        chart_modes = [("wpm", "Tezlik (WPM)"), ("accuracy", "Aniqlik (%)")]
        for key, text in chart_modes:
            btn = ctk.CTkButton(
                self.chart_header,
                text=text,
                font=("Segoe UI", 11, "bold"),
                width=100,
                height=28,
                corner_radius=6,
                fg_color=theme_colors["card_bg"],
                text_color=theme_colors["fg"],
                hover_color=theme_colors["select_bg"],
                command=lambda k=key: self._set_chart_type(k)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.toggle_buttons[key] = btn

        # Main chart view frames
        self.wpm_chart = LineChart(self.chart_panel)
        self.wpm_chart.y_key = "wpm"
        self.wpm_chart.y_format = "integer"
        self.wpm_chart.x_key = "date"

        self.acc_chart = AccuracyChart(self.chart_panel)
        self.acc_chart.y_key = "accuracy"
        self.acc_chart.y_format = "integer"
        self.acc_chart.x_key = "date"

        # Pack default chart WPM
        self.wpm_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Empty state warning label
        self.empty_label = ctk.CTkLabel(
            self.table_frame,
            text="Tarixiy mashqlar topilmadi",
            font=("Segoe UI", 13, "italic"),
            text_color=theme_colors["secondary_fg"]
        )

        # Scrollable Treeview setup
        columns = ("completed_at", "mode", "duration", "wpm", "accuracy", "xp_earned")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure headings
        self.tree.heading("completed_at", text="Sana/Vaqt", anchor="center")
        self.tree.heading("mode", text="Kategoriya", anchor="center")
        self.tree.heading("duration", text="Vaqt", anchor="center")
        self.tree.heading("wpm", text="Tezlik (WPM)", anchor="center")
        self.tree.heading("accuracy", text="Aniqlik", anchor="center")
        self.tree.heading("xp_earned", text="XP", anchor="center")
        
        # Configure columns layout properties
        self.tree.column("completed_at", anchor="center", width=120)
        self.tree.column("mode", anchor="center", width=80)
        self.tree.column("duration", anchor="center", width=70)
        self.tree.column("wpm", anchor="e", width=95)
        self.tree.column("accuracy", anchor="e", width=85)
        self.tree.column("xp_earned", anchor="center", width=75)

        # Scrollbar binding
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def on_show(self):
        """Lifecycle hook resetting page position and loading records."""
        self.current_page = 0
        self._update_list()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_list()

    def _next_page(self):
        self.current_page += 1
        self._update_list()

    def _update_list(self):
        """Fetches history records and updates chart & paginated Treeview dynamically."""
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Update frame styling parameters
        self.chart_panel.configure(fg_color=theme_colors["card_bg"])
        self.back_btn.configure(
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"]
        )

        user = get_current_user()
        if not user:
            self._transition_empty_state(True)
            self.wpm_chart.clear()
            self.acc_chart.clear()
            return

        # Configure dynamic charts theme colours
        self.wpm_chart.apply_theme_colors(
            bg_color=theme_colors["card_bg"],
            line_color=theme_colors["accent"],
            grid_color=theme_colors["border"],
            text_color=theme_colors["secondary_fg"]
        )
        self.acc_chart.apply_theme_colors(
            bg_color=theme_colors["card_bg"],
            line_color="#10b981", # emerald Green
            grid_color=theme_colors["border"],
            text_color=theme_colors["secondary_fg"]
        )

        # Fetch history records with active filters applied
        from services.i18n_service import t
        mode = self.mode_combo.get()
        diff = self.diff_combo.get()
        only_pb = self.pb_var.get()

        passed_mode = self._get_db_mode(mode)
        passed_diff = self._get_db_diff(diff)

        tests = self.test_repo.get_tests_by_user(
            user_id=user.get("id"),
            mode=passed_mode,
            difficulty=passed_diff,
            only_pb=only_pb
        )
        
        # Reset Treeview contents
        self.tree.delete(*self.tree.get_children())

        # Update button highlights
        for key, btn in self.toggle_buttons.items():
            if key == self.active_chart_key:
                btn.configure(fg_color=theme_colors["select_bg"])
            else:
                btn.configure(fg_color=theme_colors["card_bg"])

        if not tests:
            self._transition_empty_state(True)
            self.wpm_chart.clear()
            self.acc_chart.clear()
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
            self.page_lbl.configure(text=f"{t('page')} 1 / 1")
        else:
            self._transition_empty_state(False)
            
            # Pagination borders
            total_pages = max(1, (len(tests) + self.page_size - 1) // self.page_size)
            if self.current_page >= total_pages:
                self.current_page = total_pages - 1
            if self.current_page < 0:
                self.current_page = 0

            self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_btn.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
            self.page_lbl.configure(text=f"{t('page')} {self.current_page + 1} / {total_pages}")
            
            # Slice current page to show in Treeview
            start_idx = self.current_page * self.page_size
            end_idx = start_idx + self.page_size
            page_list = tests[start_idx:end_idx]

            # Populate Treeview
            for row in page_list:
                # Format date string
                date_str = row.get("completed_at", "")
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
                
                # Highlight Personal Bests with Gold Star prefix symbol
                wpm_val = row.get("wpm", 0.0)
                wpm_txt = f"{wpm_val:.1f}"
                if row.get("is_personal_best"):
                    wpm_txt = f"★ {wpm_txt}"
                    
                accuracy_val = row.get("accuracy", 0.0)
                xp_val = row.get("xp_earned", 0)
                
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        date_str,
                        self._get_display_mode(row.get("mode", "")),
                        f"{row.get('duration', 0)}s",
                        wpm_txt,
                        f"{accuracy_val:.1f}%",
                        f"+{xp_val} XP"
                    )
                )

            # Map chronological stats datasets (newest returns first, so we reverse it!)
            reversed_tests = list(reversed(tests))
            chart_data = []
            for r in reversed_tests:
                # Truncate date to simple YYYY-MM-DD
                timestamp = r.get("completed_at", "")[:10]
                chart_data.append({
                    "date": timestamp,
                    "wpm": r.get("wpm", 0.0),
                    "accuracy": r.get("accuracy", 0.0)
                })

            # Feed datasets into both LineChart and AccuracyChart (shows full directory history progress!)
            self.wpm_chart.set_data(chart_data, x_key="date", y_key="wpm")
            self.acc_chart.set_data(chart_data, x_key="date", y_key="accuracy")

    def _set_chart_type(self, chart_key: str):
        """Swaps chart widgets active on history screen."""
        self.active_chart_key = chart_key
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        for key, btn in self.toggle_buttons.items():
            if key == chart_key:
                btn.configure(fg_color=theme_colors["select_bg"])
            else:
                btn.configure(fg_color=theme_colors["card_bg"])

        # Unpack both first, then repack selected one
        self.wpm_chart.pack_forget()
        self.acc_chart.pack_forget()

        if chart_key == "wpm":
            self.wpm_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        else:
            self.acc_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _transition_empty_state(self, is_empty: bool):
        """Swaps display pack bindings between split panels and empty text."""
        if is_empty:
            self.tree.pack_forget()
            self.scrollbar.pack_forget()
            self.chart_panel.pack_forget()
            self.empty_label.pack(expand=True, pady=40)
        else:
            self.empty_label.pack_forget()
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.chart_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

    def _handle_back(self):
        """Reroutes transition path back to the main dashboard screen view."""
        self.controller.show_view("home")

    def apply_theme(self, theme_name: str):
        """Re-applies colors when active theme is toggled."""
        from ui.theme import THEMES
        theme = THEMES.get(theme_name, THEMES["dark"])
        
        if hasattr(self, "title_label") and self.title_label:
            self.title_label.configure(text_color=theme["fg"])
        if hasattr(self, "category_lbl") and self.category_lbl:
            self.category_lbl.configure(text_color=theme["fg"])
        if hasattr(self, "difficulty_lbl") and self.difficulty_lbl:
            self.difficulty_lbl.configure(text_color=theme["fg"])
        if hasattr(self, "page_lbl") and self.page_lbl:
            self.page_lbl.configure(text_color=theme["fg"])
        if hasattr(self, "pb_check") and self.pb_check:
            self.pb_check.configure(text_color=theme["fg"])
        if hasattr(self, "empty_label") and self.empty_label:
            self.empty_label.configure(text_color=theme["secondary_fg"])
            
        for combo_name in ("mode_combo", "diff_combo"):
            combo = getattr(self, combo_name, None)
            if combo:
                try:
                    combo.configure(
                        fg_color=theme["entry_bg"],
                        text_color=theme["entry_fg"],
                        button_color=theme["select_bg"],
                        button_hover_color=theme["accent"],
                        border_color=theme["border"]
                    )
                except Exception:
                    pass

        if hasattr(self, "chart_panel") and self.chart_panel:
            self.chart_panel.configure(fg_color=theme["card_bg"])
            
        for btn_name in ("back_btn", "prev_btn", "next_btn"):
            btn = getattr(self, btn_name, None)
            if btn:
                try:
                    btn.configure(
                        fg_color=theme["card_bg"],
                        text_color=theme["fg"],
                        hover_color=theme["select_bg"]
                    )
                except Exception:
                    pass

        for btn in self.toggle_buttons.values():
            if btn:
                try:
                    btn.configure(
                        fg_color=theme["card_bg"],
                        text_color=theme["fg"],
                        hover_color=theme["select_bg"]
                    )
                except Exception:
                    pass
        
        # Configure dynamic charts theme colours
        if hasattr(self, "wpm_chart") and self.wpm_chart:
            self.wpm_chart.apply_theme_colors(
                bg_color=theme["card_bg"],
                line_color=theme["accent"],
                grid_color=theme["border"],
                text_color=theme["secondary_fg"]
            )
        if hasattr(self, "acc_chart") and self.acc_chart:
            self.acc_chart.apply_theme_colors(
                bg_color=theme["card_bg"],
                line_color="#10b981", # emerald Green
                grid_color=theme["border"],
                text_color=theme["secondary_fg"]
            )

        self._update_list()

    def retranslate_ui(self):
        """Dynamic text configuration mapping for history view filter menus and tables."""
        from services.i18n_service import t
        # Page Title
        self.title_label.configure(text=t("history_title"))
        
        # Filters Labels
        if hasattr(self, "category_lbl") and self.category_lbl:
            self.category_lbl.configure(text=t("history_filter_category"))
        if hasattr(self, "difficulty_lbl") and self.difficulty_lbl:
            self.difficulty_lbl.configure(text=t("history_filter_difficulty"))
        if hasattr(self, "pb_check") and self.pb_check:
            self.pb_check.configure(text=t("history_filter_pb_only"))
            
        # Combobox options translation
        mode_val = self.mode_combo.get()
        diff_val = self.diff_combo.get()
        
        # Get previous DB value before translating
        db_mode = self._get_db_mode(mode_val)
        db_diff = self._get_db_diff(diff_val)
        
        self.mode_combo.configure(values=[t("history_all"), t("mode_words"), t("mode_time"), t("mode_quotes"), t("mode_file")])
        self.diff_combo.configure(values=[t("history_all"), t("diff_normal"), t("diff_expert"), t("diff_master")])
        
        # Set selection to new translated text
        self.mode_combo.set(self._get_display_mode(db_mode))
        self.diff_combo.set(self._get_display_diff(db_diff))
            
        # Action Buttons
        if hasattr(self, "back_btn") and self.back_btn:
            self.back_btn.configure(text=t("btn_back_to_dashboard"))
        if hasattr(self, "prev_btn") and self.prev_btn:
            self.prev_btn.configure(text="< " + t("btn_prev"))
        if hasattr(self, "next_btn") and self.next_btn:
            self.next_btn.configure(text=t("btn_next") + " >")
            
        # Chart Switches
        chart_names = {"wpm": "graph_wpm", "accuracy": "graph_accuracy"}
        for k, v in chart_names.items():
            if k in self.toggle_buttons:
                self.toggle_buttons[k].configure(text=t(v))
                
        # Empty Warning
        if hasattr(self, "empty_label") and self.empty_label:
            self.empty_label.configure(text=t("history_empty"))
            
        # Table Columns Headers
        self.tree.heading("completed_at", text=t("history_date"), anchor="center")
        self.tree.heading("mode", text=t("history_category"), anchor="center")
        self.tree.heading("duration", text=t("history_duration"), anchor="center")
        self.tree.heading("wpm", text=t("history_speed"), anchor="center")
        self.tree.heading("accuracy", text=t("history_accuracy"), anchor="center")
        self.tree.heading("xp_earned", text=t("history_xp"), anchor="center")
        
        if self.winfo_ismapped():
            self._update_list()

    def _get_db_mode(self, display_val: str) -> str:
        from services.i18n_service import t
        # Maps display text back to DB keys
        # We check both Uzbek/English/raw strings to be bulletproof
        maps = {
            t("history_all"): "Barchasi",
            t("mode_words"): "words",
            t("mode_time"): "time",
            t("mode_quotes"): "quotes",
            t("mode_file"): "file",
            "Barchasi": "Barchasi",
            "All": "Barchasi",
            "words": "words",
            "time": "time",
            "quotes": "quotes",
            "file": "file"
        }
        return maps.get(display_val, "Barchasi")

    def _get_display_mode(self, db_val: str) -> str:
        from services.i18n_service import t
        maps = {
            "Barchasi": t("history_all"),
            "words": t("mode_words"),
            "time": t("mode_time"),
            "quotes": t("mode_quotes"),
            "file": t("mode_file")
        }
        return maps.get(db_val, t("history_all"))

    def _get_db_diff(self, display_val: str) -> str:
        from services.i18n_service import t
        maps = {
            t("history_all"): "Barchasi",
            t("diff_normal"): "normal",
            t("diff_expert"): "expert",
            t("diff_master"): "master",
            "Barchasi": "Barchasi",
            "All": "Barchasi",
            "normal": "normal",
            "expert": "expert",
            "master": "master"
        }
        return maps.get(display_val, "Barchasi")

    def _get_display_diff(self, db_val: str) -> str:
        from services.i18n_service import t
        maps = {
            "Barchasi": t("history_all"),
            "normal": t("diff_normal"),
            "expert": t("diff_expert"),
            "master": t("diff_master")
        }
        return maps.get(db_val, t("history_all"))

