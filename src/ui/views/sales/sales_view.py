"""
Vue du point de vente - Interface utilisateur uniquement.
Herite de BaseView pour une structure coherente.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

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
        print(f"Erreur chargement icone {icon_name}: {e}")
        return QPixmap()


class SalesView(BaseView):
    """Vue du point de vente — Herite de BaseView."""

    search_requested = Signal()
    type_filter_changed = Signal(str)
    add_to_cart_requested = Signal(int)
    remove_from_cart_requested = Signal(int)
    clear_cart_requested = Signal()
    checkout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Point de Vente",
            icon_name="shopping-cart"
        )

        self.type_filter = None
        self.search_input = None
        self.products_table = None
        self.cart_table = None
        self.total_label = None
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
        self._init_search_section()
        self._init_products_table()
        self._init_cart_section()
        
        self._connect_signals()
        self._apply_theme_styles()

    def _init_search_section(self):
        """Section de recherche"""
        search_group = QGroupBox("Recherche Produit")
        search_group.setObjectName("searchGroup")

        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        label_filter = QLabel("Filtrer:")
        label_filter.setObjectName("filterLabel")

        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous types", None)
        self.type_filter.addItem("Unitaires (UNT)", "unitaire")
        self.type_filter.addItem("Paquets (PQT)", "paquet")
        self.type_filter.addItem("Cartons (CRT)", "carton")
        self.type_filter.setMinimumHeight(36)
        self.type_filter.setObjectName("filterCombo")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Code-barres ou nom produit...")
        self.search_input.setMinimumHeight(36)
        self.search_input.setObjectName("searchInput")

        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(36)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setObjectName("searchBtn")
        search_icon = load_svg_icon("search", size=16)
        search_btn.setIcon(QIcon(search_icon))
        search_btn.setIconSize(search_icon.size() if not search_icon.isNull() else QSize(16, 16))
        search_btn.clicked.connect(lambda: self.search_requested.emit())

        layout.addWidget(label_filter)
        layout.addWidget(self.type_filter)
        layout.addSpacerItem(QSpacerItem(15, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.search_input, 2)
        layout.addWidget(search_btn)

        search_group.setLayout(layout)
        self.content_layout.addWidget(search_group)

    def _init_products_table(self):
        """Tableau des produits"""
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["SKU", "Code-barres", "Nom", "Type", "Prix", "Stock"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.verticalHeader().setDefaultSectionSize(35)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.setAlternatingRowColors(False)
        self.products_table.setObjectName("productsTable")
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.content_layout.addWidget(self.products_table, 1)

    def _init_cart_section(self):
        """Section du panier"""
        cart_group = QGroupBox("Panier Courant")
        cart_group.setObjectName("cartGroup")

        cart_layout = QVBoxLayout()
        cart_layout.setSpacing(12)
        cart_layout.setContentsMargins(16, 16, 16, 16)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(
            ["SKU", "Code", "Nom", "Type", "Qte", "Sous-total"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.verticalHeader().setDefaultSectionSize(35)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)
        self.cart_table.setObjectName("cartTable")
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.total_label = QLabel("Total: 0 FCFA")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn = self._make_cart_btn(
            "Ajouter (F1)", "#2ecc71", "#27ae60", "#1e8449", "plus", self._on_add_clicked
        )
        self.remove_btn = self._make_cart_btn(
            "Retirer (F2)", "#f39c12", "#e67e22", "#d35400", "minus", self._on_remove_clicked
        )
        self.clear_btn = self._make_cart_btn(
            "Vider (F3)", "#95a5a6", "#7f8c8d", "#6c7a7a", "trash", 
            lambda: self.clear_cart_requested.emit()
        )
        self.checkout_btn = self._make_cart_btn(
            "Paiement (F4)", "#9b59b6", "#8e44ad", "#7d3c98", "credit-card", 
            lambda: self.checkout_requested.emit(), font_size=14
        )

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.checkout_btn)

        cart_layout.addWidget(self.cart_table)
        cart_layout.addWidget(self.total_label)
        cart_layout.addLayout(btn_layout)

        cart_group.setLayout(cart_layout)
        self.content_layout.addWidget(cart_group)

    def _make_cart_btn(self, label, color, hover, pressed, icon_name, 
                        slot=None, font_size=13) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        ico = load_svg_icon(icon_name, size=18)
        if not ico.isNull():
            btn.setIcon(QIcon(ico))
            btn.setIconSize(ico.size())
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        self.search_input.returnPressed.connect(lambda: self.search_requested.emit())
        self.type_filter.currentIndexChanged.connect(
            lambda: self.type_filter_changed.emit(self.type_filter.currentData())
        )
        self.products_table.clicked.connect(self._on_product_row_clicked)

    def _on_product_row_clicked(self, index):
        row = index.row()
        if self.products_table.selectionModel().isRowSelected(row, index.parent()):
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectRow(row)
            self._last_selected_row = row

    def _on_add_clicked(self):
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = self.products_table.item(row, 0).data(Qt.UserRole)
            if product_id is not None:
                self.add_to_cart_requested.emit(int(product_id))

    def _on_remove_clicked(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            product_id = self.cart_table.item(row, 0).data(Qt.UserRole)
            if product_id is not None:
                self.remove_from_cart_requested.emit(int(product_id))

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme (appele depuis le manager)"""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme"""
        # Couleurs en dur pour eviter les problemes d'import
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

        # Style des tables
        table_style = f"""
            QTableWidget {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableWidget::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableWidget::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableWidget::item:hover {{
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
        self.cart_table.setStyleSheet(table_style)

        # Style des groupes
        if self._is_dark:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#searchGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #e0e0e0;
                    background: transparent;
                }
                QGroupBox#searchGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #567ba1;
                }
                QGroupBox#cartGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #2ecc71;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #e0e0e0;
                    background: transparent;
                }
                QGroupBox#cartGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #2ecc71;
                }
                QLabel#filterLabel {
                    color: #e0e0e0;
                }
                QComboBox#filterCombo {
                    font-size: 14px;
                    padding: 6px 12px;
                    border: 2px solid #3d3d5c;
                    border-radius: 6px;
                    min-height: 34px;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QComboBox#filterCombo:hover {
                    border-color: #567ba1;
                }
                QComboBox#filterCombo::drop-down {
                    border: none;
                    padding-right: 8px;
                }
                QComboBox#filterCombo QAbstractItemView {
                    background: #2d2d44;
                    color: #e0e0e0;
                    selection-background-color: #4a6a8a;
                    selection-color: white;
                    border: 2px solid #3d3d5c;
                    border-radius: 6px;
                }
                QLineEdit#searchInput {
                    padding: 6px 12px;
                    border: 2px solid #3d3d5c;
                    border-radius: 6px;
                    font-size: 13px;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QLineEdit#searchInput:focus {
                    border-color: #567ba1;
                }
                QPushButton#searchBtn {
                    background-color: #567ba1;
                    color: white;
                    padding: 6px 14px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton#searchBtn:hover {
                    background-color: #46648a;
                }
                QLabel#totalLabel {
                    padding: 10px;
                    color: #e0e0e0;
                    background-color: rgba(86, 123, 161, 0.20);
                    border-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet(self.styleSheet() + """
                QGroupBox#searchGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #2c3e50;
                    background: transparent;
                }
                QGroupBox#searchGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #567ba1;
                }
                QGroupBox#cartGroup {
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #2ecc71;
                    border-radius: 8px;
                    margin-top: 14px;
                    padding-top: 18px;
                    color: #2c3e50;
                    background: transparent;
                }
                QGroupBox#cartGroup::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 4px 12px;
                    color: #2ecc71;
                }
                QLabel#filterLabel {
                    color: #2c3e50;
                }
                QComboBox#filterCombo {
                    font-size: 14px;
                    padding: 6px 12px;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    min-height: 34px;
                    background: white;
                    color: #2c3e50;
                }
                QComboBox#filterCombo:hover {
                    border-color: #567ba1;
                }
                QComboBox#filterCombo::drop-down {
                    border: none;
                    padding-right: 8px;
                }
                QComboBox#filterCombo QAbstractItemView {
                    background: white;
                    color: #2c3e50;
                    selection-background-color: #7895b4;
                    selection-color: white;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                }
                QLineEdit#searchInput {
                    padding: 6px 12px;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                    font-size: 13px;
                    background: white;
                    color: #2c3e50;
                }
                QLineEdit#searchInput:focus {
                    border-color: #567ba1;
                }
                QPushButton#searchBtn {
                    background-color: #567ba1;
                    color: white;
                    padding: 6px 14px;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton#searchBtn:hover {
                    background-color: #46648a;
                }
                QLabel#totalLabel {
                    padding: 10px;
                    color: #567ba1;
                    background-color: rgba(86, 123, 161, 0.10);
                    border-radius: 6px;
                }
            """)

    # ========== API PUBLIQUE ==========

    def update_products_table(self, products: list):
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            type_display = {
                "unitaire": "UNT", "paquet": "PQT", "carton": "CRT",
            }.get(product.get("type", ""), product.get("type", ""))

            sku_item = QTableWidgetItem(product.get("sku", ""))
            sku_item.setData(Qt.UserRole, product.get("id"))
            self.products_table.setItem(row, 0, sku_item)

            self.products_table.setItem(row, 1, QTableWidgetItem(product.get("barcode_test", "")))
            self.products_table.setItem(row, 2, QTableWidgetItem(product.get("name", "")))
            self.products_table.setItem(row, 3, QTableWidgetItem(type_display))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"{product.get('price', 0):.0f} FCFA"))
            self.products_table.setItem(row, 5, QTableWidgetItem(str(product.get("stock", 0))))

    def update_cart_table(self, cart_items: list, total: float):
        self.cart_table.setRowCount(len(cart_items))
        for row, item in enumerate(cart_items):
            product = item["product"]
            subtotal = product["price"] * item["quantity"]

            sku_item = QTableWidgetItem(product.get("sku", ""))
            sku_item.setData(Qt.UserRole, product.get("id"))
            self.cart_table.setItem(row, 0, sku_item)

            self.cart_table.setItem(row, 1, QTableWidgetItem(product.get("barcode_test", "")))
            self.cart_table.setItem(row, 2, QTableWidgetItem(product["name"]))
            self.cart_table.setItem(row, 3, QTableWidgetItem(item.get("type_display", "")))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(item["quantity"])))
            self.cart_table.setItem(row, 5, QTableWidgetItem(f"{subtotal:.0f} FCFA"))
        self.total_label.setText(f"Total: {total:.0f} FCFA")

    def get_search_term(self) -> str:
        return self.search_input.text().lower()

    def get_type_filter(self):
        return self.type_filter.currentData()