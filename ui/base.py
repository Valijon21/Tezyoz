"""
Base classes for TypeMaster user interface.
"""
import tkinter as tk
from tkinter import ttk

class BaseView(ttk.Frame):
    """
    Base view contract class for all screens/views in TypeMaster.
    All view panels should subclass this to get uniform structure.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.controller = controller

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
