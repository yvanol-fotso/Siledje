"""
Vue de la gestion du stock - Interface utilisateur uniquement.
Séparation complète de la logique métier.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QDateEdit, QRadioButton, QButtonGroup, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont


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
        main_layout.setSpacing(15)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Barre de recherche + Ajouter
        search_layout = self._create_search_section()
        main_layout.addLayout(search_layout)
        
        main_layout.addSpacing(20)
        
        # Filtres (Ligne 1)
        filter_row1 = self._create_filter_row1()
        main_layout.addLayout(filter_row1)
        
        main_layout.addSpacing(10)
        
        # Filtres (Ligne 2 - Dates)
        filter_row2 = self._create_filter_row2()
        main_layout.addLayout(filter_row2)
        
        main_layout.addSpacing(20)
        
        # Table
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setStyleSheet("""
            QTableView {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border: none;
            }
        """)
        main_layout.addWidget(self.table_view)
        
        main_layout.addSpacing(15)
        
        # Boutons d'action
        btn_layout = self._create_action_buttons()
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # Connecter les signaux internes
        self._connect_signals()
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête de la page."""
        layout = QHBoxLayout()
        
        title = QLabel("📚 Gestion du Stock")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        layout.addWidget(title)
        layout.addStretch()
        
        return layout
    
    def _create_search_section(self) -> QHBoxLayout:
        """Crée la section de recherche."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher un produit...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        search_btn = QPushButton("Rechercher")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self._on_search_clicked)
        
        add_btn = QPushButton("➕ Ajouter Produit")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
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
        layout.setSpacing(20)
        
        # Catégorie
        layout.addWidget(QLabel("Catégorie:"))
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("Toutes")
        self.category_filter_combo.setFixedWidth(150)
        layout.addWidget(self.category_filter_combo)
        
        layout.addSpacing(30)
        
        # Fournisseur
        layout.addWidget(QLabel("Fournisseur:"))
        self.supplier_filter_combo = QComboBox()
        self.supplier_filter_combo.addItem("Tous")
        self.supplier_filter_combo.setFixedWidth(150)
        layout.addWidget(self.supplier_filter_combo)
        
        layout.addSpacing(30)
        
        # Type d'emballage
        layout.addWidget(QLabel("Type d'emballage:"))
        self.packaging_group = QButtonGroup(self)
        packaging_options = ["Tous", "Carton", "Unité", "Pièce", "Lot", "Autre"]
        for option in packaging_options:
            radio_btn = QRadioButton(option)
            layout.addWidget(radio_btn)
            self.packaging_group.addButton(radio_btn)
            if option == "Tous":
                radio_btn.setChecked(True)
        
        layout.addSpacing(30)
        
        # Classe (pour Manuels)
        layout.addWidget(QLabel("Classe:"))
        self.class_filter_combo = QComboBox()
        self.class_filter_combo.addItem("Toutes")
        self.class_filter_combo.setFixedWidth(150)
        layout.addWidget(self.class_filter_combo)
        
        layout.addStretch()
        
        return layout
    
    def _create_filter_row2(self) -> QHBoxLayout:
        """Crée la deuxième ligne de filtres (dates)."""
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Date d'ajout (Du):"))
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.start_date_edit.setDate(QDate(2024, 1, 1))
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.start_date_edit)
        
        layout.addWidget(QLabel("Au:"))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(self.end_date_edit)
        
        layout.addStretch()
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Crée les boutons d'action."""
        layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        edit_btn.clicked.connect(self._on_edit_clicked)
        
        delete_btn = QPushButton("🗑️ Supprimer")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(self._on_delete_clicked)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
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