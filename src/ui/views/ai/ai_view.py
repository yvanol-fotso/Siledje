"""
Vue de gestion des parametres IA - Interface utilisateur.
Herite de BaseView. Boutons = CustomButton, dialogues = InfoDialog (via manager).
Le style de base (QGroupBox, QLabel, couleurs) vient de BaseView / QSS global.
Seuls les éléments propres à cette vue (bannière, chips de valeur) sont stylés ici.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap

from src.ui.views.base.base_view import BaseView
from src.ui.views.base.palette import Palette
from src.ui.widgets.custom_button import primary_btn, outline_btn, CustomButton
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return QPixmap()
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else QPixmap()
    except Exception as e:
        print(f"Erreur icone {icon_name}: {e}")
        return QPixmap()


class AIView(BaseView):
    """Vue de gestion des parametres IA. Herite de BaseView."""

    edit_config_requested = Signal()
    test_connection_requested = Signal()
    reset_config_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Parametres de l'Assistant IA",
            icon_name="cpu"
        )

        self.status_label = None
        self.model_label = None
        self.temperature_label = None
        self.max_tokens_label = None
        self.context_label = None
        self.suggestions_label = None

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_info_banner()
        self._init_config_display()
        self._init_action_buttons()
        self._apply_local_styles()
        self._restyle_all_buttons()

    def _init_info_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("infoBanner")

        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setPixmap(load_svg_icon("cpu", size=24))

        text = QLabel(
            "L'assistant IA peut vous aider dans la gestion quotidienne de votre librairie : "
            "suggestions de commandes, analyses de ventes, optimisation du stock, et plus encore."
        )
        text.setObjectName("bannerText")
        text.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(text, 1)
        banner.setLayout(layout)
        self.content_layout.addWidget(banner)

        return banner

    def _init_config_display(self):
        group = QGroupBox("Configuration Actuelle")
        group.setObjectName("configGroup")

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(24, 24, 24, 24)

        def add_row(row, label_text):
            lbl = QLabel(label_text)
            lbl.setObjectName("configRowLabel")
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            val = QLabel("—")
            val.setObjectName("configRowValue")
            val.setFixedHeight(36)

            grid.addWidget(lbl, row, 0)
            grid.addWidget(val, row, 1)
            return val

        self.status_label = add_row(0, "Statut :")
        self.model_label = add_row(1, "Modele :")
        self.temperature_label = add_row(2, "Temperature :")
        self.max_tokens_label = add_row(3, "Max Tokens :")
        self.context_label = add_row(4, "Context Window :")
        self.suggestions_label = add_row(5, "Suggestions automatiques :")

        grid.setColumnMinimumWidth(0, 200)
        grid.setColumnStretch(1, 1)

        group.setLayout(grid)
        self.content_layout.addWidget(group)

    def _init_action_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(15)

        self.configure_btn = primary_btn("Configurer", "settings")
        self.configure_btn.clicked.connect(lambda: self.edit_config_requested.emit())

        self.test_btn = outline_btn("Tester la connexion", "cpu")
        self.test_btn.clicked.connect(lambda: self.test_connection_requested.emit())

        self.reset_btn = outline_btn("Reinitialiser", "refresh")
        self.reset_btn.clicked.connect(lambda: self.reset_config_requested.emit())

        for btn in (self.configure_btn, self.test_btn, self.reset_btn):
            btn.setMinimumHeight(48)
            btn.setMinimumWidth(180)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(self.configure_btn)
        layout.addWidget(self.test_btn)
        layout.addStretch()
        layout.addWidget(self.reset_btn)

        self.content_layout.addLayout(layout)

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme (BaseView pose deja le style generique)."""
        super().set_theme(is_dark)
        self._apply_local_styles()
        self._restyle_all_buttons()
        # Re-applique les couleurs actif/inactif du statut si deja affiche
        if self.status_label is not None:
            self._style_status_label(self.status_label.text() == "Actif")

    def _apply_local_styles(self):
        """Styles propres a AIView uniquement (pas deja geres par BaseView) :
        bannere d'info + chips des valeurs de config."""
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT

        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#infoBanner {{
                border-left: 5px solid {accent};
                border-radius: 8px;
                padding: 5px;
                background: {colors['bg']};
                border: 1px solid {colors['border']};
                border-left-width: 5px;
            }}
            QLabel#bannerText {{
                font-size: 14px;
                color: {colors['text']};
            }}
            QLabel#configRowLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QLabel#configRowValue {{
                font-size: 14px;
                padding: 6px 14px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                color: {colors['text']};
                background: transparent;
            }}
        """)

    def _style_status_label(self, is_active: bool):
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        color = Palette.SUCCESS if is_active else Palette.DANGER
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            padding: 6px 14px;
            border: 2px solid {color};
            border-radius: 6px;
            color: {color};
        """)

    # ========== API PUBLIQUE ==========

    def update_config_display(self, config):
        is_active = bool(config.enabled)
        self.status_label.setText("Actif" if is_active else "Desactive")
        self._style_status_label(is_active)

        self.model_label.setText(config.model)
        self.temperature_label.setText(str(config.temperature))
        self.max_tokens_label.setText(str(config.max_tokens))
        self.context_label.setText(f"{config.context_window} tokens")
        self.suggestions_label.setText("Oui" if config.auto_suggestions else "Non")