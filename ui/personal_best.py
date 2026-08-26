"""
Personal Bests display panel listing user's record typing test runs.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.base import BaseView
from database.repositories.personal_best_repository import PersonalBestRepository
from services.auth_service import get_current_user

class PersonalBestView(BaseView):
    """
    Renders user's personal best records in a scrollable list view.
    Utilizes Treeview formatting and handles empty history queries gracefully.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.pb_repo = PersonalBestRepository()
        self._setup_ui()

    def _setup_ui(self):
        # Base container
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Title block
        self.title_label = ttk.Label(
            self.container,
            text="Shaxsiy Rekordlar (Personal Bests)",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 15))

        # Main table container frame
        self.table_frame = ttk.Frame(self.container)

        # Empty state warning label
        self.empty_label = ttk.Label(
            self.table_frame,
            text="Shaxsiy rekordlar topilmadi",
            font=("Helvetica", 12, "italic"),
            foreground="#646669"
        )

        # Scrollable Treeview setup
        columns = ("mode", "duration", "best_wpm", "best_accuracy", "achieved_at")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure headings
        self.tree.heading("mode", text="Kategoriya")
        self.tree.heading("duration", text="Vaqt")
        self.tree.heading("best_wpm", text="Tezlik (WPM)")
        self.tree.heading("best_accuracy", text="Aniqlik")
        self.tree.heading("achieved_at", text="Erishilgan sana")
        
        # Configure columns layout properties
        self.tree.column("mode", anchor="center", width=120)
        self.tree.column("duration", anchor="center", width=100)
        self.tree.column("best_wpm", anchor="center", width=130)
        self.tree.column("best_accuracy", anchor="center", width=110)
        self.tree.column("achieved_at", anchor="center", width=160)

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
        """Lifecycle hook reloading user PB list whenever view becomes active."""
        user = get_current_user()
        if not user:
            self._transition_empty_state(True)
            return

        # Fetch records
        pb_list = self.pb_repo.get_all_personal_bests(user.get("id"))
        
        # Reset Treeview contents
        self.tree.delete(*self.tree.get_children())

        if not pb_list:
            self._transition_empty_state(True)
        else:
            self._transition_empty_state(False)
            for row in pb_list:
                # Format date string (YYYY-MM-DD HH:MM:SS -> YYYY-MM-DD HH:MM)
                date_str = row.get("achieved_at", "")
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    date_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
                
                wpm_val = row.get("best_wpm", 0.0)
                accuracy_val = row.get("best_accuracy", 0.0)
                
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("mode", ""),
                        f"{row.get('duration', 0)}s",
                        f"★ {wpm_val:.1f} WPM",
                        f"{accuracy_val:.1f}%",
                        date_str
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
