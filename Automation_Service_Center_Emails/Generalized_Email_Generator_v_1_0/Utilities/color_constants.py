from typing import Final, Dict

def create_hover_color(base_color: str, hover_factor: float = 0.8) -> str:
    hex_color = base_color.lstrip('#')
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except (ValueError, IndexError):
        return base_color # Return original if invalid
    
    # Apply darkening factor
    r = int(r * hover_factor)
    g = int(g * hover_factor)
    b = int(b * hover_factor)
    
    # Ensure values stay within 0-255 range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}".upper()

class ModernColors:
    """
    Comprehensive modern color palette optimized for customtkinter applications.
    Features 120+ carefully curated colors including 2025 trending colors from
    major design authorities like Pantone, Sherwin-Williams, and Behr.
    
    Colors are organized by category and designed to work well together.
    All values are hex color codes. Updated with latest design trends including:
    - Pantone Color of the Year 2025 (Mocha Mousse)
    - Digital Lavender and ethereal blues
    - Earthy browns and terracotta tones
    - Metallic finishes for futuristic designs
    - Creamy pastels and sophisticated neutrals
    """
    
    # === NEUTRALS & GRAYS ===
    # Essential for backgrounds, text, and UI elements
    pure_white: Final[str] = "#FFFFFF"
    ghost_white: Final[str] = "#F8F9FA"
    light_gray: Final[str] = "#F1F3F4"
    silver_mist: Final[str] = "#E9ECEF"
    cool_gray: Final[str] = "#DEE2E6"
    medium_gray: Final[str] = "#ADB5BD"
    slate_gray: Final[str] = "#6C757D"
    dark_gray: Final[str] = "#495057"
    charcoal: Final[str] = "#343A40"
    gunmetal: Final[str] = "#2D3436"
    space_gray: Final[str] = "#212529"
    midnight_black: Final[str] = "#000000"
    
    # === BLUES ===
    # Popular in modern UI design, professional and calming
    ice_blue: Final[str] = "#E3F2FD"
    sky_blue: Final[str] = "#BBDEFB"
    cornflower_blue: Final[str] = "#90CAF9"
    ocean_blue: Final[str] = "#64B5F6"
    azure: Final[str] = "#42A5F5"
    royal_blue: Final[str] = "#2196F3"
    cobalt_blue: Final[str] = "#1E88E5"
    navy_blue: Final[str] = "#1976D2"
    midnight_blue: Final[str] = "#1565C0"
    deep_blue: Final[str] = "#0D47A1"
    steel_blue: Final[str] = "#455A64"
    slate_blue: Final[str] = "#37474F"
    
    # === GREENS ===
    # Great for success states and nature-inspired themes
    mint_green: Final[str] = "#E8F5E8"
    sage_green: Final[str] = "#C8E6C9"
    lime_green: Final[str] = "#A5D6A7"
    forest_green: Final[str] = "#81C784"
    emerald_green: Final[str] = "#66BB6A"
    jade_green: Final[str] = "#4CAF50"
    pine_green: Final[str] = "#43A047"
    hunter_green: Final[str] = "#388E3C"
    dark_green: Final[str] = "#2E7D32"
    deep_forest: Final[str] = "#1B5E20"
    teal: Final[str] = "#009688"
    dark_teal: Final[str] = "#00695C"
    
    # === PURPLES ===
    # Modern, creative, and sophisticated
    lavender: Final[str] = "#F3E5F5"
    lilac: Final[str] = "#E1BEE7"
    orchid: Final[str] = "#CE93D8"
    amethyst: Final[str] = "#BA68C8"
    violet: Final[str] = "#AB47BC"
    purple: Final[str] = "#9C27B0"
    deep_purple: Final[str] = "#8E24AA"
    royal_purple: Final[str] = "#7B1FA2"
    indigo: Final[str] = "#673AB7"
    dark_indigo: Final[str] = "#512DA8"
    midnight_purple: Final[str] = "#4527A0"
    eggplant: Final[str] = "#311B92"
    
    # === REDS ===
    # Perfect for warnings, errors, and accent colors
    rose_pink: Final[str] = "#FFEBEE"
    blush_pink: Final[str] = "#FFCDD2"
    coral_pink: Final[str] = "#EF9A9A"
    salmon: Final[str] = "#E57373"
    tomato_red: Final[str] = "#EF5350"
    crimson: Final[str] = "#F44336"
    cherry_red: Final[str] = "#E53935"
    ruby_red: Final[str] = "#D32F2F"
    burgundy: Final[str] = "#C62828"
    wine_red: Final[str] = "#B71C1C"
    brick_red: Final[str] = "#8D1E1E"
    maroon: Final[str] = "#5D1212"
    
    # === ORANGES & YELLOWS ===
    # Great for highlights and warm accents
    cream: Final[str] = "#FFF8E1"
    champagne: Final[str] = "#FFECB3"
    gold: Final[str] = "#FFD54F"
    mustard_yellow: Final[str] = "#FFDB58"
    amber: Final[str] = "#FFC107"
    honey: Final[str] = "#FFB300"
    orange: Final[str] = "#FF9800"
    burnt_orange: Final[str] = "#F57C00"
    tangerine: Final[str] = "#FF6F00"
    copper: Final[str] = "#E65100"
    rust: Final[str] = "#BF360C"
    
    # === 2025 TRENDING COLORS ===
    # Based on Pantone and major color authorities for 2025
    mocha_mousse: Final[str] = "#A47864"          # Pantone Color of the Year 2025
    digital_lavender: Final[str] = "#A78BFA"      # Tranquil, ethereal purple
    canary_yellow: Final[str] = "#FFD700"         # Optimistic, energetic bright yellow
    verdant_green: Final[str] = "#4CAF50"         # Vibrant, nature-inspired emerald
    muted_rose: Final[str] = "#D4A5A5"            # Sophisticated, calming pink
    burnt_sienna: Final[str] = "#CC5500"          # Rich, earthy orange-red
    sage_blue: Final[str] = "#8FBC8F"             # Calming sage with blue undertones
    terracotta_clay: Final[str] = "#C99383"       # Warm, grounding earth tone
    ethereal_blue: Final[str] = "#B6E5FF"         # Soft, otherworldly blue
    deep_ruby: Final[str] = "#8B0000"             # Rich, passionate red
    
    # === MODERN ACCENT COLORS ===
    # Trending colors for contemporary designs
    electric_blue: Final[str] = "#00B4D8"
    cyan: Final[str] = "#00BCD4"
    turquoise: Final[str] = "#1DE9B6"
    neon_green: Final[str] = "#64DD17"
    lime: Final[str] = "#76FF03"
    hot_pink: Final[str] = "#E91E63"
    magenta: Final[str] = "#FF1744"
    electric_purple: Final[str] = "#7C4DFF"
    
    # === METALLIC & FUTURISTIC ===
    # Modern metallics for luxury and tech designs
    chrome_silver: Final[str] = "#C0C0C0"
    platinum: Final[str] = "#E5E4E2"
    gunmetal_gray: Final[str] = "#2C3539"
    rose_gold: Final[str] = "#E8B4B8"
    champagne_gold: Final[str] = "#F7E7CE"
    copper_bronze: Final[str] = "#B87333"
    
    # === CREAMY PASTELS ===
    # Warm, sophisticated pastel variations
    cream_mint: Final[str] = "#F0FFF0"
    cream_peach: Final[str] = "#FFEBE9"
    cream_lavender: Final[str] = "#F5F0FF"
    cream_yellow: Final[str] = "#FFFEF7"
    dusty_pink: Final[str] = "#DCC0C6"
    dusty_blue: Final[str] = "#A8C8E1"
    
    # === SPECIAL UI COLORS ===
    # Commonly used in modern applications
    success_green: Final[str] = "#28A745"
    warning_yellow: Final[str] = "#FFC107"
    danger_red: Final[str] = "#DC3545"
    info_blue: Final[str] = "#17A2B8"
    
    # === DARK MODE OPTIMIZED ===
    # Perfect for dark theme applications
    dark_background: Final[str] = "#121212"
    dark_surface: Final[str] = "#1E1E1E"
    dark_card: Final[str] = "#2D2D2D"
    dark_border: Final[str] = "#3D3D3D"
    dark_text_primary: Final[str] = "#FFFFFF"
    dark_text_secondary: Final[str] = "#B3B3B3"
    dark_accent: Final[str] = "#BB86FC"
    dark_accent_variant: Final[str] = "#3700B3"
    
    # === LIGHT MODE OPTIMIZED ===
    # Perfect for light theme applications
    light_background: Final[str] = "#FAFAFA"
    light_surface: Final[str] = "#FFFFFF"
    light_card: Final[str] = "#F5F5F5"
    light_border: Final[str] = "#E0E0E0"
    light_text_primary: Final[str] = "#212121"
    light_text_secondary: Final[str] = "#757575"
    light_accent: Final[str] = "#6200EE"
    light_accent_variant: Final[str] = "#3700B3"

class ColorPalettes:
    """
    13 expertly curated color combinations that work beautifully together.
    Perfect for creating cohesive UI themes. Hover colors are automatically
    generated from base colors to maintain consistency and reduce maintenance.
    
    Features themes for every use case:
    - Business/Corporate applications
    - Wellness & spa experiences  
    - Luxury & premium brands
    - Tech & futuristic interfaces
    - Sustainable & earthy designs
    - High-energy & vibrant apps
    - Vintage modern aesthetics
    - Monochromatic schemes
    """
    
    # Professional Business Theme
    corporate: Final[Dict[str, str]] = {
        "primary": ModernColors.navy_blue,                              # Color: #1976D2
        "primary_hover": create_hover_color(ModernColors.navy_blue),     # Color: Auto-generated hover
        "secondary": ModernColors.steel_blue,                           # Color: #455A64
        "accent": ModernColors.electric_blue,                           # Color: #00B4D8
        "background": ModernColors.ghost_white,                         # Color: #F8F9FA
        "surface": ModernColors.pure_white,                            # Color: #FFFFFF
        "text": ModernColors.charcoal,                                 # Color: #343A40
        "success": ModernColors.success_green,                         # Color: #28A745
        "success_hover": create_hover_color(ModernColors.success_green), # Color: Auto-generated hover
        "warning": ModernColors.warning_yellow,                        # Color: #FFC107
        "error": ModernColors.danger_red,                              # Color: #DC3545
        "disabled": ModernColors.medium_gray                           # Color: #ADB5BD (professional neutral)
    }
    
    # Modern Dark Theme
    dark_modern: Final[Dict[str, str]] = {
        "primary": ModernColors.electric_purple,                           # Color: #7C4DFF
        "primary_hover": create_hover_color(ModernColors.electric_purple), # Color: Auto-generated hover
        "secondary": ModernColors.dark_accent,                             # Color: #BB86FC
        "accent": ModernColors.cyan,                                       # Color: #00BCD4
        "background": ModernColors.dark_background,                        # Color: #121212
        "surface": ModernColors.dark_surface,                              # Color: #1E1E1E
        "text": ModernColors.dark_text_primary,                            # Color: #FFFFFF
        "success": ModernColors.emerald_green,                             # Color: #66BB6A
        "success_hover": create_hover_color(ModernColors.emerald_green),   # Color: Auto-generated hover
        "warning": ModernColors.amber,                                     # Color: #FFC107
        "error": ModernColors.hot_pink,                                    # Color: #E91E63
        "disabled": "#6C757D"                                              # Color: #6C757D (visible on dark backgrounds)
    }
    
    # Nature Inspired Theme
    nature: Final[Dict[str, str]] = {
        "primary": ModernColors.forest_green,                             # Color: #81C784
        "primary_hover": create_hover_color(ModernColors.forest_green),   # Color: Auto-generated hover
        "secondary": ModernColors.sage_green,                             # Color: #C8E6C9
        "accent": ModernColors.lime_green,                                # Color: #A5D6A7
        "background": ModernColors.mint_green,                            # Color: #E8F5E8
        "surface": ModernColors.pure_white,                               # Color: #FFFFFF
        "text": ModernColors.dark_green,                                  # Color: #2E7D32
        "success": ModernColors.jade_green,                               # Color: #4CAF50
        "success_hover": create_hover_color(ModernColors.jade_green),     # Color: Auto-generated hover
        "warning": ModernColors.honey,                                    # Color: #FFB300
        "error": ModernColors.tomato_red,                                 # Color: #EF5350
        "disabled": "#8D9A8D"                                             # Color: #8D9A8D (muted green-gray for nature theme)
    }
    
    # Creative/Design Theme
    creative: Final[Dict[str, str]] = {
        "primary": ModernColors.royal_purple,                             # Color: #9C27B0
        "primary_hover": create_hover_color(ModernColors.royal_purple),   # Color: Auto-generated hover
        "secondary": ModernColors.amethyst,                               # Color: #BA68C8
        "accent": ModernColors.hot_pink,                                  # Color: #E91E63
        "background": ModernColors.lavender,                              # Color: #F3E5F5
        "surface": ModernColors.pure_white,                               # Color: #FFFFFF
        "text": ModernColors.midnight_purple,                             # Color: #4527A0
        "success": ModernColors.turquoise,                                # Color: #1DE9B6
        "success_hover": create_hover_color(ModernColors.turquoise),      # Color: Auto-generated hover
        "warning": ModernColors.gold,                                     # Color: #FFD54F
        "error": ModernColors.magenta,                                    # Color: #FF1744
        "disabled": "#B39DDB"                                             # Color: #B39DDB (muted purple for creative theme)
    }
    
    # Minimalist Theme
    minimalist: Final[Dict[str, str]] = {
        "primary": ModernColors.charcoal,                                 # Color: #343A40
        "primary_hover": create_hover_color(ModernColors.charcoal),       # Color: Auto-generated hover
        "secondary": ModernColors.medium_gray,                            # Color: #ADB5BD
        "accent": ModernColors.royal_blue,                                # Color: #2196F3
        "background": ModernColors.ghost_white,                           # Color: #F8F9FA
        "surface": ModernColors.pure_white,                               # Color: #FFFFFF
        "text": ModernColors.space_gray,                                  # Color: #212529
        "success": ModernColors.pine_green,                               # Color: #43A047
        "success_hover": create_hover_color(ModernColors.pine_green),     # Color: Auto-generated hover
        "warning": ModernColors.burnt_orange,                             # Color: #F57C00
        "error": ModernColors.cherry_red,                                 # Color: #E53935
        "disabled": ModernColors.slate_gray                               # Color: #6C757D (clean neutral for minimalist)
    }
    
    # === 2025 TRENDING PALETTES ===
    # Based on current design trends and color research
    
    # Wellness & Spa Theme
    wellness: Final[Dict[str, str]] = {
        "primary": ModernColors.sage_blue,                                # Color: #8FBC8F
        "primary_hover": create_hover_color(ModernColors.sage_blue),      # Color: Auto-generated hover
        "secondary": ModernColors.cream_mint,                             # Color: #F0FFF0
        "accent": ModernColors.digital_lavender,                          # Color: #A78BFA
        "background": ModernColors.ethereal_blue,                         # Color: #B6E5FF
        "surface": ModernColors.pure_white,                               # Color: #FFFFFF
        "text": ModernColors.dark_green,                                  # Color: #2E7D32
        "success": ModernColors.emerald_green,                            # Color: #66BB6A
        "success_hover": create_hover_color(ModernColors.emerald_green),  # Color: Auto-generated hover
        "warning": ModernColors.canary_yellow,                            # Color: #FFD700
        "error": ModernColors.muted_rose,                                 # Color: #D4A5A5
        "disabled": "#B0C4B0"                                             # Color: #B0C4B0 (soft sage-gray for wellness)
    }
    
    # Luxury & Premium Theme
    luxury: Final[Dict[str, str]] = {
        "primary": ModernColors.midnight_black,                           # Color: #000000
        "primary_hover": "#1A1A1A",                                       # Color: #1A1A1A (special case for black)
        "secondary": ModernColors.gunmetal_gray,                          # Color: #2C3539
        "accent": ModernColors.champagne_gold,                            # Color: #F7E7CE
        "background": ModernColors.charcoal,                              # Color: #343A40
        "surface": ModernColors.dark_gray,                                # Color: #495057
        "text": ModernColors.platinum,                                    # Color: #E5E4E2
        "success": ModernColors.emerald_green,                            # Color: #66BB6A
        "success_hover": create_hover_color(ModernColors.emerald_green),  # Color: #4CAF50 (darker emerald)
        "warning": ModernColors.gold,                                     # Color: #FFD54F
        "error": ModernColors.deep_ruby,                                  # Color: #8B0000
        "disabled": "#808080"                                             # Color: #808080 (sophisticated platinum-gray)
    }
    
    # Tech & Futuristic Theme
    tech_future: Final[Dict[str, str]] = {
        "primary": ModernColors.electric_purple,                          # Color: #7C4DFF
        "primary_hover": create_hover_color(ModernColors.electric_purple), # Color: Auto-generated hover
        "secondary": ModernColors.gunmetal_gray,                          # Color: #2C3539
        "accent": ModernColors.chrome_silver,                             # Color: #C0C0C0
        "background": ModernColors.space_gray,                            # Color: #212529
        "surface": ModernColors.dark_surface,                             # Color: #1E1E1E
        "text": ModernColors.platinum,                                    # Color: #E5E4E2
        "success": ModernColors.jade_green,                               # Color: #4CAF50 (using jade_green instead of hard-coded)
        "success_hover": create_hover_color(ModernColors.jade_green),     # Color: Auto-generated hover
        "warning": ModernColors.canary_yellow,                            # Color: #FFD700
        "error": ModernColors.hot_pink,                                   # Color: #E91E63
        "disabled": "#5A6A72"                                             # Color: #5A6A72 (cool metallic gray for tech)
    }
    
    # Earthy & Sustainable Theme  
    earthy_sustainable: Final[Dict[str, str]] = {
        "primary": ModernColors.mocha_mousse,                             # Color: #A47864
        "primary_hover": create_hover_color(ModernColors.mocha_mousse),   # Color: Auto-generated hover
        "secondary": ModernColors.terracotta_clay,                        # Color: #C99383
        "accent": ModernColors.sage_green,                                # Color: #C8E6C9
        "background": ModernColors.cream,                                 # Color: #FFF8E1
        "surface": ModernColors.champagne,                                # Color: #FFECB3
        "text": ModernColors.dark_green,                                  # Color: #2E7D32
        "success": ModernColors.forest_green,                             # Color: #81C784
        "success_hover": create_hover_color(ModernColors.forest_green),   # Color: Auto-generated hover
        "warning": ModernColors.burnt_sienna,                             # Color: #CC5500
        "error": ModernColors.brick_red,                                  # Color: #8D1E1E
        "disabled": "#A0958A"                                             # Color: #A0958A (warm earth-tone gray)
    }
    
    # Vibrant & Energetic Theme
    vibrant_energy: Final[Dict[str, str]] = {
        "primary": ModernColors.electric_blue,                            # Color: #00B4D8
        "primary_hover": create_hover_color(ModernColors.electric_blue),  # Color: Auto-generated hover
        "secondary": ModernColors.hot_pink,                               # Color: #E91E63
        "accent": ModernColors.canary_yellow,                             # Color: #FFD700
        "background": ModernColors.ghost_white,                           # Color: #F8F9FA
        "surface": ModernColors.pure_white,                               # Color: #FFFFFF
        "text": ModernColors.charcoal,                                    # Color: #343A40
        "success": ModernColors.lime,                                     # Color: #76FF03
        "success_hover": create_hover_color(ModernColors.lime),           # Color: Auto-generated hover
        "warning": ModernColors.tangerine,                                # Color: #FF6F00
        "error": ModernColors.magenta,                                    # Color: #FF1744
        "disabled": "#9E9E9E"                                             # Color: #9E9E9E (neutral but still energetic)
    }
    
    # Vintage Modern Theme
    vintage_modern: Final[Dict[str, str]] = {
        "primary": ModernColors.burnt_sienna,                             # Color: #CC5500
        "primary_hover": create_hover_color(ModernColors.burnt_sienna),   # Color: Auto-generated hover
        "secondary": ModernColors.dusty_pink,                             # Color: #DCC0C6
        "accent": ModernColors.mustard_yellow,                            # Color: #FFDB58
        "background": ModernColors.cream_peach,                           # Color: #FFEBE9
        "surface": ModernColors.cream,                                    # Color: #FFF8E1
        "text": ModernColors.dark_gray,                                   # Color: #495057
        "success": ModernColors.sage_green,                               # Color: #C8E6C9
        "success_hover": create_hover_color(ModernColors.sage_green),     # Color: Auto-generated hover
        "warning": ModernColors.amber,                                    # Color: #FFC107
        "error": ModernColors.burgundy,                                   # Color: #C62828
        "disabled": "#C4A48A"                                             # Color: #C4A48A (warm vintage beige-gray)
    }
    
    # Monochromatic Blue Theme
    mono_blue: Final[Dict[str, str]] = {
        "primary": ModernColors.royal_blue,                               # Color: #2196F3
        "primary_hover": create_hover_color(ModernColors.royal_blue),     # Color: Auto-generated hover
        "secondary": ModernColors.sky_blue,                               # Color: #BBDEFB
        "accent": ModernColors.navy_blue,                                 # Color: #1976D2
        "background": ModernColors.ice_blue,                              # Color: #E3F2FD
        "surface": ModernColors.cornflower_blue,                          # Color: #90CAF9
        "text": ModernColors.midnight_blue,                               # Color: #1565C0
        "success": ModernColors.ocean_blue,                               # Color: #64B5F6
        "success_hover": create_hover_color(ModernColors.ocean_blue),     # Color: Auto-generated hover
        "warning": ModernColors.steel_blue,                               # Color: #455A64
        "error": ModernColors.deep_blue,                                  # Color: #0D47A1
        "disabled": "#9E9E9E"                                             # Color: #9E9E9E (neutral blue-gray for mono theme)
    }
    
    # Monochromatic Green Theme
    mono_green: Final[Dict[str, str]] = {
        "primary": ModernColors.jade_green,                               # Color: #4CAF50
        "primary_hover": create_hover_color(ModernColors.jade_green),     # Color: Auto-generated hover
        "secondary": ModernColors.sage_green,                             # Color: #C8E6C9
        "accent": ModernColors.pine_green,                                # Color: #43A047
        "background": ModernColors.mint_green,                            # Color: #E8F5E8
        "surface": ModernColors.lime_green,                               # Color: #A5D6A7
        "text": ModernColors.deep_forest,                                 # Color: #1B5E20
        "success": ModernColors.emerald_green,                            # Color: #66BB6A
        "success_hover": create_hover_color(ModernColors.emerald_green),  # Color: Auto-generated hover
        "warning": ModernColors.forest_green,                             # Color: #81C784
        "error": ModernColors.dark_green,                                 # Color: #2E7D32
        "disabled": "#A8A8A8"                                             # Color: #A8A8A8 (muted green-gray for mono theme)
    }