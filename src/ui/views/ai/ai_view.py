"""
Vue de gestion des parametres IA - Interface utilisateur.
Herite de BaseView pour une structure coherente.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

from src.ui.views.base.base_view import BaseView, Palette
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

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_info_banner()
        self._init_config_display()
        self._init_action_buttons()
        self._apply_theme_styles()

    def _init_info_banner(self) -> QFrame:
        """Banniere d'information."""
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
        """Affichage de la configuration."""
        group = QGroupBox("Configuration Actuelle")
        group.setObjectName("configGroup")

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(24, 24, 24, 24)

        lbl_s = "font-size: 14px; font-weight: bold;"
        val_s = """
            font-size: 14px;
            padding: 6px 14px;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
        """

        def add_row(row, label_text):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(lbl_s)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            val = QLabel("—")
            val.setStyleSheet(val_s)
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
        """Boutons d'action."""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        layout.addWidget(self._make_btn(
            "Configurer", "settings", "#3498db", "#2980b9", "#21618c", w=180,
            slot=lambda: self.edit_config_requested.emit()
        ))

        layout.addWidget(self._make_btn(
            "Tester la connexion", "cpu", "#2ecc71", "#27ae60", "#1e8449", w=200,
            slot=lambda: self.test_connection_requested.emit()
        ))

        layout.addStretch()

        layout.addWidget(self._make_btn(
            "Reinitialiser", "refresh", "#e74c3c", "#c0392b", "#a93226", w=180,
            slot=lambda: self.reset_config_requested.emit()
        ))

        self.content_layout.addLayout(layout)

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(48)
        if w:
            btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon(icon_name, size=18)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(18, 18))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: #95a5a6; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme."""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
        if self._is_dark:
            border = "#3d3d5c"
            bg = "#2d2d44"
            text = "#e0e0e0"
            banner_bg = "#2d2d44"
            banner_border = "#3d3d5c"
            note_bg = "#2d2d44"
            note_border = "#567ba1"
        else:
            border = "#bdc3c7"
            bg = "#ffffff"
            text = "#2c3e50"
            banner_bg = "#f8f9fa"
            banner_border = "#bdc3c7"
            note_bg = "#f8f9fa"
            note_border = "#3498db"

        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#infoBanner {{
                border-left: 5px solid #3498db;
                border-radius: 8px;
                padding: 5px;
                background: {banner_bg};
                border: 1px solid {banner_border};
                border-left-width: 5px;
            }}
            QLabel#bannerText {{
                font-size: 14px;
                color: {text};
            }}
            QGroupBox#configGroup {{
                font-size: 15px;
                font-weight: bold;
                border: 2px solid {border};
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
                color: {text};
            }}
            QGroupBox#configGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                color: #3498db;
                font-weight: bold;
            }}
        """)

    # ========== API PUBLIQUE ==========

    def update_config_display(self, config):
        """Met a jour l'affichage de la configuration."""
        from src.ui.views.ai.ai_config import AIConfig

        if config.enabled:
            self.status_label.setText("Actif")
            self.status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: 2px solid #27ae60;
                border-radius: 6px;
                color: #27ae60;
            """)
        else:
            self.status_label.setText("Desactive")
            self.status_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                padding: 6px 14px;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                color: #e74c3c;
            """)

        val_s = """
            font-size: 14px;
            padding: 6px 14px;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
        """

        self.model_label.setText(config.model)
        self.model_label.setStyleSheet(val_s)

        self.temperature_label.setText(str(config.temperature))
        self.temperature_label.setStyleSheet(val_s)

        self.max_tokens_label.setText(str(config.max_tokens))
        self.max_tokens_label.setStyleSheet(val_s)

        self.context_label.setText(f"{config.context_window} tokens")
        self.context_label.setStyleSheet(val_s)

        self.suggestions_label.setText("Oui" if config.auto_suggestions else "Non")
        self.suggestions_label.setStyleSheet(val_s)