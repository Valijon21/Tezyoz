"""
Custom Tkinter Canvas-based LineChart component for TypeMaster.
Provides a modern, responsive, and animated visualization of user metrics (WPM, Accuracy, etc.).
"""
import tkinter as tk
from datetime import datetime

class LineChart(tk.Canvas):
    """
    A custom Tkinter Canvas element designed to display interactive line graphs.
    Supports dynamic resizing, customized themes, grid lines, and interactive hover tooltips.
    """
    def __init__(self, parent, bg_color="#18181c", line_color="#e2b714", 
                 grid_color="#2c2c34", text_color="#646669", tooltip_bg="#2c2c35", 
                 tooltip_fg="#ffffff", **kwargs):
        # Override default options with clean dashboard colors
        kwargs.setdefault("bg", bg_color)
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)
        
        self.bg_color = bg_color
        self.line_color = line_color
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
        self.y_key = "average_wpm"
        
        # Track active tooltip element IDs
        self.active_tooltip = []
        self.hovered_dot = None
        
        # Set resize listener
        self.bind("<Configure>", self._on_resize)

    def apply_theme_colors(self, bg_color, line_color, grid_color, text_color, font_family="Consolas"):
        """
        Dynamically updates chart color parameters and requests redraw.
        """
        self.bg_color = bg_color
        self.line_color = line_color
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

    def draw(self):
        """Main rendering engine mapping historical records to canvas space."""
        self.delete("all")
        self.active_tooltip = []
        self.hovered_dot = None
        
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
                font=("Helvetica", int(12 * sf), "bold"),
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
            y_max = 50.0  # Default display height threshold
        else:
            y_max = y_max * 1.15  # 15% headroom top spacing

        # Cap ceiling range bounds for accuracy metrics
        if "accuracy" in self.y_key and y_max > 100.0:
            y_max = 100.0

        # Draw grid lines and Y-axis scale ticks
        num_ticks = 4
        plot_height = height - padding_t - padding_b
        plot_width = width - padding_l - padding_r
        
        for i in range(num_ticks + 1):
            factor = i / num_ticks
            y_pos = height - padding_b - (factor * plot_height)
            tick_value = factor * y_max
            
            # Format tick label (remove decimal place if integer value)
            label_text = f"{int(tick_value)}" if tick_value.is_integer() else f"{tick_value:.1f}"
            
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
        x_step = plot_width / (n_points - 1) if n_points > 1 else plot_width
        
        # Calculate coordinates for dots and lines
        points_coords = []
        for i, val in enumerate(values):
            x = padding_l + (i * x_step)
            # Map Y coordinate safely
            y = height - padding_b - ((val / y_max) * plot_height)
            points_coords.append((x, y))

        # Thin out X-axis date labels spacing to prevent layout overlap
        lbl_step = 1
        if n_points > 7:
            lbl_step = 2
        if n_points > 14:
            lbl_step = 5
            
        for i, label in enumerate(labels):
            if i % lbl_step == 0:
                x, _ = points_coords[i]
                
                # Format date string for better visualization (e.g. YYYY-MM-DD -> MM-DD)
                formatted_label = label
                try:
                    dt = datetime.strptime(label, "%Y-%m-%d")
                    formatted_label = dt.strftime("%m-%d")
                except Exception:
                    pass
                
                self.create_text(
                    x, height - padding_b + int(15 * sf),
                    text=formatted_label,
                    fill=self.text_color,
                    anchor="n",
                    font=(self.font_family, int(8 * sf))
                )

        # Render connecting plot line paths
        if n_points > 1:
            flat_coords = []
            for x, y in points_coords:
                flat_coords.extend([x, y])
                
            # Render a smooth primary bezier curve
            self.create_line(
                flat_coords, 
                fill=self.line_color, 
                width=int(3 * sf), 
                smooth=True, 
                tags="plot_line"
            )

        # Render dot nodes and bind hover interactivity
        dot_r = 4.5 * sf
        for i, (x, y) in enumerate(points_coords):
            dot_id = self.create_oval(
                x - dot_r, y - dot_r,
                x + dot_r, y + dot_r,
                fill=self.line_color,
                outline=self.bg_color,
                width=int(1.5 * sf),
                tags=("plot_dot", f"dot_{i}")
            )
            
            # Closure function scoping to capture index properly
            self.tag_bind(dot_id, "<Enter>", lambda e, idx=i, px=x, py=y, val=values[i], date=labels[i]: self._on_dot_enter(idx, px, py, val, date))
            self.tag_bind(dot_id, "<Leave>", lambda e, idx=i: self._on_dot_leave(idx))

    def _on_dot_enter(self, index, x, y, value, date):
        """Triggers hovering highlight actions and shows metric values and date tooltip details."""
        # Clean any old hanging elements
        self._clear_tooltip()
        
        sf = self.get_scale_factor()

        padding_l = int(self.padding_left * sf)
        padding_r = int(self.padding_right * sf)

        # Visually scale selected dot indicator
        self.hovered_dot = f"dot_{index}"
        highlight_r = 6.5 * sf
        self.coords(
            self.hovered_dot, 
            x - highlight_r, y - highlight_r, 
            x + highlight_r, y + highlight_r
        )
        self.itemconfig(self.hovered_dot, width=int(2 * sf), outline="#ffffff")
        
        # Format Tooltip Text details
        val_str = f"{value:.1f} WPM" if self.y_key == "average_wpm" or "wpm" in self.y_key else f"{value:.1f}"
        if "accuracy" in self.y_key:
            val_str = f"{value:.1f}%"
            
        tooltip_text = f"{val_str}\n{date}"
        
        # Calculate tooltip render positioning coordinates safely bounds
        canvas_width = self.winfo_width()
        tip_w = int(90 * sf)
        tip_h = int(42 * sf)
        
        # Place tooltip above the dot, shifting horizontally if near bounds
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
            outline=self.line_color,
            width=int(1 * sf),
            tags="tooltip"
        )
        
        # Render tooltip details text
        txt = self.create_text(
            tx, ty,
            text=tooltip_text,
            fill=self.tooltip_fg,
            font=("Helvetica", int(8 * sf), "bold"),
            justify="center",
            anchor="center",
            tags="tooltip"
        )
        
        self.active_tooltip = [bg_rect, txt]

    def _on_dot_leave(self, index):
        """Restores selected dot and dismisses active tooltip."""
        sf = self.get_scale_factor()

        if self.hovered_dot:
            # Re-fetch default coordinates
            dot_r = 4.5 * sf
            coords = self.coords(self.hovered_dot)
            if coords:
                cx = (coords[0] + coords[2]) / 2
                cy = (coords[1] + coords[3]) / 2
                self.coords(
                    self.hovered_dot,
                    cx - dot_r, cy - dot_r,
                    cx + dot_r, cy + dot_r
                )
            self.itemconfig(self.hovered_dot, width=int(1.5 * sf), outline=self.bg_color)
            self.hovered_dot = None
            
        self._clear_tooltip()

    def _clear_tooltip(self):
        """Removes tooltip elements from canvas."""
        for item in self.active_tooltip:
            self.delete(item)
        self.delete("tooltip")
        self.active_tooltip = []



class AccuracyChart(LineChart):
    """
    Subclass of LineChart preconfigured for rendering accuracy metrics.
    Uses emerald green accent line and default average_accuracy key.
    """
    def __init__(self, parent, bg_color="#18181c", line_color="#10b981", 
                 grid_color="#2c2c34", text_color="#646669", tooltip_bg="#2c2c35", 
                 tooltip_fg="#ffffff", **kwargs):
        super().__init__(parent, bg_color=bg_color, line_color=line_color, 
                         grid_color=grid_color, text_color=text_color, 
                         tooltip_bg=tooltip_bg, tooltip_fg=tooltip_fg, **kwargs)
        self.y_key = "average_accuracy"

