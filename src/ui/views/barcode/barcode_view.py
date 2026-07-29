"""
Vue de gestion des codes-barres - Interface utilisateur uniquement.
Herite de BaseView pour une structure coherente.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGridLayout, QTabWidget, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QDoubleValidator, QIntValidator

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


class BarcodeView(BaseView):
    """Vue de gestion des codes-barres. Herite de BaseView."""

    search_barcode_requested = Signal(str)
    scan_barcode_requested = Signal()
    save_product_requested = Signal(dict)
    generate_internal_barcode_requested = Signal(dict)
    print_barcode_requested = Signal()
    refresh_products_requested = Signal()
    edit_product_requested = Signal(int)
    delete_product_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion des Codes-Barres",
            icon_name="package"
        )

        self.tab_widget = None
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
        self.products_table = None
        self._last_selected_row = -1

        # Reconstruire le contenu
        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        # Initialiser les composants
        self._init_tabs()
        self._connect_signals()
        self._apply_theme_styles()

    def _init_tabs(self):
        """Initialise les onglets."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("barcodeTabs")

        self.tab_widget.addTab(self._create_product_management_tab(), "Ajouter/Gerer Codes-Barres")
        self.tab_widget.addTab(self._create_audit_tab(), "Audit & Edition Produits")

        self.content_layout.addWidget(self.tab_widget)

    def _create_product_management_tab(self) -> QWidget:
        """Onglet de gestion des produits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Recherche ────────────────────────────────────────────────
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit")
        scan_group.setObjectName("scanGroup")
        scan_v = QVBoxLayout(scan_group)
        scan_v.setSpacing(8)

        scan_row = QHBoxLayout()
        scan_row.setSpacing(10)

        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText("Scannez ou saisissez un code-barres...")
        self.external_barcode_input.setMinimumHeight(38)
        self.external_barcode_input.setObjectName("barcodeInput")
        self.external_barcode_input.returnPressed.connect(self._on_search_barcode)

        # ✅ Utilisation de couleurs en dur pour eviter les erreurs Palette
        search_btn = self._make_btn(
            "Rechercher", "search", "#567ba1", "#46648a",
            "#3a5470", w=130, slot=self._on_search_barcode
        )

        scan_btn = self._make_btn(
            "Scanner", "scan", "#3498db", "#2980b9",
            "#21618c", w=120, slot=lambda: self.scan_barcode_requested.emit()
        )

        scan_row.addWidget(self.external_barcode_input, 1)
        scan_row.addWidget(search_btn)
        scan_row.addWidget(scan_btn)
        scan_v.addLayout(scan_row)

        self.scan_product_status = QLabel("Saisissez un code-barres pour rechercher un produit.")
        self.scan_product_status.setWordWrap(True)
        self.scan_product_status.setObjectName("statusLabel")
        scan_v.addWidget(self.scan_product_status)

        layout.addWidget(scan_group)

        # ── Détails produit ──────────────────────────────────────────
        form_group = QGroupBox("Details du Produit")
        form_group.setObjectName("formGroup")
        form_group.setMinimumHeight(160)

        self.product_id_hidden = QLabel("")
        self.product_id_hidden.setVisible(False)

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nom du produit")
        self.product_name_input.setMinimumHeight(38)
        self.product_name_input.setObjectName("productNameInput")

        self.product_category_combo = QComboBox()
        self.product_category_combo.addItems(["Papeterie", "Fournitures", "Vetements", "Livres", "Divers"])
        self.product_category_combo.setMinimumHeight(38)
        self.product_category_combo.setObjectName("categoryCombo")

        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText("0.00")
        self.product_price_input.setValidator(QDoubleValidator(0, 99999.99, 2))
        self.product_price_input.setMinimumHeight(38)
        self.product_price_input.setObjectName("priceInput")

        self.product_stock_input = QLineEdit()
        self.product_stock_input.setPlaceholderText("0")
        self.product_stock_input.setValidator(QIntValidator(0, 999999))
        self.product_stock_input.setMinimumHeight(38)
        self.product_stock_input.setObjectName("stockInput")

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(30)
        grid.setContentsMargins(20, 30, 20, 30)

        grid.addWidget(QLabel("Nom :"), 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_name_input, 0, 1)
        grid.addWidget(QLabel("Categorie :"), 0, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_category_combo, 0, 3)

        grid.addWidget(QLabel("Prix unitaire :"), 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_price_input, 1, 1)
        grid.addWidget(QLabel("Stock :"), 1, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_stock_input, 1, 3)

        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(3, 1)

        form_group.setLayout(grid)
        layout.addWidget(form_group)

        # ── Boutons d'action ─────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.save_product_btn = self._make_btn(
            "Ajouter Produit", "plus-circle", "#2ecc71", "#27ae60",
            "#1e8449", w=160, slot=self._on_save_product
        )

        gen_btn = self._make_btn(
            "Generer Code Interne", "barcode", "#9b59b6", "#8e44ad",
            "#7d3c98", w=180, slot=self._on_generate_internal
        )

        btn_row.addWidget(self.save_product_btn)
        btn_row.addWidget(gen_btn)
        layout.addLayout(btn_row)

        # ── Apercu code-barres ───────────────────────────────────────
        preview_group = QGroupBox("Apercu du Code-Barres")
        preview_group.setObjectName("previewGroup")
        preview_v = QVBoxLayout(preview_group)
        preview_v.setSpacing(8)

        self.barcode_preview = QLabel()
        self.barcode_preview.setAlignment(Qt.AlignCenter)
        self.barcode_preview.setMinimumHeight(100)
        self.barcode_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.barcode_preview.setObjectName("barcodePreview")
        preview_v.addWidget(self.barcode_preview)

        self.barcode_value_display = QLabel("<i>Code-barres affiche ici</i>")
        self.barcode_value_display.setAlignment(Qt.AlignCenter)
        self.barcode_value_display.setFont(QFont("Courier New", 12))
        self.barcode_value_display.setObjectName("barcodeValue")
        preview_v.addWidget(self.barcode_value_display)

        self.print_internal_btn = self._make_btn(
            "Imprimer l'Etiquette", "printer", "#17a2b8", "#138496",
            "#117a8b", w=180, slot=lambda: self.print_barcode_requested.emit()
        )
        self.print_internal_btn.setEnabled(False)
        preview_v.addWidget(self.print_internal_btn)

        layout.addWidget(preview_group)
        layout.addStretch()

        return tab

    def _create_audit_tab(self) -> QWidget:
        """Onglet d'audit des produits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Tableau
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Code-Barres", "Nom", "Categorie", "Prix", "Stock", "Interne"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.setAlternatingRowColors(False)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.products_table.verticalHeader().setDefaultSectionSize(38)
        self.products_table.setObjectName("barcodeTable")

        layout.addWidget(self.products_table, 1)

        # Boutons d'action
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = self._make_btn(
            "Actualiser", "refresh", "#aab7b8", "#95a5a6",
            "#7f8c8d", w=130, slot=lambda: self.refresh_products_requested.emit()
        )

        edit_btn = self._make_btn(
            "Editer", "edit", "#f39c12", "#e67e22",
            "#d35400", w=130, slot=self._on_edit_product
        )

        delete_btn = self._make_btn(
            "Supprimer", "trash", "#e74c3c", "#c0392b",
            "#a93226", w=130, slot=self._on_delete_product
        )

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        return tab

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(38)
        if w:
            btn.setMinimumWidth(w)
        btn.setCursor(Qt.PointingHandCursor)
        px = load_svg_icon(icon_name, size=16)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 14px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: #aab7b8; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        self.products_table.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        row = index.row()
        if self.products_table.selectionModel().isRowSelected(row, index.parent()):
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectRow(row)
            self._last_selected_row = row

    def _on_search_barcode(self):
        barcode = self.external_barcode_input.text().strip()
        if barcode:
            self.search_barcode_requested.emit(barcode)

    def _on_save_product(self):
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
        data = {
            'name': self.product_name_input.text().strip(),
            'category': self.product_category_combo.currentText(),
            'price': self.product_price_input.text().strip(),
            'stock': self.product_stock_input.text().strip()
        }
        self.generate_internal_barcode_requested.emit(data)

    def _on_edit_product(self):
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = int(self.products_table.item(row, 0).text())
            self.edit_product_requested.emit(product_id)

    def _on_delete_product(self):
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = int(self.products_table.item(row, 0).text())
            self.delete_product_requested.emit(product_id)

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme."""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
        if self._is_dark:
            bg = "#1e1e2e"
            text = "#e0e0e0"
            border = "#3d3d5c"
            hover = "rgba(86, 123, 161, 0.20)"
            selection = "#4a6a8a"
            header_bg = "#2d2d44"
            scrollbar_bg = "#1e1e2e"
            scrollbar_handle = "#3d3d5c"
        else:
            bg = "#ffffff"
            text = "#2c3e50"
            border = "#bdc3c7"
            hover = "rgba(86, 123, 161, 0.10)"
            selection = "#7895b4"
            header_bg = "#567ba1"
            scrollbar_bg = "#d5d8dc"
            scrollbar_handle = "#aab7b8"

        # Style du tableau
        table_style = f"""
            QTableWidget#barcodeTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget#barcodeTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget#barcodeTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#barcodeTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget#barcodeTable::item:hover {{
                background-color: {hover};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid rgba(255,255,255,0.2);
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {scrollbar_bg};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {"#95a5a6" if not self._is_dark else "#4a6a8a"};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {scrollbar_bg};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scrollbar_handle};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {"#95a5a6" if not self._is_dark else "#4a6a8a"};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        self.products_table.setStyleSheet(table_style)

        # Style des autres composants
        if self._is_dark:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#scanGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #e0e0e0;
                }
                QGroupBox#scanGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QGroupBox#formGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #e0e0e0;
                }
                QGroupBox#formGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QGroupBox#previewGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #e0e0e0;
                }
                QGroupBox#previewGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QLabel#statusLabel {
                    color: #e0e0e0;
                }
                QLineEdit#barcodeInput, QLineEdit#productNameInput,
                QLineEdit#priceInput, QLineEdit#stockInput {
                    padding: 6px 10px;
                    border: 2px solid #3d3d5c;
                    border-radius: 6px;
                    font-size: 13px;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QLineEdit#barcodeInput:focus, QLineEdit#productNameInput:focus,
                QLineEdit#priceInput:focus, QLineEdit#stockInput:focus {
                    border-color: #567ba1;
                }
                QComboBox#categoryCombo {
                    padding: 6px 10px;
                    border: 2px solid #3d3d5c;
                    border-radius: 6px;
                    font-size: 13px;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QComboBox#categoryCombo:hover {
                    border-color: #567ba1;
                }
                QComboBox#categoryCombo QAbstractItemView {
                    background: #2d2d44;
                    color: #e0e0e0;
                    selection-background-color: #4a6a8a;
                    selection-color: white;
                    border: 2px solid #3d3d5c;
                }
                QTabWidget#barcodeTabs::pane {
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    padding: 10px 20px;
                    margin-right: 5px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QTabBar::tab:selected {
                    background: #567ba1;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #46648a;
                    color: white;
                }
                QLabel#barcodePreview {
                    background-color: #2d2d44;
                    border: 1px solid #3d3d5c;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLabel#barcodeValue {
                    color: #e0e0e0;
                }
            """)
        else:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#scanGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #2c3e50;
                }
                QGroupBox#scanGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QGroupBox#formGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #2c3e50;
                }
                QGroupBox#formGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QGroupBox#previewGroup {
                    font-size: 13px;
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 12px;
                    color: #2c3e50;
                }
                QGroupBox#previewGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 3px 10px;
                    color: #567ba1;
                }
                QLabel#statusLabel {
                    color: #7f8c8d;
                }
                QLineEdit#barcodeInput, QLineEdit#productNameInput,
                QLineEdit#priceInput, QLineEdit#stockInput {
                    padding: 6px 10px;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    font-size: 13px;
                    background: white;
                    color: #2c3e50;
                }
                QLineEdit#barcodeInput:focus, QLineEdit#productNameInput:focus,
                QLineEdit#priceInput:focus, QLineEdit#stockInput:focus {
                    border-color: #567ba1;
                }
                QComboBox#categoryCombo {
                    padding: 6px 10px;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    font-size: 13px;
                    background: white;
                    color: #2c3e50;
                }
                QComboBox#categoryCombo:hover {
                    border-color: #567ba1;
                }
                QComboBox#categoryCombo QAbstractItemView {
                    background: white;
                    color: #2c3e50;
                    selection-background-color: #7895b4;
                    selection-color: white;
                    border: 2px solid #bdc3c7;
                }
                QTabWidget#barcodeTabs::pane {
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                }
                QTabBar::tab {
                    padding: 10px 20px;
                    margin-right: 5px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    background: #aab7b8;
                    color: white;
                }
                QTabBar::tab:selected {
                    background: #567ba1;
                    color: white;
                }
                QTabBar::tab:hover {
                    background: #46648a;
                    color: white;
                }
                QLabel#barcodePreview {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLabel#barcodeValue {
                    color: #2c3e50;
                }
            """)

    # ========== API PUBLIQUE ==========

    def update_product_form(self, product_data: dict):
        """Met à jour le formulaire avec les données d'un produit."""
        self.product_id_hidden.setText(str(product_data.get('id', '')))
        self.external_barcode_input.setText(product_data.get('barcode', ''))
        self.product_name_input.setText(product_data.get('name', ''))
        
        category = product_data.get('category', 'Divers')
        idx = self.product_category_combo.findText(category)
        if idx >= 0:
            self.product_category_combo.setCurrentIndex(idx)
        
        self.product_price_input.setText(str(product_data.get('price', '0')))
        self.product_stock_input.setText(str(product_data.get('stock', '0')))

        if product_data.get('id'):
            self.save_product_btn.setText("Mettre a Jour")
            self.set_status_message(f"Produit trouve : <b>{product_data.get('name')}</b>")
        else:
            self.save_product_btn.setText("Ajouter Produit")
            self.set_status_message("Code-barres non trouve. Remplissez les details pour ajouter.")

    def clear_product_form(self):
        """Reinitialise le formulaire."""
        self.product_id_hidden.setText("")
        self.external_barcode_input.clear()
        self.product_name_input.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_price_input.clear()
        self.product_stock_input.clear()
        self.save_product_btn.setText("Ajouter Produit")
        self.scan_product_status.setText("Saisissez un code-barres pour rechercher un produit.")
        self.barcode_preview.clear()
        self.barcode_value_display.setText("<i>Code-barres affiche ici</i>")
        self.print_internal_btn.setEnabled(False)

    def update_barcode_preview(self, barcode_value: str, image_path: str):
        """Met à jour l'aperçu du code-barres."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaledToWidth(
                min(pixmap.width(), 400),
                Qt.SmoothTransformation
            )
            self.barcode_preview.setPixmap(scaled)
        self.barcode_value_display.setText(f"<b>{barcode_value}</b>")
        self.print_internal_btn.setEnabled(True)
        self.set_status_message(
            f"Code genere : <b>{barcode_value}</b> — cliquez sur Imprimer l'Etiquette pour l'imprimer.",
            is_error=False
        )

    def update_products_table(self, products: list):
        """Met à jour le tableau de l'onglet Audit."""
        self.products_table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            self.products_table.setItem(row_idx, 0, QTableWidgetItem(str(product['id'])))
            self.products_table.setItem(row_idx, 1, QTableWidgetItem(product.get('barcode', '')))
            self.products_table.setItem(row_idx, 2, QTableWidgetItem(product.get('name', '')))
            self.products_table.setItem(row_idx, 3, QTableWidgetItem(product.get('category', '')))
            self.products_table.setItem(row_idx, 4, QTableWidgetItem(f"{product.get('price', 0):.2f}"))
            self.products_table.setItem(row_idx, 5, QTableWidgetItem(str(product.get('stock', 0))))
            is_internal = product.get('is_internal_barcode', False)
            self.products_table.setItem(row_idx, 6, QTableWidgetItem("Oui" if is_internal else "Non"))

    def set_status_message(self, message: str, is_error: bool = False):
        """Affiche un message de statut coloré."""
        color = "#c0392b" if is_error else "#27ae60"
        self.scan_product_status.setText(f"<span style='color:{color};'>{message}</span>")

    def switch_to_audit_tab(self):
        """Bascule vers l'onglet Audit."""
        self.tab_widget.setCurrentIndex(1)