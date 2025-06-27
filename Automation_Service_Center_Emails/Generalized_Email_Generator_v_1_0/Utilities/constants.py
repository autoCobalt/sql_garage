import os
from typing import List, Dict, Final
from enum import Enum

try:
    from .color_constants import ColorPalettes
except ImportError:
    from color_constants import ColorPalettes

try: # importing install_required_libraries()
    from .package_checker import install_required_libraries
except ImportError:
    from package_checker import install_required_libraries
install_required_libraries({ 'dotenv'})
# used to read a .env file for sensitive variables
from dotenv import dotenv_values

def darken_color(hex_color: str, factor: float = 0.8) -> str:

    hex_color = hex_color.lstrip('#')

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except (ValueError, IndexError):
        return hex_color

    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)

    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return f"#{r:02x}{g:02x}{b:02x}".upper()

def create_hover_color(base_color: str, hover_factor: float = 0.8) -> str:
    return darken_color(base_color, hover_factor)

def create_custom_hover(base_color: str, factor: float) -> str:
    return darken_color(base_color, factor)



class ColorPalette:
    custom_combination: Final[Dict[str, str]] = {
        "primary": "#865BFD",
        "primary_hover": create_hover_color("#865BFD"), 
        "secondary": "#2C3539",
        "accent": "#C0C0C0",
        "background": "#212529",
        "surface": "#1E1E1E",
        "text": "#E5E4E2",
        "success": "#4EBB52", 
        "success_hover": create_hover_color("#4EBB52"), 
        "warning": "#D97706",
        "warning_bg": "#FEF3C7",
        "warning_text": "#92400E",
        "error": "#E91E63",
        "disabled": "#99CBD4"
    }

env_values: Final[Dict[str, str | None]] = dotenv_values()
color_scheme: Final[Dict[str, str]] = ColorPalette.custom_combination

class ConnectionState(Enum):
    IDLE = "idle"
    TESTING = "testing"
    SUCCESS = "success"
    FAILED = "failed"