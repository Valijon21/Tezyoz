"""
Personal Bests display panel listing user's record typing test runs.
Features a modern split-pane CustomTkinter interface with a comparative BarChart.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import customtkinter as ctk
from ui.base import BaseView
from database.repositories.personal_best_repository import PersonalBestRepository
from services.auth_service import get_current_user
from ui.theme import THEMES
from charts.bar_chart import BarChart

class PersonalBestView(BaseView):
    """
    Renders user's personal best records in a split scrollable table and bar chart view.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, controller, **kwargs)
        self.pb_repo = PersonalBestRepository()
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
            text="Shaxsiy Rekordlar (Personal Bests)",
            font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 15))

        # Bottom navigation controls (packed first under title to reserve bottom area)
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

        # Left Panel (Table) - packed next to chart as direct container children
        self.table_frame = ctk.CTkFrame(self.container, fg_color="transparent", corner_radius=0)
        self.table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right Panel (Chart) - direct container child
        self.chart_panel = ctk.CTkFrame(
            self.container, 
            fg_color=theme_colors["card_bg"], 
            corner_radius=12,
            width=360
        )
        self.chart_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        self.chart_panel.pack_propagate(False)

        # Chart Panel Contents
        self.chart_title = ctk.CTkLabel(
            self.chart_panel,
            text="Rekordlar Solishtiruvi (WPM)",
            font=("Segoe UI", 13, "bold"),
            text_color=theme_colors["fg"]
        )
        self.chart_title.pack(anchor="w", padx=15, pady=(15, 5))

        self.pb_chart = BarChart(self.chart_panel)
        self.pb_chart.y_key = "wpm"
        self.pb_chart.y_format = "integer"
        self.pb_chart.x_key = "category"
        self.pb_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Empty state warning label
        self.empty_label = ctk.CTkLabel(
            self.table_frame,
            text="Shaxsiy rekordlar topilmadi",
            font=("Segoe UI", 13, "italic"),
            text_color=theme_colors["secondary_fg"]
        )

        # Scrollable Treeview setup inside Left Panel
        columns = ("mode", "duration", "best_wpm", "best_accuracy", "achieved_at")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure headings
        self.tree.heading("mode", text="Kategoriya")
        self.tree.heading("duration", text="Vaqt")
        self.tree.heading("best_wpm", text="Tezlik (WPM)")
        self.tree.heading("best_accuracy", text="Aniqlik")
        self.tree.heading("achieved_at", text="Erishilgan sana")
        
        # Configure columns layout properties
        self.tree.column("mode", anchor="center", width=100)
        self.tree.column("duration", anchor="center", width=80)
        self.tree.column("best_wpm", anchor="center", width=110)
        self.tree.column("best_accuracy", anchor="center", width=90)
        self.tree.column("achieved_at", anchor="center", width=140)

        # Scrollbar binding
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def on_show(self):
        """Lifecycle hook reloading user PB list and updating chart."""
        theme = "dark"
        if self.controller and hasattr(self.controller, "current_theme"):
            theme = self.controller.current_theme
        theme_colors = THEMES.get(theme, THEMES["dark"])

        # Dynamically recolor UI components
        self.chart_panel.configure(fg_color=theme_colors["card_bg"])
        self.back_btn.configure(
            fg_color=theme_colors["card_bg"],
            text_color=theme_colors["fg"],
            hover_color=theme_colors["select_bg"]
        )

        # Update Bar Chart styling colors
        self.pb_chart.apply_theme_colors(
            bg_color=theme_colors["card_bg"],
            bar_color=theme_colors["accent"],
            hover_color=theme_colors["accent"],
            grid_color=theme_colors["border"],
            text_color=theme_colors["secondary_fg"]
        )

        user = get_current_user()
        if not user:
            self._transition_empty_state(True)
            self.pb_chart.clear()
            return

        # Fetch records
        pb_list = self.pb_repo.get_all_personal_bests(user.get("id"))
        
        # Reset Treeview contents
        self.tree.delete(*self.tree.get_children())

        if not pb_list:
            self._transition_empty_state(True)
            self.pb_chart.clear()
        else:
            self._transition_empty_state(False)
            
            # Map data points into charts format
            bar_data = []
            for row in pb_list:
                # Format date string
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

                # Append data point comparison entry
                bar_data.append({
                    "category": f"{row.get('mode', '')} {row.get('duration', 0)}s",
                    "wpm": wpm_val
                })
            
            # Set comparitive bar chart datasets
            self.pb_chart.set_data(bar_data, x_key="category", y_key="wpm")

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
        
        if hasattr(self, "chart_panel") and self.chart_panel:
            self.chart_panel.configure(fg_color=theme["card_bg"])
        if hasattr(self, "back_btn") and self.back_btn:
            self.back_btn.configure(
                fg_color=theme["card_bg"],
                text_color=theme["fg"],
                hover_color=theme["select_bg"]
            )
        
        # Configure dynamic charts theme colours
        if hasattr(self, "pb_chart") and self.pb_chart:
            self.pb_chart.apply_theme_colors(
                bg_color=theme["card_bg"],
                bar_color=theme["accent"],
                hover_color=theme["accent"],
                grid_color=theme["border"],
                text_color=theme["secondary_fg"]
            )
