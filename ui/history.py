"""
History display panel listing completed typing test records.
Provides a tabular interface for historical typing performance logs.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.base import BaseView
from database.repositories.test_repository import TestRepository
from services.auth_service import get_current_user

class HistoryView(BaseView):
    """
    Renders user's typing history records in a scrollable list view.
    Utilizes Treeview formatting and handles empty history queries gracefully.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.test_repo = TestRepository()
        self._setup_ui()

    def _setup_ui(self):
        # Base container
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Title spacer block
        self.title_label = ttk.Label(
            self.container,
            text="Mashqlar Tarixi",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))

        # Filter bar toolbar frame layout
        self.filter_bar = ttk.Frame(self.container)
        self.filter_bar.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(self.filter_bar, text="Kategoriya:").pack(side=tk.LEFT, padx=(0, 5))
        self.mode_combo = ttk.Combobox(
            self.filter_bar,
            values=("Barchasi", "words", "time", "quotes"),
            width=12,
            state="readonly"
        )
        self.mode_combo.set("Barchasi")
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(self.filter_bar, text="Qiyinchilik:").pack(side=tk.LEFT, padx=(0, 5))
        self.diff_combo = ttk.Combobox(
            self.filter_bar,
            values=("Barchasi", "normal", "expert", "master"),
            width=12,
            state="readonly"
        )
        self.diff_combo.set("Barchasi")
        self.diff_combo.pack(side=tk.LEFT, padx=(0, 15))

        self.pb_var = tk.BooleanVar(value=False)
        self.pb_check = ttk.Checkbutton(
            self.filter_bar,
            text="Faqat shaxsiy rekordlar",
            variable=self.pb_var
        )
        self.pb_check.pack(side=tk.LEFT, padx=(0, 5))

        # Event triggers back-binding
        self.mode_combo.bind("<<ComboboxSelected>>", lambda e: self.on_show())
        self.diff_combo.bind("<<ComboboxSelected>>", lambda e: self.on_show())
        self.pb_var.trace_add("write", lambda *args: self.on_show())

        # Main table container frame
        self.table_frame = ttk.Frame(self.container)

        # Empty state warning label
        self.empty_label = ttk.Label(
            self.table_frame,
            text="Tarixiy mashqlar topilmadi",
            font=("Helvetica", 12, "italic"),
            foreground="#646669"
        )

        # Scrollable Treeview setup
        columns = ("completed_at", "mode", "duration", "wpm", "accuracy", "xp_earned")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure headings
        self.tree.heading("completed_at", text="Sana/Vaqt")
        self.tree.heading("mode", text="Kategoriya")
        self.tree.heading("duration", text="Vaqt (soniya)")
        self.tree.heading("wpm", text="Tezlik (WPM)")
        self.tree.heading("accuracy", text="Aniqlik")
        self.tree.heading("xp_earned", text="XP")
        
        # Configure columns layout properties
        self.tree.column("completed_at", anchor="center", width=140)
        self.tree.column("mode", anchor="center", width=90)
        self.tree.column("duration", anchor="center", width=90)
        self.tree.column("wpm", anchor="center", width=100)
        self.tree.column("accuracy", anchor="center", width=90)
        self.tree.column("xp_earned", anchor="center", width=90)

        # Scrollbar binding
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Bottom navigation controls
        self.nav_bar = ttk.Frame(self.container)
        self.nav_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.back_btn = ttk.Button(
            self.nav_bar,
            text="Orqaga (Dashboard)",
            command=self._handle_back
        )
        self.back_btn.pack(side=tk.LEFT, ipady=5)

        # Pack table_frame at the end to occupy the remaining center space
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    def on_show(self):
        """Lifecycle hook reloading user test logs whenever view becomes active."""
        user = get_current_user()
        if not user:
            self._transition_empty_state(True)
            return

        # Fetch history records with active filters applied
        mode = self.mode_combo.get()
        diff = self.diff_combo.get()
        only_pb = self.pb_var.get()

        tests = self.test_repo.get_tests_by_user(
            user_id=user.get("id"),
            mode=mode,
            difficulty=diff,
            only_pb=only_pb
        )
        
        # Reset Treeview contents
        self.tree.delete(*self.tree.get_children())

        if not tests:
            self._transition_empty_state(True)
        else:
            self._transition_empty_state(False)
            for row in tests:
                # Format date string (YYYY-MM-DD HH:MM:SS -> YYYY-MM-DD HH:MM)
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
                        row.get("mode", ""),
                        f"{row.get('duration', 0)}s",
                        wpm_txt,
                        f"{accuracy_val:.1f}%",
                        f"+{xp_val} XP"
                    )
                )

    def _transition_empty_state(self, is_empty: bool):
        """Swaps display pack bindings between list scroll view and empty text label."""
        if is_empty:
            self.tree.pack_forget()
            self.scrollbar.pack_forget()
            self.empty_label.pack(expand=True, pady=40)
        else:
            self.empty_label.pack_forget()
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _handle_back(self):
        """Reroutes transition path back to the main dashboard screen view."""
        self.controller.show_view("home")
