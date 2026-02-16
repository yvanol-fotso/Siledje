"""
Vue de gestion des notifications - Interface utilisateur responsive.
Permet de configurer tous les paramètres de notifications.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QCheckBox, QSpinBox, QFormLayout
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
    
    painter.setBrush(QBrush(QColor("#9b59b6")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    
    painter.end()
    
    return pixmap


class NotificationSettingsView(QWidget):
    """
    Vue de gestion des notifications.
    Permet de configurer l'affichage et les types de notifications.
    """
    
    # Signaux pour communiquer avec le manager
    save_requested = Signal(dict)
    test_requested = Signal()
    reset_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Checkboxes de configuration
        self.enabled_check = None
        self.desktop_check = None
        self.sound_check = None
        self.tray_check = None
        self.duration_spin = None
        
        # Checkboxes des types
        self.stock_low_check = None
        self.sales_check = None
        self.errors_check = None
        self.warnings_check = None
        self.info_check = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur responsive."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Options générales
        general_group = self._create_general_options()
        main_layout.addWidget(general_group)
        
        # Types de notifications
        types_group = self._create_types_options()
        main_layout.addWidget(types_group)
        
        # Boutons d'action
        actions_layout = self._create_actions()
        main_layout.addLayout(actions_layout)
        
        # Espaceur
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Icône + Titre
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("settings", size=40))
        
        title = QLabel("Gestion des notifications")
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
    
    def _create_general_options(self) -> QGroupBox:
        """Crée le groupe d'options générales."""
        group = QGroupBox("Options générales")
        group.setObjectName("generalGroup")
        group.setStyleSheet("""
            QGroupBox#generalGroup {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid palette(mid);
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                color: palette(text);
            }
            QGroupBox#generalGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: palette(base);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: palette(text);
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """
        
        # Activer les notifications
        self.enabled_check = QCheckBox("Activer les notifications")
        self.enabled_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.enabled_check)
        
        # Afficher sur le bureau
        self.desktop_check = QCheckBox("Afficher les notifications sur le bureau")
        self.desktop_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.desktop_check)
        
        # Jouer un son
        self.sound_check = QCheckBox("Jouer un son")
        self.sound_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.sound_check)
        
        # Afficher dans la barre système
        self.tray_check = QCheckBox("Afficher dans la barre système")
        self.tray_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.tray_check)
        
        # Durée d'affichage
        duration_layout = QFormLayout()
        duration_layout.setSpacing(10)
        
        duration_label = QLabel("Durée d'affichage (secondes):")
        duration_label.setStyleSheet("font-size: 14px; color: palette(text); font-weight: bold;")
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 30)
        self.duration_spin.setValue(5)
        self.duration_spin.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid palette(mid);
                border-radius: 6px;
                min-width: 100px;
            }
        """)
        
        duration_layout.addRow(duration_label, self.duration_spin)
        layout.addLayout(duration_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_types_options(self) -> QGroupBox:
        """Crée le groupe de types de notifications."""
        group = QGroupBox("Types de notifications")
        group.setObjectName("typesGroup")
        group.setStyleSheet("""
            QGroupBox#typesGroup {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid palette(mid);
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 25px;
                color: palette(text);
            }
            QGroupBox#typesGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: palette(base);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                color: palette(text);
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """
        
        # Stock faible
        self.stock_low_check = QCheckBox("Alertes de stock faible")
        self.stock_low_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.stock_low_check)
        
        # Ventes réussies
        self.sales_check = QCheckBox("Confirmations de ventes")
        self.sales_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.sales_check)
        
        # Erreurs
        self.errors_check = QCheckBox("Erreurs")
        self.errors_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.errors_check)
        
        # Avertissements
        self.warnings_check = QCheckBox("Avertissements")
        self.warnings_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.warnings_check)
        
        # Informations
        self.info_check = QCheckBox("Informations")
        self.info_check.setStyleSheet(checkbox_style)
        layout.addWidget(self.info_check)
        
        group.setLayout(layout)
        return group
    
    def _create_actions(self) -> QHBoxLayout:
        """Crée les boutons d'action."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Bouton Enregistrer
        save_btn = QPushButton("Enregistrer")
        save_btn.setMinimumHeight(50)
        save_btn.setMinimumWidth(180)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setObjectName("saveButton")
        
        save_icon = load_svg_icon("settings", size=20)
        save_btn.setIcon(QIcon(save_icon))
        save_btn.setIconSize(QSize(20, 20))
        
        save_btn.setStyleSheet("""
            QPushButton#saveButton {
                background-color: #3498db;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#saveButton:hover {
                background-color: #2980b9;
            }
            QPushButton#saveButton:pressed {
                background-color: #21618c;
            }
        """)
        save_btn.clicked.connect(self._on_save)
        
        # Bouton Tester
        test_btn = QPushButton("Tester")
        test_btn.setMinimumHeight(50)
        test_btn.setMinimumWidth(150)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setObjectName("testButton")
        
        test_icon = load_svg_icon("settings", size=20)
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
        test_btn.clicked.connect(lambda: self.test_requested.emit())
        
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
        reset_btn.clicked.connect(lambda: self.reset_requested.emit())
        
        layout.addWidget(save_btn)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(reset_btn)
        
        return layout
    
    def _on_save(self):
        """Collecte les données et émet le signal de sauvegarde."""
        config = {
            'enabled': self.enabled_check.isChecked(),
            'show_desktop': self.desktop_check.isChecked(),
            'show_sound': self.sound_check.isChecked(),
            'show_tray': self.tray_check.isChecked(),
            'duration': self.duration_spin.value(),
            'stock_low': self.stock_low_check.isChecked(),
            'sales_success': self.sales_check.isChecked(),
            'errors': self.errors_check.isChecked(),
            'warnings': self.warnings_check.isChecked(),
            'info': self.info_check.isChecked()
        }
        self.save_requested.emit(config)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def update_config_display(self, config):
        """Met à jour l'affichage avec la configuration."""
        self.enabled_check.setChecked(config.enabled)
        self.desktop_check.setChecked(config.show_desktop)
        self.sound_check.setChecked(config.show_sound)
        self.tray_check.setChecked(config.show_tray)
        self.duration_spin.setValue(config.duration)
        
        self.stock_low_check.setChecked(config.stock_low)
        self.sales_check.setChecked(config.sales_success)
        self.errors_check.setChecked(config.errors)
        self.warnings_check.setChecked(config.warnings)
        self.info_check.setChecked(config.info)