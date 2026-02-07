"""
Vue de la gestion du stock - Interface utilisateur uniquement.
Séparation complète de la logique métier.
Utilise des icônes SVG au lieu d'emojis.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QDateEdit, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from pathlib import Path
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    """
    Charge une icône SVG et la convertit en QPixmap.
    
    Args:
        icon_name: Nom de l'icône (sans .svg)
        size: Taille en pixels
        
    Returns:
        QPixmap de l'icône ou QPixmap vide si erreur
    """
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
    """
    Crée un placeholder visuel avec une lettre.
    
    Args:
        size: Taille du pixmap
        letter: Lettre à afficher
        
    Returns:
        QPixmap avec fond coloré et lettre
    """
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


class StockView(QWidget):
    """
    Vue de gestion du stock - Affichage uniquement.
    Émet des signaux pour communiquer avec le manager.
    """
    
    # Signaux pour communiquer avec le manager
    search_requested = Signal(str)
    category_filter_changed = Signal(str)
    supplier_filter_changed = Signal(str)
    packaging_filter_changed = Signal(str)
    class_filter_changed = Signal(str)
    date_range_changed = Signal(QDate, QDate)
    add_product_requested = Signal()
    edit_product_requested = Signal(int)
    delete_product_requested = Signal(int)
    refresh_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Widgets principaux
        self.search_input = None
        self.category_filter_combo = None
        self.supplier_filter_combo = None
        self.packaging_group = None
        self.class_filter_combo = None
        self.start_date_edit = None
        self.end_date_edit = None
        self.table_view = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Barre de recherche + Ajouter
        search_layout = self._create_search_section()
        main_layout.addLayout(search_layout)
        
        main_layout.addSpacing(15)
        
        # Filtres (Ligne 1)
        filter_row1 = self._create_filter_row1()
        main_layout.addLayout(filter_row1)
        
        main_layout.addSpacing(8)
        
        # Filtres (Ligne 2 - Dates)
        filter_row2 = self._create_filter_row2()
        main_layout.addLayout(filter_row2)
        
        main_layout.addSpacing(15)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setStyleSheet("""
            QTableView {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
            }
            QTableView::item {
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.table_view)
        
        main_layout.addSpacing(12)
        
        # Boutons d'action
        btn_layout = self._create_action_buttons()
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # Connecter les signaux internes
        self._connect_signals()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête de la page."""
        layout = QHBoxLayout()
        
        # Conteneur pour icône + titre
        header_container = QHBoxLayout()
        header_container.setSpacing(12)
        
        # Icône
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setPixmap(load_svg_icon("package", size=32))
        header_container.addWidget(icon_label)
        
        # Titre
        title = QLabel("Gestion du Stock")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_container.addWidget(title)
        
        layout.addLayout(header_container)
        layout.addStretch()
        
        return layout
    
    def _create_search_section(self) -> QHBoxLayout:
        """Crée la section de recherche."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.setMinimumHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(38)
        search_btn.setFixedWidth(120)
        search_btn.setCursor(Qt.PointingHandCursor)
        
        # Ajouter icône au bouton
        search_icon = load_svg_icon("search", size=16)
        search_btn.setIcon(QIcon(search_icon))
        search_btn.setIconSize(search_icon.size())
        
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        search_btn.clicked.connect(self._on_search_clicked)
        
        add_btn = QPushButton("Ajouter Produit")
        add_btn.setMinimumHeight(38)
        add_btn.setFixedWidth(150)
        add_btn.setCursor(Qt.PointingHandCursor)
        
        # Ajouter icône au bouton
        add_icon = load_svg_icon("plus-circle", size=16)
        add_btn.setIcon(QIcon(add_icon))
        add_btn.setIconSize(add_icon.size())
        
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_product_requested.emit())
        
        layout.addWidget(self.search_input)
        layout.addWidget(search_btn)
        layout.addStretch()
        layout.addWidget(add_btn)
        
        return layout
    
    def _create_filter_row1(self) -> QHBoxLayout:
        """Crée la première ligne de filtres."""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Catégorie
        cat_label = QLabel("Catégorie:")
        cat_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(cat_label)
        
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("Toutes")
        self.category_filter_combo.setFixedWidth(140)
        self.category_filter_combo.setMinimumHeight(32)
        self.category_filter_combo.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.category_filter_combo)
        
        layout.addSpacing(20)
        
        # Fournisseur
        sup_label = QLabel("Fournisseur:")
        sup_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(sup_label)
        
        self.supplier_filter_combo = QComboBox()
        self.supplier_filter_combo.addItem("Tous")
        self.supplier_filter_combo.setFixedWidth(140)
        self.supplier_filter_combo.setMinimumHeight(32)
        self.supplier_filter_combo.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.supplier_filter_combo)
        
        layout.addSpacing(20)
        
        # Type d'emballage
        pack_label = QLabel("Type d'emballage:")
        pack_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(pack_label)
        
        self.packaging_group = QButtonGroup(self)
        packaging_options = ["Tous", "Carton", "Unité", "Pièce", "Lot", "Autre"]
        for option in packaging_options:
            radio_btn = QRadioButton(option)
            radio_btn.setStyleSheet("font-size: 13px;")
            layout.addWidget(radio_btn)
            self.packaging_group.addButton(radio_btn)
            if option == "Tous":
                radio_btn.setChecked(True)
        
        layout.addSpacing(20)
        
        # Classe (pour Manuels)
        class_label = QLabel("Classe:")
        class_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(class_label)
        
        self.class_filter_combo = QComboBox()
        self.class_filter_combo.addItem("Toutes")
        self.class_filter_combo.setFixedWidth(140)
        self.class_filter_combo.setMinimumHeight(32)
        self.class_filter_combo.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.class_filter_combo)
        
        layout.addStretch()
        
        return layout
    
    def _create_filter_row2(self) -> QHBoxLayout:
        """Crée la deuxième ligne de filtres (dates)."""
        layout = QHBoxLayout()
        
        date_label = QLabel("Date d'ajout (Du):")
        date_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(date_label)
        
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.start_date_edit.setDate(QDate(2024, 1, 1))
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setFixedWidth(130)
        self.start_date_edit.setMinimumHeight(32)
        self.start_date_edit.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.start_date_edit)
        
        to_label = QLabel("Au:")
        to_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(to_label)
        
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setFixedWidth(130)
        self.end_date_edit.setMinimumHeight(32)
        self.end_date_edit.setStyleSheet("font-size: 13px; padding: 5px;")
        layout.addWidget(self.end_date_edit)
        
        layout.addStretch()
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action."""
        layout = QHBoxLayout()
        
        # Bouton Modifier
        edit_btn = QPushButton("Modifier")
        edit_btn.setMinimumHeight(40)
        edit_btn.setFixedWidth(130)
        edit_btn.setCursor(Qt.PointingHandCursor)
        
        edit_icon = load_svg_icon("edit", size=16)
        edit_btn.setIcon(QIcon(edit_icon))
        edit_btn.setIconSize(edit_icon.size())
        
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        edit_btn.clicked.connect(self._on_edit_clicked)
        
        # Bouton Supprimer
        delete_btn = QPushButton("Supprimer")
        delete_btn.setMinimumHeight(40)
        delete_btn.setFixedWidth(130)
        delete_btn.setCursor(Qt.PointingHandCursor)
        
        delete_icon = load_svg_icon("trash", size=16)
        delete_btn.setIcon(QIcon(delete_icon))
        delete_btn.setIconSize(delete_icon.size())
        
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        delete_btn.clicked.connect(self._on_delete_clicked)
        
        # Bouton Actualiser
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setFixedWidth(130)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        
        refresh_icon = load_svg_icon("refresh", size=16)
        refresh_btn.setIcon(QIcon(refresh_icon))
        refresh_btn.setIconSize(refresh_icon.size())
        
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
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
        self.category_filter_combo.currentTextChanged.connect(
            lambda text: self.category_filter_changed.emit(text)
        )
        self.supplier_filter_combo.currentTextChanged.connect(
            lambda text: self.supplier_filter_changed.emit(text)
        )
        self.packaging_group.buttonClicked.connect(
            lambda btn: self.packaging_filter_changed.emit(btn.text())
        )
        self.class_filter_combo.currentTextChanged.connect(
            lambda text: self.class_filter_changed.emit(text)
        )
        self.start_date_edit.dateChanged.connect(self._on_date_changed)
        self.end_date_edit.dateChanged.connect(self._on_date_changed)
    
    def _on_search_clicked(self):
        """Gère le clic sur Rechercher."""
        search_text = self.search_input.text()
        self.search_requested.emit(search_text)
    
    def _on_edit_clicked(self):
        """Gère le clic sur Modifier."""
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row = selected_index.row()
            self.edit_product_requested.emit(row)
    
    def _on_delete_clicked(self):
        """Gère le clic sur Supprimer."""
        selected_index = self.table_view.currentIndex()
        if selected_index.isValid():
            row = selected_index.row()
            self.delete_product_requested.emit(row)
    
    def _on_date_changed(self):
        """Gère le changement de dates."""
        start = self.start_date_edit.date()
        end = self.end_date_edit.date()
        self.date_range_changed.emit(start, end)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def set_table_model(self, model):
        """Définit le modèle du tableau."""
        self.table_view.setModel(model)
    
    def update_categories(self, categories: list):
        """Met à jour la liste des catégories."""
        current = self.category_filter_combo.currentText()
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem("Toutes")
        self.category_filter_combo.addItems(categories)
        
        # Restaurer la sélection
        index = self.category_filter_combo.findText(current)
        if index >= 0:
            self.category_filter_combo.setCurrentIndex(index)
    
    def update_suppliers(self, suppliers: list):
        """Met à jour la liste des fournisseurs."""
        current = self.supplier_filter_combo.currentText()
        self.supplier_filter_combo.clear()
        self.supplier_filter_combo.addItem("Tous")
        self.supplier_filter_combo.addItems(suppliers)
        
        # Restaurer la sélection
        index = self.supplier_filter_combo.findText(current)
        if index >= 0:
            self.supplier_filter_combo.setCurrentIndex(index)
    
    def update_classes(self, classes: list):
        """Met à jour la liste des classes."""
        current = self.class_filter_combo.currentText()
        self.class_filter_combo.clear()
        self.class_filter_combo.addItem("Toutes")
        self.class_filter_combo.addItems(classes)
        
        # Restaurer la sélection
        index = self.class_filter_combo.findText(current)
        if index >= 0:
            self.class_filter_combo.setCurrentIndex(index)
    
    def get_selected_row(self) -> int:
        """Retourne l'index de la ligne sélectionnée."""
        selected_index = self.table_view.currentIndex()
        return selected_index.row() if selected_index.isValid() else -1
    
    def clear_search(self):
        """Vide la barre de recherche."""
        self.search_input.clear()