"""
Boutons personnalisés avec styles prédéfinis.
Support complet Light/Dark via apply_theme().

Light  → primary/outline = ACCENT (bleu)
Dark   → primary/outline = TEAL (vert)  ← forcé, non écrasable par parent
"""

from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon


class CustomButton(QPushButton):
    """
    Bouton sémantique (primary, success, danger, outline…).
    Couleurs = Palette. Dark : primary/outline → TEAL.
    """

    def __init__(self, text: str = "", type: str = "primary",
                 icon_name: str = None, parent=None):
        super().__init__(text, parent)
        self._type = type
        self._icon_name = icon_name
        self._is_dark = False
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        # ObjectName unique → spécificité max (évite override parent)
        self.setObjectName(f"customBtn_{type}_{id(self)}")
        self._init_style()

    def apply_theme(self, is_dark: bool):
        """À appeler depuis la vue au set_theme(is_dark)."""
        self._is_dark = bool(is_dark)
        self._init_style()

    def _colors_for_type(self) -> dict:
        from src.ui.views.base.base_view import Palette

        is_dark = self._is_dark

        # Accent principal : TEAL en dark, ACCENT en light
        accent = Palette.TEAL if is_dark else Palette.ACCENT
        accent_hover = Palette.TEAL_HOVER if is_dark else Palette.ACCENT_HOVER
        accent_pressed = Palette.TEAL_PRESSED if is_dark else Palette.ACCENT_PRESSED

        styles = {
            "primary": {
                "bg": accent,
                "hover": accent_hover,
                "pressed": accent_pressed,
                "text": "white",
                "border": "none",
            },
            "success": {
                "bg": Palette.SUCCESS,
                "hover": Palette.SUCCESS_HOVER,
                "pressed": Palette.SUCCESS_PRESSED,
                "text": "white",
                "border": "none",
            },
            "warning": {
                "bg": Palette.WARNING,
                "hover": Palette.WARNING_HOVER,
                "pressed": Palette.WARNING_PRESSED,
                "text": "white",
                "border": "none",
            },
            "danger": {
                "bg": Palette.DANGER,
                "hover": Palette.DANGER_HOVER,
                "pressed": Palette.DANGER_PRESSED,
                "text": "white",
                "border": "none",
            },
            "info": {
                "bg": Palette.INFO,
                "hover": Palette.INFO_HOVER,
                "pressed": Palette.INFO_PRESSED,
                "text": "white",
                "border": "none",
            },
            "secondary": {
                "bg": "#95a5a6",
                "hover": "#7f8c8d",
                "pressed": "#6c7a7a",
                "text": "white",
                "border": "none",
            },
            "outline": {
                "bg": "transparent",
                "hover": (
                    "rgba(26, 188, 156, 0.15)" if is_dark else Palette.ROW_HOVER
                ),
                "pressed": (
                    "rgba(26, 188, 156, 0.25)" if is_dark else Palette.ROW_HOVER
                ),
                "text": accent,
                "border": f"2px solid {accent}",
            },
        }
        return styles.get(self._type, styles["primary"])

    def _init_style(self):
        from src.ui.views.base.base_view import Palette

        c = self._colors_for_type()
        disabled_bg = Palette.DARK_BORDER if self._is_dark else "#bdc3c7"
        disabled_text = "#7f8c8d"
        obj = self.objectName()

        # Sélecteur QPushButton#objectName → prioritaire sur tout CSS parent
        self.setStyleSheet(f"""
            QPushButton#{obj} {{
                background-color: {c['bg']};
                color: {c['text']};
                border: {c['border']};
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 16px;
                min-height: 36px;
            }}
            QPushButton#{obj}:hover {{
                background-color: {c['hover']};
            }}
            QPushButton#{obj}:pressed {{
                background-color: {c['pressed']};
            }}
            QPushButton#{obj}:disabled {{
                background-color: {disabled_bg};
                color: {disabled_text};
                border: none;
            }}
        """)

        if self._icon_name:
            self._set_icon(self._icon_name)

    def _set_icon(self, icon_name: str):
        try:
            from src.utils.helpers import get_asset_path
            icon_path = get_asset_path("icons", f"{icon_name}.svg")
            if icon_path.exists():
                self.setIcon(QIcon(str(icon_path)))
                self.setIconSize(QSize(16, 16))
        except Exception:
            pass

    def set_type(self, type: str):
        self._type = type
        self.setObjectName(f"customBtn_{type}_{id(self)}")
        self._init_style()

    def set_icon_name(self, icon_name: str):
        self._icon_name = icon_name
        self._set_icon(icon_name)


# ── Helpers de création ──────────────────────────────────────────

def primary_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "primary", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def success_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "success", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def warning_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "warning", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def danger_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "danger", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def info_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "info", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def secondary_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "secondary", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn


def outline_btn(text: str, icon: str = None, slot=None) -> CustomButton:
    btn = CustomButton(text, "outline", icon)
    if slot:
        btn.clicked.connect(slot)
    return btn