"""
Vue de gestion de la base de données - Interface utilisateur moderne.
Combine design élégant avec icônes SVG professionnelles.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    """Charge une icône SVG et la convertit en QPixmap."""
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
        print(f"Erreur chargement icône {icon_name}: {e}")
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    """Crée un placeholder visuel avec une lettre."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    painter.setBrush(QBrush(QColor("#27ae60")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    
    painter.end()
    
    return pixmap


def create_colored_icon(icon_name: str, bg_color: str, size: int = 48) -> QPixmap:
    """Crée une icône SVG avec fond coloré circulaire."""
    # Charger l'icône SVG
    svg_pixmap = load_svg_icon(icon_name, size // 2)
    
    # Créer le fond circulaire
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    
    painter = QPainter(result)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Dessiner le cercle de fond
    painter.setBrush(QBrush(QColor(bg_color)))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawEllipse(0, 0, size, size)
    
    # Centrer l'icône SVG
    icon_offset = (size - svg_pixmap.width()) // 2
    painter.drawPixmap(icon_offset, icon_offset, svg_pixmap)
    
    painter.end()
    
    return result


class StatCard(QFrame):
    """Carte de statistique moderne avec icône SVG."""
    
    def __init__(self, title: str, icon_name: str, icon_color: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.icon_name = icon_name
        self.icon_color = icon_color
        
        self.setObjectName("statCard")
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: palette(base);
                border: 2px solid palette(mid);
                border-radius: 12px;
                padding: 15px;
            }
            QFrame#statCard:hover {
                border: 2px solid #3498db;
                background-color: palette(alternate-base);
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface de la carte."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # En-tête avec icône SVG
        header_layout = QHBoxLayout()
        
        # Icône SVG avec fond coloré
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setPixmap(create_colored_icon(self.icon_name, self.icon_color, 48))
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: palette(text);
        """)
        title_label.setWordWrap(True)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label, 1)
        
        # Valeur (grande et en gras)
        self.value_label = QLabel("...")
        self.value_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: palette(text);
            margin-top: 10px;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
    
    def set_value(self, value: str):
        """Met à jour la valeur affichée."""
        self.value_label.setText(value)


class DatabaseSettingsView(QWidget):
    """
    Vue moderne de gestion de la base de données.
    Affiche les statistiques sous forme de cartes élégantes avec icônes SVG.
    """
    
    # Signaux
    optimize_requested = Signal()
    check_integrity_requested = Signal()
    backup_requested = Signal()
    refresh_stats_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Cartes de statistiques
        self.cards = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur moderne."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ========== EN-TÊTE ==========
        header = self._create_header()
        main_layout.addWidget(header)
        
        # ========== ZONE SCROLLABLE ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # Cartes de statistiques
        stats_grid = self._create_stats_cards()
        scroll_layout.addLayout(stats_grid)
        
        # Boutons d'action
        actions = self._create_action_buttons()
        scroll_layout.addLayout(actions)
        
        # Informations supplémentaires
        info_box = self._create_info_box()
        scroll_layout.addWidget(info_box)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def _create_header(self) -> QFrame:
        """Crée l'en-tête moderne avec icône SVG."""
        header = QFrame()
        header.setObjectName("header")
        header.setStyleSheet("""
            QFrame#header {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db,
                    stop:1 #2ecc71
                );
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Icône SVG principale
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        # Utiliser une icône SVG au lieu d'un placeholder
        icon_pixmap = load_svg_icon("database", size=60)
        if icon_pixmap.isNull():
            icon_pixmap = load_svg_icon("settings", size=60)
        icon_label.setPixmap(icon_pixmap)
        
        # Titre et sous-titre
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title = QLabel("Gestion de la Base de Données")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
        """)
        
        subtitle = QLabel("Optimisez, vérifiez et sauvegardez vos données")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
        """)
        
        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)
        
        return header
    
    def _create_stats_cards(self) -> QGridLayout:
        """Crée la grille de cartes de statistiques avec icônes SVG."""
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Configuration des cartes (titre, icône SVG, couleur)
        cards_config = [
            ("file_size", "Taille du fichier", "file", "#e74c3c"),
            ("products", "Produits", "package", "#3498db"),
            ("barcodes", "Codes-barres", "barcode", "#9b59b6"),
            ("sales", "Ventes", "shopping-cart", "#2ecc71"),
            ("users", "Utilisateurs", "users", "#f39c12"),
            ("pages", "Pages BDD", "database", "#1abc9c"),
        ]
        
        # Créer les cartes en grille 3x2
        row, col = 0, 0
        for key, title, icon_name, color in cards_config:
            card = StatCard(title, icon_name, color)
            self.cards[key] = card
            grid.addWidget(card, row, col)
            
            col += 1
            if col >= 3:  # 3 colonnes
                col = 0
                row += 1
        
        return grid
    
    def _create_action_buttons(self) -> QVBoxLayout:
        """Crée les boutons d'action avec icônes SVG."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Titre de section
        section_title = QLabel("Actions de maintenance")
        section_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: palette(text);
            margin-top: 10px;
        """)
        layout.addWidget(section_title)
        
        # Grille de boutons
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)
        
        # Configuration des boutons (texte, icône SVG, couleur)
        buttons_config = [
            ("Optimiser la BDD", "refresh", "#3498db", self.optimize_requested),
            ("Vérifier l'intégrité", "shield", "#2ecc71", self.check_integrity_requested),
            ("Créer une sauvegarde", "package", "#e67e22", self.backup_requested),
            ("Actualiser les stats", "refresh", "#95a5a6", self.refresh_stats_requested),
        ]
        
        row, col = 0, 0
        for text, icon_name, color, signal in buttons_config:
            btn = self._create_action_button(text, icon_name, color, signal)
            buttons_grid.addWidget(btn, row, col)
            
            col += 1
            if col >= 2:  # 2 colonnes
                col = 0
                row += 1
        
        layout.addLayout(buttons_grid)
        
        return layout
    
    def _create_action_button(self, text: str, icon_name: str, color: str, signal: Signal) -> QPushButton:
        """Crée un bouton d'action avec icône SVG."""
        btn = QPushButton(text)
        btn.setMinimumHeight(55)
        btn.setMinimumWidth(180)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Icône SVG
        icon_pixmap = load_svg_icon(icon_name, size=20)
        btn.setIcon(QIcon(icon_pixmap))
        btn.setIconSize(QSize(20, 20))
        
        # Calculer les couleurs hover/pressed
        hover_color = self._darken_color(color, 0.8)
        pressed_color = self._darken_color(color, 0.6)
        
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
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)
        
        btn.clicked.connect(signal.emit)
        
        return btn
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Assombrit une couleur hexadécimale."""
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        color.setHsv(h, s, int(v * factor), a)
        return color.name()
    
    def _create_info_box(self) -> QFrame:
        """Crée une boîte d'informations sans emojis."""
        info_box = QFrame()
        info_box.setObjectName("infoBox")
        info_box.setStyleSheet("""
            QFrame#infoBox {
                background-color: #e8f4f8;
                border-left: 4px solid #3498db;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(info_box)
        layout.setSpacing(15)
        
        # Icône SVG d'information
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("info", size=32))
        
        # Texte layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        # Titre
        title = QLabel("Conseils de maintenance")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        # Conseils
        tips = QLabel(
            "- Optimisez régulièrement votre base de données pour maintenir les performances\n"
            "- Créez des sauvegardes avant toute opération importante\n"
            "- Vérifiez l'intégrité en cas de comportement anormal\n"
            "- Les statistiques se mettent à jour automatiquement"
        )
        tips.setStyleSheet("""
            font-size: 13px;
            color: #34495e;
            line-height: 1.6;
        """)
        tips.setWordWrap(True)
        
        text_layout.addWidget(title)
        text_layout.addWidget(tips)
        
        layout.addWidget(icon_label)
        layout.addLayout(text_layout, 1)
        
        return info_box
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def update_stats_display(self, stats):
        """Met à jour l'affichage des statistiques sur les cartes."""
        # Taille du fichier
        self.cards['file_size'].set_value(f"{stats['file_size']:.2f} MB")
        
        # Produits
        self.cards['products'].set_value(str(stats['total_products']))
        
        # Codes-barres
        self.cards['barcodes'].set_value(str(stats['total_barcodes']))
        
        # Ventes
        self.cards['sales'].set_value(str(stats['total_sales']))
        
        # Utilisateurs
        self.cards['users'].set_value(str(stats['total_users']))
        
        # Pages
        self.cards['pages'].set_value(f"{stats['page_count']}")
        
        print("[DatabaseSettingsView] Statistiques mises à jour")