"""
Style themes and palette manager for TypeMaster.
Provides style definitions and override routines for dark, light, and cyberpunk settings.
"""
import tkinter as tk
from tkinter import ttk

THEMES = {
    "dark": {
        "bg": "#15161f",          # Slate/charcoal background
        "fg": "#ffffff",          # White foreground
        "card_bg": "#1e1f29",     # Elevated card background
        "border": "#282a36",      # Premium thin border
        "accent": "#00f0ff",      # Glowing cyan accent
        "accent_fg": "#14151f",   # Dark text for accent buttons
        "secondary_fg": "#8e9196", # Muted slate text
        "chart_grid": "#24283b",
        "chart_line": "#00f0ff",
        "chart_line2": "#3b82f6",
        "entry_bg": "#10111a",
        "entry_fg": "#ffffff",
        "select_bg": "#24283b",
        "sidebar_bg": "#14151f"
    },
    "light": {
        "bg": "#f9fafb",
        "fg": "#111827",
        "card_bg": "#ffffff",
        "border": "#e5e7eb",
        "accent": "#4f46e5",
        "accent_fg": "#ffffff",
        "secondary_fg": "#4b5563",
        "chart_grid": "#f3f4f6",
        "chart_line": "#4f46e5",
        "chart_line2": "#06b6d4",
        "entry_bg": "#ffffff",
        "entry_fg": "#111827",
        "select_bg": "#e5e7eb",
        "sidebar_bg": "#f3f4f6"
    },
    "cyberpunk": {
        "bg": "#050515",
        "fg": "#00f0ff",
        "card_bg": "#0d0d2b",
        "border": "#ff007f",
        "accent": "#ff007f",
        "accent_fg": "#050515",
        "secondary_fg": "#a100ff",
        "chart_grid": "#1f003d",
        "chart_line": "#ff007f",
        "chart_line2": "#00f0ff",
        "entry_bg": "#02020a",
        "entry_fg": "#00f0ff",
        "select_bg": "#1f003d",
        "sidebar_bg": "#03030b"
    }
}

def apply_theme_colors(style: ttk.Style, theme_name: str, font_family: str = "Segoe UI", font_size: int = 11):
    """
    Applies overrides to the given ttk.Style instance using colors from the selected theme,
    and scales standard text displays using the selected font configurations.
    """
    # Force Segoe UI (fluent system font) for main UI, but allow Consolas fallback for code
    if font_family in ("Helvetica", "TkDefaultFont", "Arial"):
        font_family = "Segoe UI"

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
    style.configure("Sidebar.TFrame", background=theme.get("sidebar_bg", bg))
    
    # Labels
    style.configure("TLabel", background=bg, foreground=fg, font=(font_family, font_size))
    style.configure("Title.TLabel", background=bg, foreground=fg, font=(font_family, int(font_size * 1.5), "bold"))
    style.configure("Secondary.TLabel", background=bg, foreground=sec_fg, font=(font_family, int(font_size * 0.95)))
    style.configure("Link.TLabel", background=bg, foreground=accent, font=(font_family, int(font_size * 0.95), "underline"))
    style.configure("Card.TLabel", background=card_bg, foreground=fg, font=(font_family, font_size))
    style.configure("CardSecondary.TLabel", background=card_bg, foreground=sec_fg, font=(font_family, int(font_size * 0.95)))
    style.configure("CardValue.TLabel", background=card_bg, foreground=fg, font=(font_family, int(font_size * 1.4), "bold"))
    style.configure("CardTitle.TLabel", background=card_bg, foreground=fg, font=(font_family, int(font_size * 1.4), "bold"))
    style.configure("CardLink.TLabel", background=card_bg, foreground=accent, font=(font_family, int(font_size * 0.95), "underline"))
    style.configure("Sidebar.TLabel", background=theme.get("sidebar_bg", bg), foreground=fg, font=(font_family, font_size))
    style.configure("SidebarTitle.TLabel", background=theme.get("sidebar_bg", bg), foreground=fg, font=(font_family, int(font_size * 1.3), "bold"))

    
    # LabelFrames
    style.configure("TLabelframe", background=bg, foreground=fg, bordercolor=border)
    style.configure("TLabelframe.Label", background=bg, foreground=fg, font=(font_family, font_size, "bold"))
    style.configure("Card.TLabelframe", background=card_bg, foreground=fg, bordercolor=border)
    style.configure("Card.TLabelframe.Label", background=card_bg, foreground=fg, font=(font_family, font_size, "bold"))

    # Modern flat buttons padding and styles
    style.configure("TButton", background=card_bg, foreground=fg, bordercolor=border, relief="flat", font=(font_family, font_size, "bold"), padding=(15, 6))
    style.map("TButton",
              background=[("active", border), ("pressed", bg)],
              foreground=[("active", fg)])
              
    style.configure("Accent.TButton", background=accent, foreground=accent_fg, bordercolor=accent, relief="flat", font=(font_family, font_size, "bold"), padding=(15, 6))
    style.map("Accent.TButton",
              background=[("active", accent), ("pressed", accent)],
              foreground=[("active", accent_fg)])

    # Navigation Buttons (Sidebar)
    style.configure("Nav.TButton", background=theme.get("sidebar_bg", bg), foreground=theme["secondary_fg"], relief="flat", font=(font_family, font_size, "bold"), padding=(10, 8))
    style.map("Nav.TButton",
              background=[("active", theme["select_bg"]), ("selected", theme["select_bg"])],
              foreground=[("active", fg), ("selected", fg)])
              
    style.configure("NavActive.TButton", background=theme["select_bg"], foreground=fg, relief="flat", font=(font_family, font_size, "bold"), padding=(10, 8))
    style.map("NavActive.TButton",
              background=[("active", theme["select_bg"])],
              foreground=[("active", fg)])

    # Entry
    style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], bordercolor=border, font=(font_family, font_size), padding=6)
    style.map("TEntry",
              fieldbackground=[("active", theme["entry_bg"]), ("focus", theme["entry_bg"]), ("disabled", bg)],
              foreground=[("active", theme["entry_fg"]), ("focus", theme["entry_fg"]), ("disabled", sec_fg)],
              bordercolor=[("focus", accent), ("active", border)])
    
    # Combobox
    style.configure("TCombobox", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], selectbackground=theme["select_bg"], font=(font_family, font_size))
    style.map("TCombobox",
              fieldbackground=[("readonly", theme["entry_bg"]), ("disabled", bg)],
              background=[("readonly", theme["entry_bg"]), ("active", border)],
              foreground=[("readonly", theme["entry_fg"]), ("disabled", sec_fg)],
              bordercolor=[("focus", accent), ("active", border)])
              
    # Option database style overrides for the popup listbox of the Comboboxes
    style.master.option_add("*TCombobox*Listbox.background", theme["entry_bg"])
    style.master.option_add("*TCombobox*Listbox.foreground", theme["entry_fg"])
    style.master.option_add("*TCombobox*Listbox.selectBackground", theme["select_bg"])
    style.master.option_add("*TCombobox*Listbox.selectForeground", fg)
    style.master.option_add("*TCombobox*Listbox.font", (font_family, font_size))
    
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
                    rowheight=int(font_size * 2.2),
                    font=(font_family, font_size))
    style.configure("Treeview.Heading",
                    background=border,
                    foreground=fg,
                    bordercolor=bg,
                    font=(font_family, font_size, "bold"))
    style.map("Treeview",
              background=[("selected", theme["select_bg"])],
              foreground=[("selected", fg)])

