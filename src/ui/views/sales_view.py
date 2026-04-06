"""
Vue du point de vente - Interface utilisateur uniquement.
Séparation complète de la logique métier.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QComboBox, QGroupBox, QHeaderView, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


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
    painter.setBrush(QBrush(QColor("#3498db")))
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

        self.init_ui()

    # ── Construction de l'UI ──────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("shopping-cart", size=40))

        title = QLabel("Point de Vente")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Recherche
        main_layout.addWidget(self._create_search_group())

        # Tableau produits
        self.products_table = self._create_products_table()
        main_layout.addWidget(self.products_table)

        # Panier
        main_layout.addWidget(self._create_cart_group())

        self.setLayout(main_layout)
        self._connect_signals()

    def _create_search_group(self) -> QGroupBox:
        search_group = QGroupBox("Recherche Produit")
        search_group.setMaximumHeight(100)
        layout = QHBoxLayout()
        layout.setSpacing(10)

        label_filter = QLabel("Filtrer:")
        label_filter.setFixedWidth(50)

        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous types", None)
        self.type_filter.addItem("Unitaires (UNT)", "unitaire")
        self.type_filter.addItem("Paquets (PQT)", "paquet")
        self.type_filter.addItem("Cartons (CRT)", "carton")
        self.type_filter.setFixedWidth(180)
        self.type_filter.setMinimumHeight(36)
        self.type_filter.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 5px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Code-barres ou nom produit...")
        self.search_input.setMinimumWidth(280)
        self.search_input.setMinimumHeight(36)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #3498db; }
        """)

        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(36)
        search_btn.setFixedWidth(110)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_icon = load_svg_icon("search", size=16)
        search_btn.setIcon(QIcon(search_icon))
        search_btn.setIconSize(search_icon.size())
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                padding: 6px 14px; border: none;
                border-radius: 6px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; }
        """)
        search_btn.clicked.connect(lambda: self.search_requested.emit())

        layout.addWidget(label_filter)
        layout.addWidget(self.type_filter)
        layout.addSpacerItem(QSpacerItem(15, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(self.search_input)
        layout.addWidget(search_btn)

        search_group.setLayout(layout)
        return search_group

    def _create_products_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["ID", "Code-barres", "Nom", "Type", "Prix", "Stock"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(30)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #3498db; color: white;
                font-weight: bold; padding: 6px;
            }
        """)
        return table

    def _create_cart_group(self) -> QGroupBox:
        cart_group = QGroupBox("Panier Courant")
        cart_layout = QVBoxLayout()

        # Table panier
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(
            ["ID", "Code", "Nom", "Type", "Qté", "Sous-total"]
        )
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.verticalHeader().setDefaultSectionSize(30)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                border: 2px solid #2ecc71;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #2ecc71; color: white;
                font-weight: bold; padding: 6px;
            }
        """)

        # Total
        self.total_label = QLabel("Total: 0 FCFA")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("QLabel#totalLabel { padding: 10px; }")

        # Boutons d'action
        btn_layout = QHBoxLayout()

        self.add_btn = self._make_btn(
            "Ajouter (F1)", "#2ecc71", "#27ae60", "#1e8449", "plus"
        )
        self.remove_btn = self._make_btn(
            "Retirer (F2)", "#e67e22", "#d35400", "#ba4a00", "minus"
        )
        self.clear_btn = self._make_btn(
            "Vider (F3)", "#95a5a6", "#7f8c8d", "#707b7c", "trash"
        )
        self.checkout_btn = self._make_btn(
            "Paiement (F4)", "#9b59b6", "#8e44ad", "#7d3c98", "credit-card",
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
        btn.setMinimumHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        ico = load_svg_icon(icon_name, size=18)
        btn.setIcon(QIcon(ico))
        btn.setIconSize(ico.size())
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: white;
                padding: 10px 20px; border: none;
                border-radius: 6px; font-weight: bold; font-size: {font_size}px;
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