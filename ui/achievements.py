"""
Achievements display panel showing unlocked accomplishments and locked milestones.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from ui.base import BaseView
from services.achievements_service import AchievementsService
from services.auth_service import get_current_user

class AchievementsView(BaseView):
    """
    Renders registered achievements in a scrollable list view.
    Highlights unlocked accomplishments and grays out locked milestones.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.achievements_service = AchievementsService()
        self._setup_ui()

    def _setup_ui(self):
        # Base container
        self.container = ttk.Frame(self, padding=20)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Title block
        self.title_label = ttk.Label(
            self.container,
            text="Yutuqlar (Achievements)",
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 15))

        # Main table container frame
        self.table_frame = ttk.Frame(self.container)

        # Empty state warning label
        self.empty_label = ttk.Label(
            self.table_frame,
            text="Yutuqlar yuklanmadi",
            font=("Helvetica", 12, "italic"),
            foreground="#646669"
        )

        # Scrollable Treeview setup
        columns = ("title", "description", "xp_reward", "status", "unlocked_at")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure headings
        self.tree.heading("title", text="Yutuq Nomi")
        self.tree.heading("description", text="Tavsif")
        self.tree.heading("xp_reward", text="XP Mukofoti")
        self.tree.heading("status", text="Holati")
        self.tree.heading("unlocked_at", text="Erishilgan sana")
        
        # Configure columns layout properties
        self.tree.column("title", anchor="w", width=150)
        self.tree.column("description", anchor="w", width=300)
        self.tree.column("xp_reward", anchor="center", width=100)
        self.tree.column("status", anchor="center", width=150)
        self.tree.column("unlocked_at", anchor="center", width=150)

        # Configure row color tags for unlocked/locked achievements
        self.tree.tag_configure("unlocked", foreground="#10b981") # Accent green
        self.tree.tag_configure("locked", foreground="#8e9196") # Muted grey

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

        # Pack table_frame to occupy center space
        self.table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

    def on_show(self):
        """Lifecycle hook reloading user achievements list whenever view becomes active."""
        user = get_current_user()
        if not user:
            self._transition_empty_state(True)
            return

        # Fetch achievements for this user
        ach_list = self.achievements_service.get_all_achievements(user.get("id"))
        
        # Reset Treeview contents
        self.tree.delete(*self.tree.get_children())

        if not ach_list:
            self._transition_empty_state(True)
        else:
            self._transition_empty_state(False)
            for row in ach_list:
                unlocked_at = row.get("unlocked_at")
                
                if unlocked_at:
                    status_text = "Qulfdan chiqarildi 🔥"
                    tag = "unlocked"
                    # Format date string (YYYY-MM-DD HH:MM:SS -> YYYY-MM-DD HH:MM)
                    try:
                        dt = datetime.strptime(unlocked_at, "%Y-%m-%d %H:%M:%S")
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        date_str = unlocked_at
                else:
                    status_text = "Qulflangan 🔒"
                    tag = "locked"
                    date_str = "-"

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("title", ""),
                        row.get("description", ""),
                        f"+{row.get('xp_reward', 0)} XP",
                        status_text,
                        date_str
                    ),
                    tags=(tag,)
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
