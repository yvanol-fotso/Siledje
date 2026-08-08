"""
Palette centralisée - Support Light et Dark.
Une seule source de vérité pour toutes les couleurs.
"""


class Palette:
    """Palette centralisee - Support Light et Dark"""
    
    # Couleurs principales
    ACCENT = "#567ba1"
    ACCENT_HOVER = "#46648a"
    ACCENT_PRESSED = "#3a5470"
    SELECTION = "#7895b4"
    ROW_HOVER = "rgba(86, 123, 161, 0.10)"
    BORDER_GRAY = "#bdc3c7"
    MUTED_TEXT = "#8a9199"
    
    # ✅ Couleurs pour les boutons - AVEC HOVER ET PRESSED
    SUCCESS = "#2ecc71"
    SUCCESS_HOVER = "#27ae60"
    SUCCESS_PRESSED = "#1e8449"
    
    DANGER = "#e74c3c"
    DANGER_HOVER = "#c0392b"
    DANGER_PRESSED = "#a93226"
    
    WARNING = "#f39c12"
    WARNING_HOVER = "#e67e22"
    WARNING_PRESSED = "#d35400"
    
    INFO = "#3498db"
    INFO_HOVER = "#2980b9"
    INFO_PRESSED = "#21618c"
    
    PURPLE = "#9b59b6"
    PURPLE_HOVER = "#8e44ad"
    PURPLE_PRESSED = "#7d3c98"
    
    TEAL = "#1abc9c"
    TEAL_HOVER = "#16a085"
    TEAL_PRESSED = "#0e8070"
    
    # Couleurs pour les graphiques
    CHART_BLUE = "#567ba1"
    CHART_GREEN = "#2ecc71"
    CHART_RED = "#e74c3c"
    CHART_PURPLE = "#9b59b6"
    CHART_ORANGE = "#f39c12"
    CHART_GRAY = "#95a5a6"
    
    # Mode Light
    LIGHT_BG = "#ffffff"
    LIGHT_TEXT = "#2c3e50"
    LIGHT_BORDER = "#bdc3c7"
    LIGHT_HOVER = "rgba(86, 123, 161, 0.10)"
    LIGHT_SCROLLBAR_BG = "#d5d8dc"
    LIGHT_SCROLLBAR_HANDLE = "#aab7b8"
    LIGHT_SCROLLBAR_HOVER = "#95a5a6"
    
    # Mode Dark
    # DARK_BG = "#1e1e2e"
    DARK_BG = "#2c3e50"
    DARK_TEXT = "#e0e0e0"
    DARK_BORDER = "#4a6a8a"
    DARK_HOVER = "rgba(86, 123, 161, 0.20)"
    DARK_ROW_HOVER = "rgba(86, 123, 161, 0.20)"
    DARK_SELECTION = "#4a6a8a"
    DARK_HEADER = "#4a6a8a"
    DARK_SCROLLBAR_BG = "#4a6a8a"
    DARK_SCROLLBAR_HANDLE = "#4a6a8a"
    DARK_SCROLLBAR_HOVER = "#4a6a8a"
    
    # Commun
    SCROLLBAR_BG = "#d5d8dc"
    SCROLLBAR_HANDLE = "#aab7b8"
    SCROLLBAR_HOVER = "#95a5a6"
    BASE_WHITE = "#ffffff"
    
    @classmethod
    def get_theme_colors(cls, is_dark: bool = False):
        """Retourne les couleurs selon le theme"""
        if is_dark:
            return {
                'bg': cls.DARK_BG,
                'text': cls.DARK_TEXT,
                'border': cls.DARK_BORDER,
                'hover': cls.DARK_HOVER,
                'scrollbar_bg': cls.DARK_SCROLLBAR_BG,
                'scrollbar_handle': cls.DARK_SCROLLBAR_HANDLE,
                'scrollbar_hover': cls.DARK_SCROLLBAR_HOVER,
            }
        return {
            'bg': cls.LIGHT_BG,
            'text': cls.LIGHT_TEXT,
            'border': cls.LIGHT_BORDER,
            'hover': cls.LIGHT_HOVER,
            'scrollbar_bg': cls.LIGHT_SCROLLBAR_BG,
            'scrollbar_handle': cls.LIGHT_SCROLLBAR_HANDLE,
            'scrollbar_hover': cls.LIGHT_SCROLLBAR_HOVER,
        }