"""
Custom Tkinter Canvas-based BarChart component for TypeMaster.
Provides a modern, responsive bar-graph visualization of practice duration or other metrics.
"""
import tkinter as tk
from datetime import datetime

class BarChart(tk.Canvas):
    """
    A custom Tkinter Canvas element designed to display animated, interactive bar graphs.
    Supports dynamic resizing, customized themes, grid lines, and interactive hover tooltips.
    """
    def __init__(self, parent, bg_color="#18181c", bar_color="#3b82f6", 
                 hover_color="#60a5fa", grid_color="#2c2c34", text_color="#646669", 
                 tooltip_bg="#2c2c35", tooltip_fg="#ffffff", **kwargs):
        # Override default options with clean dashboard colors
        kwargs.setdefault("bg", bg_color)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)
        
        self.bg_color = bg_color
        self.bar_color = bar_color
        self.hover_color = hover_color
        self.grid_color = grid_color
        self.text_color = text_color
        self.tooltip_bg = tooltip_bg
        self.tooltip_fg = tooltip_fg
        self.font_family = "Consolas"
        
        # Grid margins
        self.padding_left = 60
        self.padding_right = 20
        self.padding_top = 35
        self.padding_bottom = 45
        
        # State variables
        self.raw_data = []
        self.x_key = "date"
        self.y_key = "practice_seconds"
        self.y_format = "duration"
        
        # Track active tooltip element IDs
        self.active_tooltip = []
        self.hovered_bar = None
        
        # Set resize listener
        self.bind("<Configure>", self._on_resize)

    def apply_theme_colors(self, bg_color, bar_color, hover_color, grid_color, text_color, font_family="Consolas"):
        """
        Dynamically updates chart color parameters and requests redraw.
        """
        self.bg_color = bg_color
        self.bar_color = bar_color
        self.hover_color = hover_color
        self.grid_color = grid_color
        self.text_color = text_color
        self.font_family = font_family
        self.configure(bg=bg_color)
        self.draw()

    def set_data(self, data_points: list, x_key: str = "date", y_key: str = None):
        """
        Updates the dataset and triggers a redraw of the chart.
        :param data_points: List of dicts representing chronological data.
        :param x_key: Key for daily index string (X-axis).
        :param y_key: Key for value metric (Y-axis).
        """
        self.raw_data = data_points or []
        self.x_key = x_key
        if y_key is not None:
            self.y_key = y_key
        elif not hasattr(self, "y_key") or self.y_key is None:
            self.y_key = "practice_seconds"
        self.draw()

    def clear(self):
        """Clears chart data and removes draw components."""
        self.raw_data = []
        self.delete("all")

    def _on_resize(self, event):
        """Dynamic redraw on widget configuration resize changes."""
        self.draw()

    def get_scale_factor(self) -> float:
        """Calculates screen DPI scaling factor using Tk coordinate system ratios."""
        try:
            return float(self.tk.call("tk", "scaling")) / 1.33333333
        except Exception:
            return 1.0

    def _format_value(self, val: float) -> str:
        """Formats the value dynamically depending on y_format."""
        if getattr(self, "y_format", "duration") == "integer":
            return str(int(val))
        return self._format_duration(val)

    def _format_duration(self, seconds: float) -> str:
        """Helper to format practice seconds into readable durations."""
        if seconds < 60:
            return f"{int(seconds)}s"
        else:
            mins = seconds / 60
            if mins.is_integer():
                return f"{int(mins)}m"
            else:
                return f"{mins:.1f}m"

    def draw(self):
        """Main rendering engine mapping historical records to canvas space."""
        self.delete("all")
        self.active_tooltip = []
        self.hovered_bar = None
        
        sf = self.get_scale_factor()

        padding_l = int(self.padding_left * sf)
        padding_r = int(self.padding_right * sf)
        padding_t = int(self.padding_top * sf)
        padding_b = int(self.padding_bottom * sf)

        width = self.winfo_width()
        height = self.winfo_height()
        
        # Fallback to configured dimensions if not plotted/mapped yet
        if width <= 1:
            try:
                width = int(self.cget("width"))
            except (ValueError, tk.TclError):
                width = 200
        if height <= 1:
            try:
                height = int(self.cget("height"))
            except (ValueError, tk.TclError):
                height = 150
                
        # Avoid drawing when viewport size is too small
        if width < 100 or height < 100:
            return
            
        # Draw Empty State if no elements exist
        if not self.raw_data:
            self.create_text(
                width // 2, height // 2,
                text="Natijalar mavjud emas",
                fill=self.text_color,
                font=(self.font_family, int(12 * sf), "bold"),
                anchor="center"
            )
            return

        # Prepare values
        labels = [item.get(self.x_key, "") for item in self.raw_data]
        values = []
        for item in self.raw_data:
            val = item.get(self.y_key, 0.0)
            values.append(float(val) if val is not None else 0.0)
            
        y_max = max(values) if values else 0.0
        # Guard against zero range and provide default scale headroom
        if y_max <= 0.0:
            y_max = 60.0  # Default display height threshold (1 min)
        else:
            y_max = y_max * 1.15  # 15% headroom top spacing

        # Draw grid lines and Y-axis scale ticks
        num_ticks = 4
        plot_height = height - padding_t - padding_b
        plot_width = width - padding_l - padding_r
        
        for i in range(num_ticks + 1):
            factor = i / num_ticks
            y_pos = height - padding_b - (factor * plot_height)
            tick_value = factor * y_max
            
            # Format tick label (e.g. seconds -> mins/seconds)
            label_text = self._format_value(tick_value)
            
            # Draw horizontal boundary separator dash
            self.create_line(
                padding_l, y_pos, 
                width - padding_r, y_pos, 
                fill=self.grid_color, 
                dash=(2, 3)
            )
            
            # Draw tick text
            self.create_text(
                padding_l - int(10 * sf), y_pos, 
                text=label_text, 
                fill=self.text_color, 
                anchor="e", 
                font=(self.font_family, int(8 * sf))
            )

        n_points = len(self.raw_data)
        x_step = plot_width / n_points
        bar_width = min(int(40 * sf), x_step * 0.6)  # Cap bar width to keep visual balance
        
        # Calculate coordinates for bars
        bars_coords = []
        for i, val in enumerate(values):
            x_center = padding_l + ((i + 0.5) * x_step)
            x0 = x_center - (bar_width / 2)
            x1 = x_center + (bar_width / 2)
            y0 = height - padding_b - ((val / y_max) * plot_height)
            y1 = height - padding_b
            bars_coords.append((x0, y0, x1, y1, x_center))

        # Thin out X-axis date labels spacing to prevent layout overlap
        lbl_step = 1
        if n_points > 7:
            lbl_step = 2
        if n_points > 14:
            lbl_step = 5
            
        for i, label in enumerate(labels):
            if i % lbl_step == 0:
                _, _, _, _, x_center = bars_coords[i]
                
                # Format date string for better visualization (e.g. YYYY-MM-DD -> MM-DD)
                formatted_label = label
                try:
                    dt = datetime.strptime(label, "%Y-%m-%d")
                    formatted_label = dt.strftime("%m-%d")
                except Exception:
                    pass
                
                self.create_text(
                    x_center, height - padding_b + int(15 * sf),
                    text=formatted_label,
                    fill=self.text_color,
                    anchor="n",
                    font=(self.font_family, int(8 * sf))
                )

        # Render bars and bind hover interactivity
        for i, (x0, y0, x1, y1, x_center) in enumerate(bars_coords):
            bar_id = self.create_rectangle(
                x0, y0,
                x1, y1,
                fill=self.bar_color,
                outline="",
                width=0,
                tags=("plot_bar", f"bar_{i}")
            )
            
            # Closure function scoping to capture index properly
            self.tag_bind(bar_id, "<Enter>", lambda e, idx=i, px=x_center, py=y0, val=values[i], date=labels[i]: self._on_bar_enter(idx, px, py, val, date))
            self.tag_bind(bar_id, "<Leave>", lambda e, idx=i: self._on_bar_leave(idx))

    def _on_bar_enter(self, index, x, y, value, date):
        """Highlights active bar on hover, drawing tooltip overlays."""
        self._clear_tooltip()
        
        sf = self.get_scale_factor()

        padding_l = int(self.padding_left * sf)
        padding_r = int(self.padding_right * sf)

        self.hovered_bar = f"bar_{index}"
        self.itemconfig(self.hovered_bar, fill=self.hover_color)
        
        # Tooltip formatting
        val_str = self._format_value(value)
        tooltip_text = f"{val_str}\n{date}"
        
        canvas_width = self.winfo_width()
        tip_w = int(90 * sf)
        tip_h = int(42 * sf)
        
        # Horizontal boundaries guard
        tx = x
        if tx < padding_l + (tip_w / 2):
            tx = padding_l + (tip_w / 2)
        elif tx > canvas_width - padding_r - (tip_w / 2):
            tx = canvas_width - padding_r - (tip_w / 2)
            
        ty = y - int(28 * sf)
        
        # Render tooltip box background
        bg_rect = self.create_rectangle(
            tx - (tip_w / 2), ty - (tip_h / 2),
            tx + (tip_w / 2), ty + (tip_h / 2),
            fill=self.tooltip_bg,
            outline=self.bar_color,
            width=int(1 * sf),
            tags="tooltip"
        )
        
        # Render tooltip details text
        txt = self.create_text(
            tx, ty,
            text=tooltip_text,
            fill=self.tooltip_fg,
            font=(self.font_family, int(8 * sf), "bold"),
            justify="center",
            anchor="center",
            tags="tooltip"
        )
        
        self.active_tooltip = [bg_rect, txt]

    def _on_bar_leave(self, index):
        """Restores default bar colors and dismisses active tooltip."""
        if self.hovered_bar:
            self.itemconfig(self.hovered_bar, fill=self.bar_color)
            self.hovered_bar = None
            
        self._clear_tooltip()

    def _clear_tooltip(self):
        """Removes tooltip elements from canvas."""
        for item in self.active_tooltip:
            self.delete(item)
        self.delete("tooltip")
        self.active_tooltip = []

