"""
Vue de gestion de la base de données - Interface utilisateur moderne.
Herite de BaseView pour une structure coherente.
Support complet Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont

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


class StatCard(QFrame):
    """Carte de statistique — s'adapte Dark/Light automatiquement."""

    def __init__(self, title: str, icon_name: str, icon_color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_name = icon_name
        self.icon_color = icon_color

        self.setObjectName("statCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setPixmap(self._create_colored_icon(48))

        title_label = QLabel(self.title)
        title_label.setObjectName("cardTitle")
        title_label.setWordWrap(True)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)

        self.value_label = QLabel("...")
        self.value_label.setObjectName("cardValue")
        self.value_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def _create_colored_icon(self, size: int = 48) -> QPixmap:
        svg_pixmap = load_svg_icon(self.icon_name, size // 2)
        result = QPixmap(size, size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.icon_color)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(0, 0, size, size)
        icon_offset = (size - svg_pixmap.width()) // 2
        painter.drawPixmap(icon_offset, icon_offset, svg_pixmap)
        painter.end()
        return result

    def set_value(self, value: str):
        self.value_label.setText(value)


class DatabaseSettingsView(BaseView):
    """Vue de gestion de la base de données. Herite de BaseView."""

    optimize_requested = Signal()
    check_integrity_requested = Signal()
    backup_requested = Signal()
    refresh_stats_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion de la Base de Donnees",
            icon_name="database"
        )

        self.cards = {}

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_header()
        self._init_scroll_content()
        self._apply_theme_styles()

    def _init_header(self):
        """En-tete avec gradient."""
        header = QFrame()
        header.setObjectName("dbHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        px = load_svg_icon("database", size=60)
        if px.isNull():
            px = load_svg_icon("settings", size=60)
        icon_label.setPixmap(px)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title = QLabel("Gestion de la Base de Donnees")
        title.setObjectName("headerTitle")

        subtitle = QLabel("Optimisez, verifiez et sauvegardez vos donnees")
        subtitle.setObjectName("headerSubtitle")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)

        self.content_layout.addWidget(header)

    def _init_scroll_content(self):
        """Contenu scrollable."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("scrollArea")

        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 12, 8, 12)

        content_layout.addLayout(self._create_stats_cards())
        content_layout.addLayout(self._create_action_buttons())
        content_layout.addWidget(self._create_info_box())
        content_layout.addStretch()

        scroll.setWidget(content)
        self.content_layout.addWidget(scroll, 1)

    def _create_stats_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(15)

        cards_config = [
            ("file_size", "Taille du fichier", "file", "#e74c3c"),
            ("products", "Produits", "package", "#3498db"),
            ("barcodes", "Codes-barres", "barcode", "#9b59b6"),
            ("sales", "Ventes", "shopping-cart", "#2ecc71"),
            ("users", "Utilisateurs", "users", "#f39c12"),
            ("pages", "Pages BDD", "database", "#1abc9c"),
        ]

        row, col = 0, 0
        for key, title, icon_name, color in cards_config:
            card = StatCard(title, icon_name, color)
            self.cards[key] = card
            grid.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        return grid

    def _create_action_buttons(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(15)

        section_title = QLabel("Actions de maintenance")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)

        buttons_config = [
            ("Optimiser la BDD", "refresh", "#3498db", self.optimize_requested),
            ("Verifier l'integrite", "shield", "#2ecc71", self.check_integrity_requested),
            ("Creer une sauvegarde", "package", "#e67e22", self.backup_requested),
            ("Actualiser les stats", "refresh", "#95a5a6", self.refresh_stats_requested),
        ]

        row, col = 0, 0
        for text, icon_name, color, signal in buttons_config:
            btn = self._make_action_button(text, icon_name, color, signal)
            buttons_grid.addWidget(btn, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        layout.addLayout(buttons_grid)
        return layout

    def _make_action_button(self, text: str, icon_name: str, color: str, signal: Signal) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(55)
        btn.setMinimumWidth(180)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("actionBtn")

        px = load_svg_icon(icon_name, size=20)
        btn.setIcon(QIcon(px))
        btn.setIconSize(QSize(20, 20))

        btn.clicked.connect(signal.emit)
        return btn

    def _create_info_box(self) -> QFrame:
        info_box = QFrame()
        info_box.setObjectName("infoBox")

        layout = QHBoxLayout(info_box)
        layout.setSpacing(15)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("info", size=32))

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title = QLabel("Conseils de maintenance")
        title.setObjectName("infoTitle")

        tips = QLabel(
            "- Optimisez regulierement pour maintenir les performances\n"
            "- Creez des sauvegardes avant toute operation importante\n"
            "- Verifiez l'integrite en cas de comportement anormal\n"
            "- Les statistiques se mettent a jour automatiquement"
        )
        tips.setObjectName("infoText")
        tips.setWordWrap(True)

        text_layout.addWidget(title)
        text_layout.addWidget(tips)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)

        return info_box

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
            info_bg = "#2d2d44"
            info_border = "#3d3d5c"
            card_border = "#3d3d5c"
        else:
            border = "#bdc3c7"
            bg = "#ffffff"
            text = "#2c3e50"
            info_bg = "#f8f9fa"
            info_border = "#bdc3c7"
            card_border = "#bdc3c7"

        # Style header (gardé avec gradient)
        self.setStyleSheet(self.styleSheet() + f"""
            QFrame#dbHeader {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71
                );
                border-radius: 12px;
            }}
            QLabel#headerTitle {{
                font-size: 26px;
                font-weight: bold;
                color: white;
            }}
            QLabel#headerSubtitle {{
                font-size: 14px;
                color: rgba(255,255,255,0.9);
            }}
            QLabel#sectionTitle {{
                font-size: 18px;
                font-weight: bold;
                color: {text};
            }}
            QScrollArea#scrollArea {{
                background: transparent;
                border: none;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QFrame#statCard {{
                border: 1px solid {card_border};
                border-radius: 12px;
                background: {bg};
            }}
            QFrame#statCard:hover {{
                border: 2px solid #3498db;
            }}
            QLabel#cardTitle {{
                font-size: 14px;
                font-weight: 600;
                color: {text};
            }}
            QLabel#cardValue {{
                font-size: 32px;
                font-weight: bold;
                color: {text};
                margin-top: 10px;
            }}
            QPushButton#actionBtn {{
                background-color: #3498db;
                color: white;
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
                text-align: left;
            }}
            QPushButton#actionBtn:hover {{
                background-color: #2980b9;
            }}
            QPushButton#actionBtn:pressed {{
                background-color: #21618c;
            }}
            QFrame#infoBox {{
                border-left: 4px solid #3498db;
                border-radius: 8px;
                background: {info_bg};
                border: 1px solid {info_border};
                border-left-width: 4px;
            }}
            QLabel#infoTitle {{
                font-size: 16px;
                font-weight: bold;
                color: {text};
            }}
            QLabel#infoText {{
                font-size: 13px;
                color: {text};
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #27ae60;
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #2ecc71;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    # ========== API PUBLIQUE ==========

    def update_stats_display(self, stats):
        """Met a jour l'affichage des cartes de statistiques."""
        self.cards['file_size'].set_value(f"{stats.get('file_size', 0):.2f} MB")
        self.cards['products'].set_value(str(stats.get('total_products', 0)))
        self.cards['barcodes'].set_value(str(stats.get('total_barcodes', 0)))
        self.cards['sales'].set_value(str(stats.get('total_sales', 0)))
        self.cards['users'].set_value(str(stats.get('total_users', 0)))
        self.cards['pages'].set_value(str(stats.get('total_tables', 0)))