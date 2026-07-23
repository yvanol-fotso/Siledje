"""
Vue du point de vente - Interface utilisateur uniquement.
Séparation complète de la logique métier.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


# ──────────────────────────────────────────────────────────────────
# PALETTE CENTRALISÉE (une seule source de vérité pour les couleurs)
# ──────────────────────────────────────────────────────────────────
class Palette:
    ACCENT          = "#567ba1"   # en-têtes, focus des champs
    ACCENT_HOVER    = "#46648a"   # survol des en-têtes / boutons liés à l'accent
    ACCENT_PRESSED  = "#3a5470"
    SELECTION       = "#7895b4"   # couleur unique de sélection/désélection de ligne
    ROW_HOVER       = "rgba(86, 123, 161, 0.10)"  # survol léger d'une ligne (dérivé de l'accent)
    BORDER_GRAY     = "#bdc3c7"
    SCROLLBAR_BG    = "#d5d8dc"   # Fond de la scrollbar (gris clair)
    SCROLLBAR_HANDLE = "#aab7b8"  # Poignée de la scrollbar (gris)
    SCROLLBAR_HOVER = "#95a5a6"   # Poignée survolée (gris plus foncé)
    BASE_WHITE      = "#ffffff"
    SUCCESS         = "#2ecc71"   # Vert pour le panier
    SUCCESS_HOVER   = "#27ae60"
    SUCCESS_PRESSED = "#1e8449"
    WARNING         = "#f39c12"   # Orange pour modifier
    WARNING_HOVER   = "#e67e22"
    WARNING_PRESSED = "#d35400"
    DANGER          = "#e74c3c"   # Rouge pour supprimer
    DANGER_HOVER    = "#c0392b"
    DANGER_PRESSED  = "#a93226"
    PURPLE          = "#9b59b6"   # Violet pour paiement
    PURPLE_HOVER    = "#8e44ad"
    PURPLE_PRESSED  = "#7d3c98"


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS ICÔNES
# ──────────────────────────────────────────────────────────────────────────────

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
        print(f"Erreur chargement icône {icon_name}: {e}")
        return create_placeholder_pixmap(size, icon_name[0].upper())


def create_placeholder_pixmap(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(Palette.ACCENT)))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    font = QFont("Segoe UI", int(size * 0.5), QFont.Bold)
    painter.setFont(font)
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


# ──────────────────────────────────────────────────────────────────────────────
# VUE PRINCIPALE
# ──────────────────────────────────────────────────────────────────────────────

class SalesView(QWidget):
    """
    Vue du point de vente — Affichage uniquement.
    Émet des signaux pour communiquer avec le manager.
    """

    # Signaux vers le manager
    search_requested = Signal()
    type_filter_changed = Signal(str)
    add_to_cart_requested = Signal(int)
    remove_from_cart_requested = Signal(int)
    clear_cart_requested = Signal()
    checkout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.type_filter = None
        self.search_input = None
        self.products_table = None
        self.cart_table = None
        self.total_label = None
        self._last_selected_row = -1

        self.init_ui()

    # ── Construction de l'UI ──────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("shopping-cart", size=40))

        title = QLabel("Point de Vente")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: bold;
            color: {Palette.ACCENT};
        """)

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Recherche
        main_layout.addWidget(self._create_search_group())

        # Tableau produits
        self.products_table = self._create_products_table()
        main_layout.addWidget(self.products_table, 1)

        # Panier
        main_layout.addWidget(self._create_cart_group())

        self.setLayout(main_layout)
        self._connect_signals()

    def _create_search_group(self) -> QGroupBox:
        search_group = QGroupBox("Recherche Produit")
        search_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        label_filter = QLabel("Filtrer:")
        label_filter.setStyleSheet("font-size: 14px; font-weight: normal;")

        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous types", None)
        self.type_filter.addItem("Unitaires (UNT)", "unitaire")
        self.type_filter.addItem("Paquets (PQT)", "paquet")
        self.type_filter.addItem("Cartons (CRT)", "carton")
        self.type_filter.setMinimumHeight(36)
        self.type_filter.setStyleSheet(f"""
            QComboBox {{
                font-size: 14px;
                padding: 6px 12px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
            }}
            QComboBox:hover {{ border-color: {Palette.ACCENT}; }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
        """)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Code-barres ou nom produit...")
        self.search_input.setMinimumHeight(36)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 12px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Palette.ACCENT}; }}
        """)

        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(36)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_icon = load_svg_icon("search", size=16)
        search_btn.setIcon(QIcon(search_icon))
        search_btn.setIconSize(search_icon.size())
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Palette.ACCENT};
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {Palette.ACCENT_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.ACCENT_PRESSED}; }}
        """)
        search_btn.clicked.connect(lambda: self.search_requested.emit())

        layout.addWidget(label_filter)
        layout.addWidget(self.type_filter)
        layout.addSpacerItem(QSpacerItem(15, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.search_input, 2)
        layout.addWidget(search_btn)

        search_group.setLayout(layout)
        return search_group

    def _create_products_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "Code-barres", "Nom", "Type", "Prix", "Stock"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(35)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setObjectName("productsTable")
        # Désactiver l'édition
        table.setEditTriggers(QTableWidget.NoEditTriggers)

        table.setStyleSheet(f"""
            QTableWidget#productsTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableWidget#productsTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }}
            QTableWidget#productsTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#productsTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#productsTable::item:hover {{
                background-color: {Palette.ROW_HOVER};
            }}
            QHeaderView::section {{
                background-color: {Palette.ACCENT};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{ border-right: none; }}
            
            /* ===== SCROLLBARS GRISES ===== */
            QScrollBar:vertical {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
        
        return table

    def _create_cart_group(self) -> QGroupBox:
        cart_group = QGroupBox("Panier Courant")
        cart_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {Palette.SUCCESS};
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: {Palette.SUCCESS};
            }}
        """)
        
        cart_layout = QVBoxLayout()
        cart_layout.setSpacing(12)
        cart_layout.setContentsMargins(16, 16, 16, 16)

        # Table panier
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(
            ["ID", "Code", "Nom", "Type", "Qté", "Sous-total"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.verticalHeader().setDefaultSectionSize(35)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)
        self.cart_table.setObjectName("cartTable")
        # Désactiver l'édition
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.cart_table.setStyleSheet(f"""
            QTableWidget#cartTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.SUCCESS};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableWidget#cartTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }}
            QTableWidget#cartTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#cartTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#cartTable::item:hover {{
                background-color: {Palette.ROW_HOVER};
            }}
            QHeaderView::section {{
                background-color: {Palette.SUCCESS};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {Palette.SUCCESS_HOVER};
            }}
            QHeaderView::section:last {{ border-right: none; }}
            
            /* ===== SCROLLBARS GRISES ===== */
            QScrollBar:vertical {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {Palette.SCROLLBAR_BG};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Palette.SCROLLBAR_HANDLE};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Palette.SCROLLBAR_HOVER};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

        # Total
        self.total_label = QLabel("Total: 0 FCFA")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet(f"""
            QLabel#totalLabel {{ 
                padding: 10px;
                color: {Palette.ACCENT};
                background-color: {Palette.ROW_HOVER};
                border-radius: 6px;
            }}
        """)

        # Boutons d'action
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.add_btn = self._make_btn(
            "Ajouter (F1)", Palette.SUCCESS, Palette.SUCCESS_HOVER, 
            Palette.SUCCESS_PRESSED, "plus"
        )
        self.remove_btn = self._make_btn(
            "Retirer (F2)", Palette.WARNING, Palette.WARNING_HOVER, 
            Palette.WARNING_PRESSED, "minus"
        )
        self.clear_btn = self._make_btn(
            "Vider (F3)", Palette.SCROLLBAR_HANDLE, Palette.SCROLLBAR_HOVER, 
            "#7f8c8d", "trash"
        )
        self.checkout_btn = self._make_btn(
            "Paiement (F4)", Palette.PURPLE, Palette.PURPLE_HOVER, 
            Palette.PURPLE_PRESSED, "credit-card",
            font_size=14,
        )

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.checkout_btn)

        cart_layout.addWidget(self.cart_table)
        cart_layout.addWidget(self.total_label)
        cart_layout.addLayout(btn_layout)

        cart_group.setLayout(cart_layout)
        return cart_group

    def _make_btn(
        self,
        label: str,
        color: str,
        hover: str,
        pressed: str,
        icon_name: str,
        font_size: int = 13,
    ) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        ico = load_svg_icon(icon_name, size=18)
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
        return btn

    # ── Connexions internes ───────────────────────────────────────

    def _connect_signals(self):
        self.search_input.returnPressed.connect(lambda: self.search_requested.emit())
        self.type_filter.currentIndexChanged.connect(
            lambda: self.type_filter_changed.emit(self.type_filter.currentData())
        )
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        self.clear_btn.clicked.connect(lambda: self.clear_cart_requested.emit())
        self.checkout_btn.clicked.connect(lambda: self.checkout_requested.emit())

        # Connexion pour la sélection/désélection du tableau produits
        self.products_table.clicked.connect(self._on_product_row_clicked)

    def _on_product_row_clicked(self, index):
        """
        Gère le toggle sélection/désélection pour le tableau des produits :
        - Si la ligne est déjà sélectionnée -> on la désélectionne
        - Si la ligne n'est pas sélectionnée -> on la sélectionne
        """
        row = index.row()
        
        # Vérifier si la ligne est déjà sélectionnée
        if self.products_table.selectionModel().isRowSelected(row, index.parent()):
            # Désélectionner la ligne
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectionModel().clearCurrentIndex()
            self._last_selected_row = -1
        else:
            # Sélectionner la ligne (efface la sélection précédente)
            self.products_table.selectionModel().clearSelection()
            self.products_table.selectRow(row)
            self._last_selected_row = row

    def _on_add_clicked(self):
        row = self.products_table.currentRow()
        if row >= 0:
            product_id = int(self.products_table.item(row, 0).text())
            self.add_to_cart_requested.emit(product_id)

    def _on_remove_clicked(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            product_id = int(self.cart_table.item(row, 0).text())
            self.remove_from_cart_requested.emit(product_id)

    # ── API publique pour le manager ─────────────────────────────

    def update_products_table(self, products: list):
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            type_display = {
                "unitaire": "UNT", "paquet": "PQT", "carton": "CRT",
            }.get(product.get("type", ""), product.get("type", ""))

            self.products_table.setItem(row, 0, QTableWidgetItem(str(product.get("id", ""))))
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
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(product["barcode_test"]))
            self.cart_table.setItem(row, 2, QTableWidgetItem(product["name"]))
            self.cart_table.setItem(row, 3, QTableWidgetItem(item["type_display"]))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(item["quantity"])))
            self.cart_table.setItem(row, 5, QTableWidgetItem(f"{subtotal:.0f} FCFA"))
        self.total_label.setText(f"Total: {total:.0f} FCFA")

    def get_search_term(self) -> str:
        return self.search_input.text().lower()

    def get_type_filter(self):
        return self.type_filter.currentData()