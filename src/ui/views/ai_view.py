"""
Vue de gestion des paramètres IA - Interface utilisateur responsive.
Utilise des icônes SVG au lieu d'emojis.
S'adapte aux modes Dark/Light.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QGridLayout, QFrame
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
    
    painter.setBrush(QBrush(QColor("#3498db")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    
    painter.end()
    
    return pixmap


class AIView(QWidget):
    """
    Vue de gestion des paramètres IA ultra-responsive.
    S'adapte automatiquement aux modes Dark/Light.
    """
    
    # Signaux pour communiquer avec le manager
    edit_config_requested = Signal()
    test_connection_requested = Signal()
    reset_config_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Labels pour afficher la configuration
        self.status_label = None
        self.model_label = None
        self.temperature_label = None
        self.max_tokens_label = None
        self.context_label = None
        self.suggestions_label = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur responsive."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Bannière d'information
        info_banner = self._create_info_banner()
        main_layout.addWidget(info_banner)
        
        # Configuration actuelle
        config_group = self._create_config_display()
        main_layout.addWidget(config_group)
        
        # Boutons d'action
        btn_layout = self._create_action_buttons()
        main_layout.addLayout(btn_layout)
        
        # Espaceur pour pousser le contenu vers le haut
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Icône + Titre
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("cpu", size=40))
        
        title = QLabel("Paramètres de l'Assistant IA")
        title.setObjectName("pageTitle")
        title.setStyleSheet("""
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: bold;
                color: palette(text);
            }
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        
        return layout
    
    def _create_info_banner(self) -> QFrame:
        """Crée une bannière d'information."""
        banner = QFrame()
        banner.setObjectName("infoBanner")
        banner.setStyleSheet("""
            QFrame#infoBanner {
                background-color: #e3f2fd;
                border-left: 5px solid #2196f3;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        banner_layout = QHBoxLayout()
        banner_layout.setSpacing(15)
        
        # Icône info
        info_icon = QLabel()
        info_icon.setFixedSize(24, 24)
        info_icon.setPixmap(load_svg_icon("cpu", size=24))
        
        # Texte
        info_text = QLabel(
            "L'assistant IA peut vous aider dans la gestion quotidienne de votre librairie : "
            "suggestions de commandes, analyses de ventes, optimisation du stock, et plus encore."
        )
        info_text.setStyleSheet("font-size: 14px; color: #1565c0;")
        info_text.setWordWrap(True)
        
        banner_layout.addWidget(info_icon)
        banner_layout.addWidget(info_text, 1)
        
        banner.setLayout(banner_layout)
        return banner
    
    def _create_config_display(self) -> QGroupBox:
        """Crée le groupe d'affichage de la configuration."""
        config_group = QGroupBox("Configuration Actuelle")
        config_group.setObjectName("configGroup")
        config_group.setStyleSheet("""
            QGroupBox#configGroup {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid palette(mid);
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                color: palette(text);
            }
            QGroupBox#configGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: palette(base);
            }
        """)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # Style pour les labels
        label_style = "font-weight: bold; font-size: 14px; color: palette(text);"
        value_style = """
            font-size: 14px; 
            color: palette(text); 
            padding: 10px; 
            background-color: palette(alternate-base);
            border-radius: 6px;
        """
        
        # Fonction helper
        def create_info_row(row, label_text, value_widget_name):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            
            value = QLabel("Non configuré")
            value.setStyleSheet(value_style)
            value.setWordWrap(True)
            
            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(value, row, 1)
            
            return value
        
        # Créer les lignes
        self.status_label = create_info_row(0, "Statut:", "status")
        self.model_label = create_info_row(1, "Modèle:", "model")
        self.temperature_label = create_info_row(2, "Temperature:", "temperature")
        self.max_tokens_label = create_info_row(3, "Max Tokens:", "max_tokens")
        self.context_label = create_info_row(4, "Context Window:", "context")
        self.suggestions_label = create_info_row(5, "Suggestions automatiques:", "suggestions")
        
        config_group.setLayout(grid_layout)
        return config_group
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Bouton Configurer
        config_btn = QPushButton("Configurer")
        config_btn.setMinimumHeight(50)
        config_btn.setMinimumWidth(180)
        config_btn.setCursor(Qt.PointingHandCursor)
        config_btn.setObjectName("configButton")
        
        config_icon = load_svg_icon("settings", size=20)
        config_btn.setIcon(QIcon(config_icon))
        config_btn.setIconSize(QSize(20, 20))
        
        config_btn.setStyleSheet("""
            QPushButton#configButton {
                background-color: #3498db;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#configButton:hover {
                background-color: #2980b9;
            }
            QPushButton#configButton:pressed {
                background-color: #21618c;
            }
        """)
        config_btn.clicked.connect(lambda: self.edit_config_requested.emit())
        
        # Bouton Tester
        test_btn = QPushButton("Tester la connexion")
        test_btn.setMinimumHeight(50)
        test_btn.setMinimumWidth(200)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setObjectName("testButton")
        
        test_icon = load_svg_icon("cpu", size=20)
        test_btn.setIcon(QIcon(test_icon))
        test_btn.setIconSize(QSize(20, 20))
        
        test_btn.setStyleSheet("""
            QPushButton#testButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#testButton:hover {
                background-color: #27ae60;
            }
            QPushButton#testButton:pressed {
                background-color: #1e8449;
            }
        """)
        test_btn.clicked.connect(lambda: self.test_connection_requested.emit())
        
        # Bouton Réinitialiser
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.setMinimumHeight(50)
        reset_btn.setMinimumWidth(180)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setObjectName("resetButton")
        
        reset_icon = load_svg_icon("refresh", size=20)
        reset_btn.setIcon(QIcon(reset_icon))
        reset_btn.setIconSize(QSize(20, 20))
        
        reset_btn.setStyleSheet("""
            QPushButton#resetButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#resetButton:hover {
                background-color: #c0392b;
            }
            QPushButton#resetButton:pressed {
                background-color: #a93226;
            }
        """)
        reset_btn.clicked.connect(lambda: self.reset_config_requested.emit())
        
        layout.addWidget(config_btn)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(reset_btn)
        
        return layout
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def update_config_display(self, config):
        """Met à jour l'affichage de la configuration."""
        # Statut
        if config.enabled:
            self.status_label.setText("✅ Activé")
            self.status_label.setStyleSheet(
                "font-size: 14px; color: #27ae60; padding: 10px; "
                "background-color: #d5f4e6; border-radius: 6px; font-weight: bold;"
            )
        else:
            self.status_label.setText("❌ Désactivé")
            self.status_label.setStyleSheet(
                "font-size: 14px; color: #e74c3c; padding: 10px; "
                "background-color: #fadbd8; border-radius: 6px; font-weight: bold;"
            )
        
        # Modèle
        self.model_label.setText(config.model)
        
        # Temperature
        self.temperature_label.setText(f"{config.temperature}")
        
        # Max Tokens
        self.max_tokens_label.setText(f"{config.max_tokens}")
        
        # Context Window
        self.context_label.setText(f"{config.context_window} tokens")
        
        # Suggestions
        suggestions_text = "Oui" if config.auto_suggestions else "Non"
        self.suggestions_label.setText(suggestions_text)