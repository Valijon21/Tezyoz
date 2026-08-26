"""
Keyboard Heatmap visualization component for TypeMaster.
Draws a QWERTY keyboard layout using Canvas and colors keys based on error rates.
"""
import tkinter as tk
from tkinter import ttk

class KeyboardHeatmap(ttk.Frame):
    """
    Tkinter widget that renders an interactive visual keyboard heatmap.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        # Tooltip details label at the top
        self.details_label = ttk.Label(
            self,
            text="Statistikani ko'rish uchun sichqonchani tugma ustiga olib boring",
            font=("Helvetica", 11, "italic"),
            anchor="center"
        )
        self.details_label.pack(fill=tk.X, pady=(0, 10))

        # Canvas for drawing the keyboard
        self.canvas_width = 580
        self.canvas_height = 230
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas.pack(pady=5)

        # Keyboard layout configuration
        self.keyboard_rows = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"]
        ]

        self.key_width = 44
        self.key_height = 44
        self.key_gap = 6

        # Physical spacing offsets
        self.row_offsets = [
            (25, 10),    # Row 1 (Q) starts at x=25, y=10
            (40, 60),    # Row 2 (A) starts at x=40, y=60
            (65, 110),   # Row 3 (Z) starts at x=65, y=110
            (150, 160)   # Row 4 (Space) starts at x=150, y=160
        ]

        # Key state tracking and map of drawing components
        self.key_stats = {}
        self.keys = {} # key name -> {"rect_id", "text_id", "char"}

        self._draw_keyboard()

        # Canvas hover bind
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

    def _draw_keyboard(self):
        self.canvas.delete("all")
        self.keys.clear()

        # 1. Draw character rows
        for row_idx, chars in enumerate(self.keyboard_rows):
            start_x, y = self.row_offsets[row_idx]
            for col_idx, char in enumerate(chars):
                x = start_x + col_idx * (self.key_width + self.key_gap)
                
                # Draw key backing
                rect_id = self.canvas.create_rectangle(
                    x, y, x + self.key_width, y + self.key_height,
                    fill="#f1f5f9", outline="#cbd5e1", width=1, tags="key"
                )
                
                # Draw letter label
                text_id = self.canvas.create_text(
                    x + self.key_width/2, y + self.key_height/2,
                    text=char.upper(), font=("Helvetica", 11, "bold"),
                    fill="#1e293b"
                )

                self.keys[char] = {
                    "rect_id": rect_id,
                    "text_id": text_id,
                    "char": char,
                    "coords": (x, y, x + self.key_width, y + self.key_height)
                }

        # 2. Draw Spacebar row
        space_x, space_y = self.row_offsets[3]
        space_w = 260
        rect_id = self.canvas.create_rectangle(
            space_x, space_y, space_x + space_w, space_y + self.key_height,
            fill="#f1f5f9", outline="#cbd5e1", width=1, tags="key"
        )
        text_id = self.canvas.create_text(
            space_x + space_w/2, space_y + self.key_height/2,
            text="Spacebar", font=("Helvetica", 10, "bold"),
            fill="#1e293b"
        )
        self.keys[" "] = {
            "rect_id": rect_id,
            "text_id": text_id,
            "char": " ",
            "coords": (space_x, space_y, space_x + space_w, space_y + self.key_height)
        }

    def set_data(self, key_stats: dict):
        """
        Refreshes key backing colors based on error rate intensity.
        """
        self.key_stats = key_stats or {}
        
        for char, widgets in self.keys.items():
            stats = self.key_stats.get(char)
            
            if not stats or stats.get("attempts", 0) == 0:
                # Untyped key gets standard gray appearance
                bg_color = "#f1f5f9"
                fg_color = "#1e293b"
            else:
                attempts = stats.get("attempts", 0)
                errors = stats.get("errors", 0)
                error_rate = (errors * 100.0) / attempts if attempts > 0 else 0.0
                
                # Interpolate colors based on error rate intensity (0.0 to 1.0)
                # Max intensity reached at >= 35.0% error rate
                intensity = min(1.0, error_rate / 35.0)
                
                if errors == 0:
                    bg_color = "#10b981" # Healthy green
                    fg_color = "#ffffff"
                else:
                    bg_color = self._interpolate_color(intensity)
                    # Text should be white for high intensity warm colors, dark for low yellow
                    fg_color = "#ffffff" if intensity > 0.4 else "#1e293b"

            self.canvas.itemconfig(widgets["rect_id"], fill=bg_color)
            self.canvas.itemconfig(widgets["text_id"], fill=fg_color)

    def _interpolate_color(self, val: float) -> str:
        """Interpolates green -> yellow -> red based on error rate parameter."""
        # Start (0.0) = Green #10b981 (16, 185, 129)
        # Mid (0.5) = Yellow #f59e0b (245, 158, 11)
        # End (1.0) = Red/Crimson #ef4444 (239, 68, 68)
        if val <= 0.0:
            return "#10b981"
        if val >= 1.0:
            return "#ef4444"

        if val < 0.5:
            # Green to Yellow
            t = val * 2.0
            r = int(16 + (245 - 16) * t)
            g = int(185 + (158 - 185) * t)
            b = int(129 + (11 - 129) * t)
        else:
            # Yellow to Red
            t = (val - 0.5) * 2.0
            r = int(245 + (239 - 245) * t)
            g = int(158 + (68 - 158) * t)
            b = int(11 + (68 - 11) * t)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _on_mouse_move(self, event):
        x, y = event.x, event.y
        hovered_char = None
        
        # Find which key is under cursor
        for char, widgets in self.keys.items():
            x1, y1, x2, y2 = widgets["coords"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                hovered_char = char
                break

        if hovered_char:
            stats = self.key_stats.get(hovered_char)
            char_display = "Space" if hovered_char == " " else hovered_char.upper()
            
            if not stats or stats.get("attempts", 0) == 0:
                txt = f"Tugma: {char_display} | Hali ishlatilmadi"
            else:
                attempts = stats["attempts"]
                errors = stats["errors"]
                rate = (errors * 100.0) / attempts
                txt = f"Tugma: {char_display} | Urinishlar: {attempts} | Xatolar: {errors} ({rate:.1f}% xatolik)"
            self.details_label.config(text=txt)
        else:
            self.details_label.config(
                text="Statistikani ko'rish uchun sichqonchani tugma ustiga olib boring"
            )

    def _on_mouse_leave(self, event):
        self.details_label.config(
            text="Statistikani ko'rish uchun sichqonchani tugma ustiga olib boring"
        )
