"""
Vue de gestion de la base de données - Interface utilisateur moderne.
Combine design élégant avec icônes SVG professionnelles.
Support complet Dark/Light — aucune couleur de fond forcée.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        if pixmap.isNull():
            return create_placeholder_pixmap(size, icon_name[0].upper())
        return pixmap
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#27ae60")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


def create_colored_icon(icon_name: str, bg_color: str, size: int = 48) -> QPixmap:
    svg_pixmap = load_svg_icon(icon_name, size // 2)
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(bg_color)))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawEllipse(0, 0, size, size)
    icon_offset = (size - svg_pixmap.width()) // 2
    painter.drawPixmap(icon_offset, icon_offset, svg_pixmap)
    painter.end()
    return result


class StatCard(QFrame):
    """Carte de statistique — s'adapte Dark/Light automatiquement."""

    def __init__(self, title: str, icon_name: str, icon_color: str, parent=None):
        super().__init__(parent)
        self.title      = title
        self.icon_name  = icon_name
        self.icon_color = icon_color

        self.setObjectName("statCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame#statCard {
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
            QFrame#statCard:hover {
                border: 2px solid #3498db;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        header_layout = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setPixmap(create_colored_icon(self.icon_name, self.icon_color, 48))

        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        title_label.setWordWrap(True)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)

        self.value_label = QLabel("...")
        self.value_label.setStyleSheet("font-size: 32px; font-weight: bold; margin-top: 10px;")
        self.value_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def set_value(self, value: str):
        self.value_label.setText(value)


class DatabaseSettingsView(QWidget):
    """Vue moderne de gestion de la base de données. Dark/Light automatique."""

    optimize_requested       = Signal()
    check_integrity_requested = Signal()
    backup_requested         = Signal()
    refresh_stats_requested  = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.cards  = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        main_layout.addWidget(self._create_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Fond transparent — hérite du thème dark/light
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 12px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60; min-height: 20px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #2ecc71; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        scroll.viewport().setAutoFillBackground(False)

        scroll_content = QWidget()
        scroll_content.setAutoFillBackground(False)
        scroll_layout  = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        scroll_layout.addLayout(self._create_stats_cards())
        scroll_layout.addLayout(self._create_action_buttons())
        scroll_layout.addWidget(self._create_info_box())
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE gradient — conservé tel quel (fond coloré explicite ok)
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("dbHeader")
        header.setStyleSheet("""
            QFrame#dbHeader {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2ecc71
                );
                border-radius: 12px;
            }
        """)

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

        title = QLabel("Gestion de la Base de Données")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")

        subtitle = QLabel("Optimisez, vérifiez et sauvegardez vos données")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9);")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)

        return header

    # ──────────────────────────────────────────────────────────────────
    # CARTES STATS
    # ──────────────────────────────────────────────────────────────────

    def _create_stats_cards(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(15)

        cards_config = [
            ("file_size", "Taille du fichier",  "file",          "#e74c3c"),
            ("products",  "Produits",            "package",       "#3498db"),
            ("barcodes",  "Codes-barres",        "barcode",       "#9b59b6"),
            ("sales",     "Ventes",              "shopping-cart", "#2ecc71"),
            ("users",     "Utilisateurs",        "users",         "#f39c12"),
            ("pages",     "Pages BDD",           "database",      "#1abc9c"),
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

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION
    # ──────────────────────────────────────────────────────────────────

    def _create_action_buttons(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(15)

        section_title = QLabel("Actions de maintenance")
        section_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(section_title)

        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)

        buttons_config = [
            ("Optimiser la BDD",      "refresh", "#3498db", self.optimize_requested),
            ("Vérifier l'intégrité",  "shield",  "#2ecc71", self.check_integrity_requested),
            ("Créer une sauvegarde",  "package", "#e67e22", self.backup_requested),
            ("Actualiser les stats",  "refresh", "#95a5a6", self.refresh_stats_requested),
        ]

        row, col = 0, 0
        for text, icon_name, color, signal in buttons_config:
            btn = self._create_action_button(text, icon_name, color, signal)
            buttons_grid.addWidget(btn, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        layout.addLayout(buttons_grid)
        return layout

    def _create_action_button(self, text: str, icon_name: str, color: str, signal: Signal) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(55)
        btn.setMinimumWidth(180)
        btn.setCursor(Qt.PointingHandCursor)

        px = load_svg_icon(icon_name, size=20)
        btn.setIcon(QIcon(px))
        btn.setIconSize(QSize(20, 20))

        hover   = self._darken_color(color, 0.8)
        pressed = self._darken_color(color, 0.6)

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
                text-align: left;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """)

        btn.clicked.connect(signal.emit)
        return btn

    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        color.setHsv(h, s, int(v * factor), a)
        return color.name()

    # ──────────────────────────────────────────────────────────────────
    # BOÎTE INFO — s'adapte Dark/Light
    # ──────────────────────────────────────────────────────────────────

    def _create_info_box(self) -> QFrame:
        info_box = QFrame()
        info_box.setObjectName("infoBox")
        # Pas de background blanc fixe — utilise palette
        info_box.setStyleSheet("""
            QFrame#infoBox {
                border-left: 4px solid #3498db;
                border-radius: 8px;
            }
        """)

        layout = QHBoxLayout(info_box)
        layout.setSpacing(15)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("info", size=32))

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title = QLabel("Conseils de maintenance")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        tips = QLabel(
            "— Optimisez régulièrement pour maintenir les performances\n"
            "— Créez des sauvegardes avant toute opération importante\n"
            "— Vérifiez l'intégrité en cas de comportement anormal\n"
            "— Les statistiques se mettent à jour automatiquement"
        )
        tips.setStyleSheet("font-size: 13px;")
        tips.setWordWrap(True)

        text_layout.addWidget(title)
        text_layout.addWidget(tips)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)

        return info_box

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES
    # ──────────────────────────────────────────────────────────────────

    def update_stats_display(self, stats):
        self.cards['file_size'].set_value(f"{stats['file_size']:.2f} MB")
        self.cards['products'].set_value(str(stats['total_products']))
        self.cards['barcodes'].set_value(str(stats['total_barcodes']))
        self.cards['sales'].set_value(str(stats['total_sales']))
        self.cards['users'].set_value(str(stats['total_users']))
        self.cards['pages'].set_value(str(stats['page_count']))
        print("[DatabaseSettingsView] Statistiques mises à jour")