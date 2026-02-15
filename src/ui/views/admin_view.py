"""
Vue de gestion des utilisateurs - Interface utilisateur responsive.
Utilise des icônes SVG au lieu d'emojis.
S'adapte aux modes Dark/Light.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QLabel
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


class AdminView(QWidget):
    """
    Vue de gestion des utilisateurs ultra-responsive.
    S'adapte automatiquement aux modes Dark/Light.
    """
    
    # Signaux pour communiquer avec le manager
    search_requested = Signal(str)
    add_user_requested = Signal()
    edit_user_requested = Signal(int)
    delete_user_requested = Signal(int)
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Widgets principaux
        self.search_input = None
        self.table_view = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur responsive."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Barre de recherche et boutons
        search_layout = self._create_search_section()
        main_layout.addLayout(search_layout)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setMinimumHeight(400)
        
        # Style adaptatif pour mode dark/light
        self.table_view.setObjectName("adminTable")
        self.table_view.setStyleSheet("""
            QTableView#adminTable {
                border: 2px solid palette(mid);
                border-radius: 10px;
                font-size: 14px;
                gridline-color: palette(mid);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QTableView#adminTable::item {
                padding: 8px;
                border-bottom: 1px solid palette(midlight);
            }
            QTableView#adminTable::item:alternate {
                background-color: palette(alternate-base);
            }
            QTableView#adminTable::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QTableView#adminTable::item:hover {
                background-color: palette(light);
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border: none;
                border-right: 1px solid #8e44ad;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        main_layout.addWidget(self.table_view)
        
        # Boutons d'action
        btn_layout = self._create_action_buttons()
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # Connecter les signaux internes
        self._connect_signals()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Icône + Titre
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("users", size=40))
        
        title = QLabel("Gestion des Utilisateurs")
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
    
    def _create_search_section(self) -> QHBoxLayout:
        """Crée la section de recherche responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Champ de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un utilisateur...")
        self.search_input.setMinimumHeight(45)
        self.search_input.setObjectName("searchInput")
        self.search_input.setStyleSheet("""
            QLineEdit#searchInput {
                padding: 10px 15px;
                border: 2px solid palette(mid);
                border-radius: 10px;
                font-size: 15px;
                background-color: palette(base);
                color: palette(text);
            }
            QLineEdit#searchInput:focus {
                border: 2px solid #9b59b6;
            }
        """)
        
        # Bouton Rechercher
        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(45)
        search_btn.setMinimumWidth(140)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setObjectName("searchButton")
        
        search_icon = load_svg_icon("search", size=18)
        search_btn.setIcon(QIcon(search_icon))
        search_btn.setIconSize(QSize(18, 18))
        
        search_btn.setStyleSheet("""
            QPushButton#searchButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#searchButton:hover {
                background-color: #8e44ad;
            }
            QPushButton#searchButton:pressed {
                background-color: #7d3c98;
            }
        """)
        search_btn.clicked.connect(self._on_search_clicked)
        
        # Bouton Ajouter
        add_btn = QPushButton("Nouvel Utilisateur")
        add_btn.setMinimumHeight(45)
        add_btn.setMinimumWidth(180)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setObjectName("addButton")
        
        add_icon = load_svg_icon("user-plus", size=18)
        add_btn.setIcon(QIcon(add_icon))
        add_btn.setIconSize(QSize(18, 18))
        
        add_btn.setStyleSheet("""
            QPushButton#addButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#addButton:hover {
                background-color: #27ae60;
            }
            QPushButton#addButton:pressed {
                background-color: #1e8449;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_user_requested.emit())
        
        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn, 1)
        layout.addWidget(add_btn, 1)
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action responsive."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Bouton Modifier
        edit_btn = QPushButton("Modifier")
        edit_btn.setMinimumHeight(45)
        edit_btn.setMinimumWidth(140)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setObjectName("editButton")
        
        edit_icon = load_svg_icon("edit", size=18)
        edit_btn.setIcon(QIcon(edit_icon))
        edit_btn.setIconSize(QSize(18, 18))
        
        edit_btn.setStyleSheet("""
            QPushButton#editButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#editButton:hover {
                background-color: #e67e22;
            }
            QPushButton#editButton:pressed {
                background-color: #d35400;
            }
        """)
        edit_btn.clicked.connect(self._on_edit_clicked)
        
        # Bouton Supprimer
        delete_btn = QPushButton("Supprimer")
        delete_btn.setMinimumHeight(45)
        delete_btn.setMinimumWidth(140)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setObjectName("deleteButton")
        
        delete_icon = load_svg_icon("trash", size=18)
        delete_btn.setIcon(QIcon(delete_icon))
        delete_btn.setIconSize(QSize(18, 18))
        
        delete_btn.setStyleSheet("""
            QPushButton#deleteButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#deleteButton:hover {
                background-color: #c0392b;
            }
            QPushButton#deleteButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_btn.clicked.connect(self._on_delete_clicked)
        
        # Bouton Actualiser
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setMinimumHeight(45)
        refresh_btn.setMinimumWidth(140)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setObjectName("refreshButton")
        
        refresh_icon = load_svg_icon("refresh", size=18)
        refresh_btn.setIcon(QIcon(refresh_icon))
        refresh_btn.setIconSize(QSize(18, 18))
        
        refresh_btn.setStyleSheet("""
            QPushButton#refreshButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#refreshButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton#refreshButton:pressed {
                background-color: #707b7c;
            }
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_requested.emit())
        
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        layout.addWidget(refresh_btn)
        
        return layout
    
    def _connect_signals(self):
        """Connecte les signaux internes des widgets."""
        self.search_input.returnPressed.connect(self._on_search_clicked)
    
    def _on_search_clicked(self):
        """Gère le clic sur Rechercher."""
        search_text = self.search_input.text()
        self.search_requested.emit(search_text)
    
    def _on_edit_clicked(self):
        """Gère le clic sur Modifier."""
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row = selected_index.row()
            self.edit_user_requested.emit(row)
    
    def _on_delete_clicked(self):
        """Gère le clic sur Supprimer."""
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row = selected_index.row()
            self.delete_user_requested.emit(row)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def set_table_model(self, model):
        """Définit le modèle du tableau."""
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
    
    def get_selected_row(self) -> int:
        """Retourne l'index de la ligne sélectionnée."""
        selected_index = self.table_view.currentIndex()
        return selected_index.row() if selected_index.isValid() else -1
    
    def clear_search(self):
        """Vide la barre de recherche."""
        self.search_input.clear()