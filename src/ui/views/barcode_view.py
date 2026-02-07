"""
Vue de gestion des codes-barres - Interface utilisateur uniquement.
Séparation complète de la logique métier.
CORRECTION: Bouton Éditer visible en mode dark.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFormLayout, QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QDoubleValidator, QIntValidator
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    """Charge une icône SVG et la convertit en QPixmap."""
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
        print(f"Erreur chargement icône {icon_name}: {e}")
        return QPixmap()


class BarcodeView(QWidget):
    """
    Vue de gestion des codes-barres - Affichage uniquement.
    Émet des signaux pour communiquer avec le manager.
    """
    
    # Signaux pour communiquer avec le manager
    search_barcode_requested = Signal(str)
    scan_barcode_requested = Signal()
    save_product_requested = Signal(dict)
    generate_internal_barcode_requested = Signal(dict)
    print_barcode_requested = Signal()
    refresh_products_requested = Signal()
    edit_product_requested = Signal(int)
    delete_product_requested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Widgets principaux
        self.tab_widget = None
        
        # Onglet 1: Gestion produits
        self.external_barcode_input = None
        self.scan_product_status = None
        self.product_id_hidden = None
        self.product_name_input = None
        self.product_category_combo = None
        self.product_price_input = None
        self.product_stock_input = None
        self.save_product_btn = None
        self.barcode_preview = None
        self.barcode_value_display = None
        self.print_internal_btn = None
        
        # Onglet 2: Audit produits
        self.products_table = None
        
        self.init_ui()
    
    def init_ui(self):
        """Construit l'interface utilisateur."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # En-tête
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #9b59b6;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                background: #95a5a6;
                color: white;
            }
            QTabBar::tab:hover {
                background: #7f8c8d;
                color: white;
            }
        """)
        
        # Onglet 1: Gestion des produits
        tab1 = self._create_product_management_tab()
        self.tab_widget.addTab(tab1, "Ajouter/Gérer Codes-Barres")
        
        # Onglet 2: Audit des produits
        tab2 = self._create_audit_tab()
        self.tab_widget.addTab(tab2, "Audit & Édition Produits")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
    
    def _create_header(self) -> QHBoxLayout:
        """Crée l'en-tête de la page."""
        layout = QHBoxLayout()
        
        # Conteneur pour icône + titre
        header_container = QHBoxLayout()
        header_container.setSpacing(12)
        
        # Icône (utiliser package.svg comme icône de barcode)
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_pixmap = load_svg_icon("package", size=32)
        if not icon_pixmap.isNull():
            icon_label.setPixmap(icon_pixmap)
        header_container.addWidget(icon_label)
        
        # Titre
        title = QLabel("Gestion des Codes-Barres")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_container.addWidget(title)
        
        layout.addLayout(header_container)
        layout.addStretch()
        
        return layout
    
    def _create_product_management_tab(self) -> QWidget:
        """Crée l'onglet de gestion des produits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Section scan/recherche
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit")
        scan_layout = QVBoxLayout(scan_group)
        
        # Champ de saisie + boutons
        scan_input_layout = QHBoxLayout()
        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText("Scannez ou saisissez un code-barres...")
        self.external_barcode_input.setMinimumHeight(34)
        scan_input_layout.addWidget(self.external_barcode_input)
        
        # Bouton Rechercher
        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(34)
        search_btn.setFixedWidth(120)
        search_icon = load_svg_icon("search", size=16)
        if not search_icon.isNull():
            search_btn.setIcon(QIcon(search_icon))
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self._on_search_barcode)
        scan_input_layout.addWidget(search_btn)
        
        # Bouton Scanner
        scan_btn = QPushButton("Scanner")
        scan_btn.setMinimumHeight(34)
        scan_btn.setFixedWidth(120)
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        scan_btn.clicked.connect(lambda: self.scan_barcode_requested.emit())
        scan_input_layout.addWidget(scan_btn)
        
        scan_layout.addLayout(scan_input_layout)
        
        # Statut
        self.scan_product_status = QLabel("Saisissez un code-barres pour rechercher un produit.")
        self.scan_product_status.setWordWrap(True)
        self.scan_product_status.setStyleSheet("color: #7f8c8d; font-style: italic;")
        scan_layout.addWidget(self.scan_product_status)
        
        layout.addWidget(scan_group)
        
        # Formulaire produit
        form_group = QGroupBox("Détails du Produit")
        form_layout = QFormLayout(form_group)
        
        self.product_id_hidden = QLabel("")
        self.product_id_hidden.setVisible(False)
        
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nom du produit")
        self.product_name_input.setMinimumHeight(34)
        
        self.product_category_combo = QComboBox()
        self.product_category_combo.addItems([
            "Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"
        ])
        self.product_category_combo.setMinimumHeight(34)
        
        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText("0.00")
        self.product_price_input.setValidator(QDoubleValidator(0, 99999.99, 2))
        self.product_price_input.setMinimumHeight(34)
        
        self.product_stock_input = QLineEdit()
        self.product_stock_input.setPlaceholderText("0")
        self.product_stock_input.setValidator(QIntValidator(0, 999999))
        self.product_stock_input.setMinimumHeight(34)
        
        form_layout.addRow("Nom:", self.product_name_input)
        form_layout.addRow("Catégorie:", self.product_category_combo)
        form_layout.addRow("Prix unitaire:", self.product_price_input)
        form_layout.addRow("Stock:", self.product_stock_input)
        
        layout.addWidget(form_group)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Bouton Sauvegarder
        self.save_product_btn = QPushButton("Ajouter Produit")
        self.save_product_btn.setMinimumHeight(38)
        self.save_product_btn.setFixedWidth(180)
        save_icon = load_svg_icon("plus-circle", size=16)
        if not save_icon.isNull():
            self.save_product_btn.setIcon(QIcon(save_icon))
        self.save_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_product_btn.clicked.connect(self._on_save_product)
        buttons_layout.addWidget(self.save_product_btn)
        
        # Bouton Générer Code Interne
        generate_btn = QPushButton("Générer Code Interne")
        generate_btn.setMinimumHeight(38)
        generate_btn.setFixedWidth(180)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        generate_btn.clicked.connect(self._on_generate_internal)
        buttons_layout.addWidget(generate_btn)
        
        layout.addLayout(buttons_layout)
        
        # Aperçu du code-barres
        preview_group = QGroupBox("Aperçu du Code-Barres")
        preview_layout = QVBoxLayout(preview_group)
        
        self.barcode_preview = QLabel()
        self.barcode_preview.setAlignment(Qt.AlignCenter)
        self.barcode_preview.setMinimumHeight(120)
        self.barcode_preview.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6;")
        preview_layout.addWidget(self.barcode_preview)
        
        self.barcode_value_display = QLabel("<i>Code-barres affiché ici</i>")
        self.barcode_value_display.setAlignment(Qt.AlignCenter)
        self.barcode_value_display.setFont(QFont("Courier New", 12))
        preview_layout.addWidget(self.barcode_value_display)
        
        # Bouton Imprimer
        self.print_internal_btn = QPushButton("Imprimer l'Étiquette")
        self.print_internal_btn.setMinimumHeight(38)
        self.print_internal_btn.setEnabled(False)
        print_icon = load_svg_icon("printer", size=16)
        if not print_icon.isNull():
            self.print_internal_btn.setIcon(QIcon(print_icon))
        self.print_internal_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.print_internal_btn.clicked.connect(lambda: self.print_barcode_requested.emit())
        preview_layout.addWidget(self.print_internal_btn)
        
        layout.addWidget(preview_group)
        layout.addStretch()
        
        return tab
    
    def _create_audit_tab(self) -> QWidget:
        """Crée l'onglet d'audit des produits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tableau des produits
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Code-Barres", "Nom", "Catégorie", "Prix", "Stock", "Interne"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """)
        layout.addWidget(self.products_table)
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        # Bouton Actualiser
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setMinimumHeight(38)
        refresh_btn.setFixedWidth(130)
        refresh_icon = load_svg_icon("refresh", size=16)
        if not refresh_icon.isNull():
            refresh_btn.setIcon(QIcon(refresh_icon))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_products_requested.emit())
        buttons_layout.addWidget(refresh_btn)
        
        # Bouton Éditer - CORRIGÉ POUR MODE DARK
        edit_btn = QPushButton("Éditer")
        edit_btn.setMinimumHeight(38)
        edit_btn.setFixedWidth(130)
        edit_icon = load_svg_icon("edit", size=16)
        if not edit_icon.isNull():
            edit_btn.setIcon(QIcon(edit_icon))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: #2c3e50;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
                color: white;
            }
        """)
        edit_btn.clicked.connect(self._on_edit_product)
        buttons_layout.addWidget(edit_btn)
        
        # Bouton Supprimer
        delete_btn = QPushButton("Supprimer")
        delete_btn.setMinimumHeight(38)
        delete_btn.setFixedWidth(130)
        delete_icon = load_svg_icon("trash", size=16)
        if not delete_icon.isNull():
            delete_btn.setIcon(QIcon(delete_icon))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(self._on_delete_product)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return tab
    
    # ========== SLOTS INTERNES ==========
    
    def _on_search_barcode(self):
        """Gère la recherche de code-barres."""
        barcode = self.external_barcode_input.text().strip()
        if barcode:
            self.search_barcode_requested.emit(barcode)
    
    def _on_save_product(self):
        """Gère la sauvegarde du produit."""
        data = {
            'id': self.product_id_hidden.text(),
            'barcode': self.external_barcode_input.text().strip(),
            'name': self.product_name_input.text().strip(),
            'category': self.product_category_combo.currentText(),
            'price': self.product_price_input.text().strip(),
            'stock': self.product_stock_input.text().strip()
        }
        self.save_product_requested.emit(data)
    
    def _on_generate_internal(self):
        """Gère la génération de code interne."""
        data = {
            'name': self.product_name_input.text().strip(),
            'category': self.product_category_combo.currentText(),
            'price': self.product_price_input.text().strip(),
            'stock': self.product_stock_input.text().strip()
        }
        self.generate_internal_barcode_requested.emit(data)
    
    def _on_edit_product(self):
        """Gère l'édition d'un produit."""
        selected_rows = self.products_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            product_id = int(self.products_table.item(row, 0).text())
            self.edit_product_requested.emit(product_id)
    
    def _on_delete_product(self):
        """Gère la suppression d'un produit."""
        selected_rows = self.products_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            product_id = int(self.products_table.item(row, 0).text())
            self.delete_product_requested.emit(product_id)
    
    # ========== MÉTHODES PUBLIQUES POUR LE MANAGER ==========
    
    def update_product_form(self, product_data: dict):
        """Met à jour le formulaire avec les données d'un produit."""
        self.product_id_hidden.setText(str(product_data.get('id', '')))
        self.external_barcode_input.setText(product_data.get('barcode', ''))
        self.product_name_input.setText(product_data.get('name', ''))
        self.product_category_combo.setCurrentText(product_data.get('category', 'Divers'))
        self.product_price_input.setText(str(product_data.get('price', '0')))
        self.product_stock_input.setText(str(product_data.get('stock', '0')))
        
        if product_data.get('id'):
            self.save_product_btn.setText("Mettre à Jour")
            self.scan_product_status.setText(f"Produit trouvé: <b>{product_data.get('name')}</b>")
        else:
            self.save_product_btn.setText("Ajouter Produit")
            self.scan_product_status.setText(f"Code-barres non trouvé. Remplissez les détails pour ajouter.")
    
    def clear_product_form(self):
        """Réinitialise le formulaire."""
        self.product_id_hidden.setText("")
        self.external_barcode_input.clear()
        self.product_name_input.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_price_input.clear()
        self.product_stock_input.clear()
        self.save_product_btn.setText("Ajouter Produit")
        self.scan_product_status.setText("Saisissez un code-barres pour rechercher un produit.")
        self.barcode_preview.clear()
        self.barcode_value_display.setText("<i>Code-barres affiché ici</i>")
        self.print_internal_btn.setEnabled(False)
    
    def update_barcode_preview(self, barcode_value: str, image_path: str):
        """Met à jour l'aperçu du code-barres."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.barcode_preview.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
            self.barcode_value_display.setText(barcode_value)
            self.print_internal_btn.setEnabled(True)
    
    def update_products_table(self, products: list):
        """Met à jour le tableau des produits."""
        self.products_table.setRowCount(len(products))
        
        for row_idx, product in enumerate(products):
            self.products_table.setItem(row_idx, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row_idx, 1, QTableWidgetItem(product['barcode']))
            self.products_table.setItem(row_idx, 2, QTableWidgetItem(product['name']))
            self.products_table.setItem(row_idx, 3, QTableWidgetItem(product['category']))
            self.products_table.setItem(row_idx, 4, QTableWidgetItem(f"{product['price']:.2f}"))
            self.products_table.setItem(row_idx, 5, QTableWidgetItem(str(product['stock'])))
            self.products_table.setItem(row_idx, 6, QTableWidgetItem("Oui" if product['is_internal_barcode'] else "Non"))
    
    def set_status_message(self, message: str, is_error: bool = False):
        """Affiche un message de statut."""
        color = "red" if is_error else "#27ae60"
        self.scan_product_status.setText(f"<span style='color: {color};'>{message}</span>")