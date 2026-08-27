"""
Base classes for TypeMaster user interface.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class BaseView(ctk.CTkFrame):
    """
    Base view contract class for all screens/views in TypeMaster.
    All view panels should subclass this to get uniform structure.
    """
    def __init__(self, parent, controller, **kwargs):
        # Configure CTkFrame options safely with transparent bg or default
        if "fg_color" not in kwargs:
            kwargs["fg_color"] = "transparent"
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.controller = controller
        # Bind hover effects once child widgets are fully constructed and mapped
        self.bind("<Map>", lambda e: self._bind_hover_effects(self), add="+")

    def _bind_hover_effects(self, widget):
        """Recursively scans and binds standard Ttk active state triggers on hover."""
        try:
            classname = widget.winfo_class()
            if "Button" in classname:
                widget.bind("<Enter>", lambda e, w=widget: w.state(["active"]), add="+")
                widget.bind("<Leave>", lambda e, w=widget: w.state(["!active"]), add="+")
        except Exception:
            pass

        for child in widget.winfo_children():
            self._bind_hover_effects(child)


    def on_show(self):
        """
        Called when this view becomes active/visible on the screen.
        Can be overridden by subclasses for data refreshing.
        """
        pass

    def on_hide(self):
        """
        Called when the view is transitioned away from.
        Can be overridden by subclasses for clean up.
        """
        pass

    def apply_theme(self, theme_name: str):
        """
        Called when the active UI theme changes.
        Can be overridden by subclasses to update custom drawing elements.
        """
        pass

    def get_scale_factor(self) -> float:
        """Calculates screen DPI scaling factor using Tk coordinate system ratios."""
        try:
            return float(self.tk.call("tk", "scaling")) / 1.33333333
        except Exception:
            return 1.0

    def scale_px(self, px: int) -> int:
        """Converts raw pixel size to scaled integer values based on current DPI."""
        return int(px * self.get_scale_factor())

