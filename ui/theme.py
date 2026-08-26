"""
Style themes and palette manager for TypeMaster.
Provides style definitions and override routines for dark, light, and cyberpunk settings.
"""
import tkinter as tk
from tkinter import ttk

THEMES = {
    "dark": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "card_bg": "#313244",
        "border": "#45475a",
        "accent": "#f5c2e7",
        "accent_fg": "#11111b",
        "secondary_fg": "#a6adc8",
        "chart_grid": "#45475a",
        "chart_line": "#f5c2e7",
        "chart_line2": "#89b4fa",
        "entry_bg": "#181825",
        "entry_fg": "#cdd6f4",
        "select_bg": "#313244"
    },
    "light": {
        "bg": "#f4f4f7",
        "fg": "#1e1e2e",
        "card_bg": "#ffffff",
        "border": "#e2e8f0",
        "accent": "#4f46e5",
        "accent_fg": "#ffffff",
        "secondary_fg": "#64748b",
        "chart_grid": "#cbd5e1",
        "chart_line": "#4f46e5",
        "chart_line2": "#06b6d4",
        "entry_bg": "#ffffff",
        "entry_fg": "#1e1e2e",
        "select_bg": "#e2e8f0"
    },
    "cyberpunk": {
        "bg": "#0d021c",
        "fg": "#00ffcc",
        "card_bg": "#1a0833",
        "border": "#ff007f",
        "accent": "#ff007f",
        "accent_fg": "#0d021c",
        "secondary_fg": "#ff00ff",
        "chart_grid": "#330d66",
        "chart_line": "#ff007f",
        "chart_line2": "#00ffcc",
        "entry_bg": "#0a0014",
        "entry_fg": "#00ffcc",
        "select_bg": "#330d66"
    }
}

def apply_theme_colors(style: ttk.Style, theme_name: str, font_family: str = "Consolas", font_size: int = 14):
    """
    Applies overrides to the given ttk.Style instance using colors from the selected theme,
    and scales standard text displays using the selected font configurations.
    """
    theme = THEMES.get(theme_name, THEMES["dark"])
    bg = theme["bg"]
    fg = theme["fg"]
    card_bg = theme["card_bg"]
    border = theme["border"]
    accent = theme["accent"]
    accent_fg = theme["accent_fg"]
    sec_fg = theme["secondary_fg"]

    # Configure parent settings
    style.configure(".", background=bg, foreground=fg, font=(font_family, font_size))
    
    # Frames
    style.configure("TFrame", background=bg)
    style.configure("Card.TFrame", background=card_bg)
    
    # Labels
    style.configure("TLabel", background=bg, foreground=fg, font=(font_family, font_size))
    style.configure("Title.TLabel", background=bg, foreground=fg, font=(font_family, int(font_size * 1.5), "bold"))
    style.configure("Secondary.TLabel", background=bg, foreground=sec_fg, font=(font_family, int(font_size * 0.95)))
    style.configure("Card.TLabel", background=card_bg, foreground=fg, font=(font_family, font_size))
    style.configure("CardSecondary.TLabel", background=card_bg, foreground=sec_fg, font=(font_family, int(font_size * 0.95)))
    style.configure("CardValue.TLabel", background=card_bg, foreground=fg, font=(font_family, int(font_size * 1.3), "bold"))
    
    # LabelFrames
    style.configure("TLabelframe", background=bg, foreground=fg, bordercolor=border)
    style.configure("TLabelframe.Label", background=bg, foreground=fg, font=(font_family, font_size, "bold"))
    style.configure("Card.TLabelframe", background=card_bg, foreground=fg, bordercolor=border)
    style.configure("Card.TLabelframe.Label", background=card_bg, foreground=fg, font=(font_family, font_size, "bold"))

    # Buttons
    style.configure("TButton", background=card_bg, foreground=fg, bordercolor=border, relief="flat", font=(font_family, font_size))
    style.map("TButton",
              background=[("active", border), ("pressed", bg)],
              foreground=[("active", fg)])
              
    style.configure("Accent.TButton", background=accent, foreground=accent_fg, bordercolor=accent, relief="flat", font=(font_family, font_size, "bold"))
    style.map("Accent.TButton",
              background=[("active", accent), ("pressed", accent)],
              foreground=[("active", accent_fg)])

    # Entry
    style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], bordercolor=border, font=(font_family, font_size))
    
    # Combobox
    style.configure("TCombobox", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], selectbackground=theme["select_bg"], font=(font_family, font_size))
    
    # Progressbar
    style.configure("Horizontal.TProgressbar",
                    troughcolor=bg,
                    background=accent,
                    bordercolor=border,
                    lightcolor=accent,
                    darkcolor=accent)
    
    # Checkbutton
    style.configure("TCheckbutton", background=bg, foreground=fg, font=(font_family, font_size))
    
    # Scrollbar
    style.configure("Vertical.TScrollbar", background=card_bg, bordercolor=border, troughcolor=bg)

    # Treeview
    style.configure("Treeview",
                    background=card_bg,
                    foreground=fg,
                    fieldbackground=card_bg,
                    bordercolor=border,
                    rowheight=int(font_size * 1.8),
                    font=(font_family, font_size))
    style.configure("Treeview.Heading",
                    background=border,
                    foreground=fg,
                    bordercolor=bg,
                    font=(font_family, font_size, "bold"))
    style.map("Treeview",
              background=[("selected", theme["select_bg"])],
              foreground=[("selected", fg)])
