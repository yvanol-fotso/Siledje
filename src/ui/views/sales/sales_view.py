"""
Vue Point de Vente — FileView / Accueil style.
Tables = ThemedTable, boutons = CustomButton, titres GroupBox = teal dark.
Champs recherche/combo : palette forcée (Windows).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QGroupBox, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from src.ui.views.base.base_view import BaseView, Palette
from src.ui.widgets.custom_button import primary_btn, outline_btn, CustomButton
from src.ui.views.sales.sales_table import SalesProductsTable, SalesCartTable


class SalesView(BaseView):
    search_requested = Signal()
    type_filter_changed = Signal(object)
    add_to_cart_requested = Signal(int)
    remove_from_cart_requested = Signal(int)
    clear_cart_requested = Signal()
    checkout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent, title="Point de Vente", icon_name="shopping-cart")

        self.type_filter = None
        self.search_input = None
        self.products_table = None
        self.cart_table = None
        self.total_label = None
        self._last_selected_row = -1

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_search_section()
        self._init_products_table()
        self._init_cart_section()
        self._connect_signals()
        self._restyle_all_buttons()
        self._apply_theme_styles()
        self._force_inputs_theme()

    def _init_search_section(self):
        search_group = QGroupBox("Recherche Produit")
        search_group.setObjectName("searchGroup")

        layout = QHBoxLayout(search_group)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 10, 12, 10)

        self.type_filter = QComboBox()
        self.type_filter.setObjectName("filterCombo")
        self.type_filter.setMinimumHeight(34)
        self.type_filter.setMinimumWidth(160)
        self.type_filter.addItem("Tous types", None)
        self.type_filter.addItem("Unitaires (UNT)", "unitaire")
        self.type_filter.addItem("Paquets (PQT)", "paquet")
        self.type_filter.addItem("Cartons (CRT)", "carton")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Code-barres ou nom produit...")
        self.search_input.setMinimumHeight(34)

        search_btn = outline_btn("Rechercher", "search")
        search_btn.clicked.connect(lambda: self.search_requested.emit())

        layout.addWidget(self.type_filter)
        layout.addWidget(self.search_input, 1)
        layout.addWidget(search_btn)

        self.content_layout.addWidget(search_group)
        self._patch_combo_popup(self.type_filter)

    def _init_products_table(self):
        self.products_table = SalesProductsTable()
        self.products_table.clicked.connect(self._on_product_row_clicked)
        self.content_layout.addWidget(self.products_table, 3)

    def _init_cart_section(self):
        cart_group = QGroupBox("Panier Courant")
        cart_group.setObjectName("cartGroup")

        cart_layout = QVBoxLayout(cart_group)
        cart_layout.setSpacing(8)
        cart_layout.setContentsMargins(12, 10, 12, 10)

        self.cart_table = SalesCartTable()
        self.cart_table.setMinimumHeight(140)
        cart_layout.addWidget(self.cart_table, 1)

        self.total_label = QLabel("Total: 0 FCFA")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        cart_layout.addWidget(self.total_label)

        self.add_btn = primary_btn("Ajouter (F1)", "plus")
        self.add_btn.setShortcut("F1")
        self.add_btn.clicked.connect(self._on_add_clicked)

        self.remove_btn = outline_btn("Retirer (F2)", "minus")
        self.remove_btn.setShortcut("F2")
        self.remove_btn.clicked.connect(self._on_remove_clicked)

        self.clear_btn = outline_btn("Vider (F3)", "trash")
        self.clear_btn.setShortcut("F3")
        self.clear_btn.clicked.connect(lambda: self.clear_cart_requested.emit())

        self.checkout_btn = primary_btn("Paiement (F4)", "credit-card")
        self.checkout_btn.setShortcut("F4")
        self.checkout_btn.clicked.connect(lambda: self.checkout_requested.emit())

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        for btn in (self.add_btn, self.remove_btn, self.clear_btn, self.checkout_btn):
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(150)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Gauche : Ajouter + Retirer
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)

        btn_layout.addStretch()  # espace au centre

        # Droite : Vider + Paiement
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.checkout_btn)

        cart_layout.addLayout(btn_layout)
        self.content_layout.addWidget(cart_group, 2)

    def _connect_signals(self):
        self.search_input.returnPressed.connect(lambda: self.search_requested.emit())
        self.type_filter.currentIndexChanged.connect(
            lambda: self.type_filter_changed.emit(self.type_filter.currentData())
        )
        self.cart_table.clicked.connect(self._on_cart_row_clicked)

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

    def _on_cart_row_clicked(self, index):
        row = index.row()
        if self.cart_table.selectionModel().isRowSelected(row, index.parent()):
            self.cart_table.selectionModel().clearSelection()
            self.cart_table.selectionModel().clearCurrentIndex()
        else:
            self.cart_table.selectionModel().clearSelection()
            self.cart_table.selectRow(row)

    def _on_add_clicked(self):
        product_id = self.products_table.get_selected_product_id()
        if product_id is not None:
            self.add_to_cart_requested.emit(int(product_id))

    def _on_remove_clicked(self):
        product_id = self.cart_table.get_selected_product_id()
        if product_id is not None:
            self.remove_from_cart_requested.emit(int(product_id))

    # ========== THEME ==========

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        try:
            self.products_table.apply_theme(is_dark)
        except Exception as e:
            print(f"[SalesView] theme products: {e}")
        try:
            self.cart_table.apply_theme(is_dark)
        except Exception as e:
            print(f"[SalesView] theme cart: {e}")

        self._restyle_all_buttons()
        self._apply_theme_styles()
        self._force_inputs_theme()
        if self.type_filter is not None:
            self._style_combo_popup_now(self.type_filter)

    def _force_inputs_theme(self):
        """Windows ignore souvent le seul QSS → palette obligatoire."""
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        bg = QColor(colors["bg"])
        text = QColor(colors["text"])
        for w in (self.search_input, self.type_filter):
            if not w:
                continue
            pal = w.palette()
            pal.setColor(QPalette.Base, bg)
            pal.setColor(QPalette.Window, bg)
            pal.setColor(QPalette.Text, text)
            pal.setColor(QPalette.Button, bg)
            pal.setColor(QPalette.ButtonText, text)
            w.setPalette(pal)
            w.setAutoFillBackground(True)

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(150)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def _patch_combo_popup(self, combo: QComboBox):
        if getattr(combo, "_siledje_popup_patched", False):
            return
        original_show = combo.showPopup

        def themed_show_popup():
            original_show()
            self._style_combo_popup_now(combo)

        combo.showPopup = themed_show_popup
        combo._siledje_popup_patched = True

    def _style_combo_popup_now(self, combo: QComboBox):
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.SELECTION
        bg = QColor(colors["bg"])
        text = QColor(colors["text"])
        view = combo.view()
        if view is None:
            return
        pal = view.palette()
        pal.setColor(QPalette.Base, bg)
        pal.setColor(QPalette.Window, bg)
        pal.setColor(QPalette.Text, text)
        pal.setColor(QPalette.WindowText, text)
        pal.setColor(QPalette.Highlight, QColor(accent))
        pal.setColor(QPalette.HighlightedText, QColor("white"))
        view.setPalette(pal)
        view.setAutoFillBackground(True)
        view.setStyleSheet(f"""
            QAbstractItemView {{
                background-color: {colors['bg']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                outline: none;
            }}
            QAbstractItemView::item {{
                padding: 8px 12px; min-height: 26px; color: {colors['text']};
            }}
            QAbstractItemView::item:selected,
            QAbstractItemView::item:hover {{
                background-color: {accent};
                color: {"#2c3e50" if self._is_dark else "white"};
            }}
        """)
        view.viewport().setAutoFillBackground(True)
        view.viewport().setPalette(pal)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        total_bg = "rgba(26, 188, 156, 0.15)" if self._is_dark else "rgba(86, 123, 161, 0.08)"

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#searchGroup, QGroupBox#cartGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                color: {colors['text']};
                background: transparent;
                margin-top: 12px;
                padding-top: 14px;
            }}
            QGroupBox#searchGroup::title, QGroupBox#cartGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}
            QLabel#totalLabel {{
                padding: 8px 10px;
                border-radius: 6px;
                color: {accent};
                background-color: {total_bg};
            }}
            QLineEdit#searchInput {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                font-size: 13px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QLineEdit#searchInput:focus {{
                border-color: {accent};
            }}
            QComboBox#filterCombo {{
                font-size: 13px;
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                min-height: 34px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QComboBox#filterCombo:hover {{
                border-color: {accent};
            }}
            QComboBox#filterCombo::drop-down {{
                border: none;
                padding-right: 8px;
            }}
        """)

    # ========== API ==========

    def update_products_table(self, products: list):
        self.products_table.update_products(products)

    def update_cart_table(self, cart_items: list, total: float):
        self.cart_table.update_cart(cart_items)
        self.total_label.setText(f"Total: {total:.0f} FCFA")

    def get_search_term(self) -> str:
        return self.search_input.text().lower()

    def get_type_filter(self):
        return self.type_filter.currentData()