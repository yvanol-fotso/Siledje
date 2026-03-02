"""
Vue de gestion des paramètres IA - Interface utilisateur responsive.
Style identique aux autres vues : titre adaptatif dark/light, pas d'emojis.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _placeholder(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _placeholder(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else _placeholder(size, icon_name[0].upper())
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _placeholder(size, icon_name[0].upper())


def _placeholder(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#3498db")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class AIView(QWidget):
    """Vue de gestion des paramètres IA. Style adaptatif dark/light."""

    edit_config_requested    = Signal()
    test_connection_requested = Signal()
    reset_config_requested   = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.status_label      = None
        self.model_label       = None
        self.temperature_label = None
        self.max_tokens_label  = None
        self.context_label     = None
        self.suggestions_label = None

        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        main_layout.addLayout(self._create_header())
        main_layout.addWidget(self._create_info_banner())
        main_layout.addWidget(self._create_config_display())
        main_layout.addLayout(self._create_action_buttons())
        main_layout.addStretch()

        self.setLayout(main_layout)

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE — pas de couleur fixe → blanc dark / noir light auto
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("cpu", size=40))

        title = QLabel("Parametres de l'Assistant IA")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # BANNIERE INFO — pas de couleur fixe
    # ──────────────────────────────────────────────────────────────────

    def _create_info_banner(self) -> QFrame:
        banner = QFrame()
        banner.setObjectName("infoBanner")
        banner.setStyleSheet("""
            QFrame#infoBanner {
                border-left: 5px solid #3498db;
                border-radius: 8px;
                padding: 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setPixmap(load_svg_icon("cpu", size=24))

        text = QLabel(
            "L'assistant IA peut vous aider dans la gestion quotidienne de votre librairie : "
            "suggestions de commandes, analyses de ventes, optimisation du stock, et plus encore."
        )
        text.setStyleSheet("font-size: 14px;")
        text.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(text, 1)
        banner.setLayout(layout)
        return banner

    # ──────────────────────────────────────────────────────────────────
    # CONFIG — labels adaptatifs, valeurs avec hauteur suffisante
    # ──────────────────────────────────────────────────────────────────

    def _create_config_display(self) -> QGroupBox:
        group = QGroupBox("Configuration Actuelle")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 14px;
                color: #3498db;
                font-weight: bold;
            }
        """)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(24, 24, 24, 24)

        # Style label gauche — pas de couleur fixe
        lbl_s = "font-size: 14px; font-weight: bold;"

        # Style valeur droite — pas de couleur fixe, hauteur min garantie
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

        self.status_label      = add_row(0, "Statut :")
        self.model_label       = add_row(1, "Modele :")
        self.temperature_label = add_row(2, "Temperature :")
        self.max_tokens_label  = add_row(3, "Max Tokens :")
        self.context_label     = add_row(4, "Context Window :")
        self.suggestions_label = add_row(5, "Suggestions automatiques :")

        grid.setColumnMinimumWidth(0, 200)
        grid.setColumnStretch(1, 1)

        group.setLayout(grid)
        return group

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION
    # ──────────────────────────────────────────────────────────────────

    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(15)

        layout.addWidget(self._make_btn(
            "Configurer", "settings", "#3498db", "#2980b9", "#21618c", w=180,
            slot=lambda: self.edit_config_requested.emit()))
        layout.addWidget(self._make_btn(
            "Tester la connexion", "cpu", "#2ecc71", "#27ae60", "#1e8449", w=200,
            slot=lambda: self.test_connection_requested.emit()))
        layout.addStretch()
        layout.addWidget(self._make_btn(
            "Reinitialiser", "refresh", "#e74c3c", "#c0392b", "#a93226", w=180,
            slot=lambda: self.reset_config_requested.emit()))

        return layout

    # ──────────────────────────────────────────────────────────────────
    # HELPER BOUTON
    # ──────────────────────────────────────────────────────────────────

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

    # ──────────────────────────────────────────────────────────────────
    # METHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def update_config_display(self, config):
        """Met a jour l'affichage de la configuration. Sans emojis, adaptatif."""

        # ── Statut — couleur fonctionnelle uniquement sur le fond ─────
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