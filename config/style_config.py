"""
Global Style Configuration for CustomTkinter UI
Supports:
- Responsive compact mode for small screens (<1400px)
- Theme presets: dark / contrast-high
"""

import customtkinter as ctk

# ===============================
# 🔹 COLOR PRESETS
# ===============================

THEMES = {
    "dark": {
        "BG": "#1E1E1E",
        "FRAME": "#2A2A2A",
        "PRIMARY": "#0078D7",
        "ACCENT": "#00BFFF",
        "DANGER": "#E81123",
        "TEXT": "white",
        "TEXT_MUTED": "gray70"
    },
    "contrast-high": {
        "BG": "#000000",
        "FRAME": "#0D0D0D",
        "PRIMARY": "#00FFFF",
        "ACCENT": "#FFFF00",
        "DANGER": "#FF3333",
        "TEXT": "#FFFFFF",
        "TEXT_MUTED": "#CCCCCC"
    }
}

# ===============================
# 🔹 FONT PRESETS
# ===============================
FONT_TITLE = ("Arial", 24, "bold")
FONT_SUBTITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 13)
FONT_SMALL = ("Arial", 11)

# ===============================
# 🔹 SPACING
# ===============================
PADDING_SMALL = 5
PADDING_MEDIUM = 10
PADDING_LARGE = 15

# ===============================
# 🔹 GLOBAL STYLE FUNCTIONS
# ===============================
def apply_global_style(root: ctk.CTk, theme: str = "dark") -> dict:
    """
    Apply theme and base styling to the root window.
    
    Args:
        root: The root CTk window
        theme: Theme name ("dark" or "contrast-high")
    
    Returns:
        dict: Color palette for the selected theme
    """
    if theme not in THEMES:
        theme = "dark"

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    palette = THEMES[theme]
    root.configure(fg_color=palette["BG"])
    return palette


def detect_compact_mode(screen_width: int) -> bool:
    """
    Determine if compact layout should be activated based on screen width.
    
    Args:
        screen_width: Width of the screen in pixels
    
    Returns:
        bool: True if compact mode should be used (screen < 1400px)
    """
    return screen_width < 1400


def get_style_config(root: ctk.CTk, theme: str = "dark") -> dict:
    """
    Detect screen resolution and return comprehensive style parameters.
    
    Args:
        root: The root CTk window
        theme: Theme name ("dark" or "contrast-high")
    
    Returns:
        dict: Style configuration containing:
            - compact: bool - whether to use compact layout
            - palette: dict - color definitions
            - fonts: dict - font presets
            - padding: dict - spacing values
    """
    screen_width = root.winfo_screenwidth()
    compact = detect_compact_mode(screen_width)
    palette = apply_global_style(root, theme)

    fonts = {
        "title": FONT_SUBTITLE if compact else FONT_TITLE,
        "label": FONT_SMALL if compact else FONT_LABEL
    }

    padding = {
        "small": PADDING_SMALL if compact else PADDING_MEDIUM,
        "medium": PADDING_MEDIUM if compact else PADDING_LARGE
    }

    return {
        "compact": compact,
        "palette": palette,
        "fonts": fonts,
        "padding": padding
    }
