"""
Vue codes-barres — unifiée.
CustomButton + ThemedTable + Palette (pas de CSS local massif).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QTabWidget, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QDoubleValidator, QIntValidator

from src.ui.views.base.base_view import BaseView
from src.ui.views.base.palette import Palette
from src.ui.widgets.custom_button import (
    primary_btn, success_btn, warning_btn, danger_btn,
    outline_btn, info_btn, CustomButton,
)
from src.ui.views.barcode.barcode_table import BarcodeProductsTable


class BarcodeView(BaseView):
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
            icon_name="package",
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

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_tabs()
        self._connect_signals()
        self._restyle_all_buttons()
        self._apply_theme_styles()

    # ──────────────────────────────────────────────
    # Onglets
    # ──────────────────────────────────────────────

    def _init_tabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("barcodeTabs")
        self.tab_widget.addTab(
            self._create_product_management_tab(),
            "Ajouter/Gerer Codes-Barres",
        )
        self.tab_widget.addTab(
            self._create_audit_tab(),
            "Audit & Edition Produits",
        )
        self.content_layout.addWidget(self.tab_widget)

    def _create_product_management_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Recherche
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit")
        scan_group.setObjectName("scanGroup")
        scan_v = QVBoxLayout(scan_group)
        scan_v.setSpacing(8)

        scan_row = QHBoxLayout()
        scan_row.setSpacing(10)

        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText(
            "Scannez ou saisissez un code-barres..."
        )
        self.external_barcode_input.setMinimumHeight(38)
        self.external_barcode_input.setObjectName("barcodeInput")
        self.external_barcode_input.returnPressed.connect(self._on_search_barcode)

        search_btn = primary_btn("Rechercher", "search", self._on_search_barcode)
        search_btn.setMinimumWidth(130)
        search_btn.setMinimumHeight(38)

        scan_btn = info_btn(
            "Scanner", "scan",
            lambda: self.scan_barcode_requested.emit(),
        )
        scan_btn.setMinimumWidth(120)
        scan_btn.setMinimumHeight(38)

        scan_row.addWidget(self.external_barcode_input, 1)
        scan_row.addWidget(search_btn)
        scan_row.addWidget(scan_btn)
        scan_v.addLayout(scan_row)

        self.scan_product_status = QLabel(
            "Saisissez un code-barres pour rechercher un produit."
        )
        self.scan_product_status.setWordWrap(True)
        self.scan_product_status.setObjectName("statusLabel")
        scan_v.addWidget(self.scan_product_status)
        layout.addWidget(scan_group)

        # Formulaire
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
        self.product_category_combo.addItems([
            "Papeterie", "Fournitures", "Vetements", "Livres", "Divers",
        ])
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
        grid.setVerticalSpacing(24)
        grid.setContentsMargins(20, 24, 20, 24)

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

        # Actions produit
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.save_product_btn = success_btn(
            "Ajouter Produit", "plus-circle", self._on_save_product
        )
        self.save_product_btn.setMinimumWidth(160)
        self.save_product_btn.setMinimumHeight(38)

        gen_btn = primary_btn(
            "Generer Code Interne", "barcode", self._on_generate_internal
        )
        gen_btn.setMinimumWidth(180)
        gen_btn.setMinimumHeight(38)

        btn_row.addWidget(self.save_product_btn)
        btn_row.addWidget(gen_btn)
        layout.addLayout(btn_row)

        # Aperçu
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

        self.print_internal_btn = info_btn(
            "Imprimer l'Etiquette", "printer",
            lambda: self.print_barcode_requested.emit(),
        )
        self.print_internal_btn.setMinimumWidth(180)
        self.print_internal_btn.setMinimumHeight(38)
        self.print_internal_btn.setEnabled(False)
        preview_v.addWidget(self.print_internal_btn, 0, Qt.AlignLeft)

        layout.addWidget(preview_group)
        layout.addStretch()
        return tab

    def _create_audit_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        self.products_table = BarcodeProductsTable()
        self.products_table.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        layout.addWidget(self.products_table, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = outline_btn(
            "Actualiser", "refresh",
            lambda: self.refresh_products_requested.emit(),
        )
        refresh_btn.setMinimumWidth(130)
        refresh_btn.setMinimumHeight(38)

        edit_btn = warning_btn("Editer", "edit", self._on_edit_product)
        edit_btn.setMinimumWidth(130)
        edit_btn.setMinimumHeight(38)

        delete_btn = danger_btn("Supprimer", "trash", self._on_delete_product)
        delete_btn.setMinimumWidth(130)
        delete_btn.setMinimumHeight(38)

        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return tab

    def _connect_signals(self):
        if self.products_table is not None:
            self.products_table.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        row = index.row()
        sm = self.products_table.selectionModel()
        if sm.isRowSelected(row, index.parent()):
            sm.clearSelection()
            sm.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            sm.clearSelection()
            self.products_table.selectRow(row)
            self._last_selected_row = row

    def _on_search_barcode(self):
        barcode = self.external_barcode_input.text().strip()
        if barcode:
            self.search_barcode_requested.emit(barcode)

    def _on_save_product(self):
        data = {
            "id": self.product_id_hidden.text(),
            "barcode": self.external_barcode_input.text().strip(),
            "name": self.product_name_input.text().strip(),
            "category": self.product_category_combo.currentText(),
            "price": self.product_price_input.text().strip(),
            "stock": self.product_stock_input.text().strip(),
        }
        self.save_product_requested.emit(data)

    def _on_generate_internal(self):
        data = {
            "name": self.product_name_input.text().strip(),
            "category": self.product_category_combo.currentText(),
            "price": self.product_price_input.text().strip(),
            "stock": self.product_stock_input.text().strip(),
        }
        self.generate_internal_barcode_requested.emit(data)

    def _on_edit_product(self):
        pid = self.products_table.get_selected_product_id()
        if pid is not None:
            self.edit_product_requested.emit(pid)

    def _on_delete_product(self):
        pid = self.products_table.get_selected_product_id()
        if pid is not None:
            self.delete_product_requested.emit(pid)

    # ──────────────────────────────────────────────
    # Thème
    # ──────────────────────────────────────────────

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        if self.products_table is not None:
            try:
                self.products_table.apply_theme(is_dark)
            except Exception as e:
                print(f"[BarcodeView] theme table: {e}")
        self._restyle_all_buttons()
        self._apply_theme_styles()

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)
            btn.setMinimumHeight(38)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        muted = "#b0b8c0" if self._is_dark else Palette.MUTED_TEXT

        self.setStyleSheet(self.styleSheet() + f"""
            QGroupBox#scanGroup,
            QGroupBox#formGroup,
            QGroupBox#previewGroup {{
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                color: {colors['text']};
                background: transparent;
            }}
            QGroupBox#scanGroup::title,
            QGroupBox#formGroup::title,
            QGroupBox#previewGroup::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}
            QLabel#statusLabel {{
                color: {muted};
            }}
            QLineEdit#barcodeInput,
            QLineEdit#productNameInput,
            QLineEdit#priceInput,
            QLineEdit#stockInput,
            QComboBox#categoryCombo {{
                padding: 6px 10px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                font-size: 13px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QLineEdit#barcodeInput:focus,
            QLineEdit#productNameInput:focus,
            QLineEdit#priceInput:focus,
            QLineEdit#stockInput:focus,
            QComboBox#categoryCombo:hover {{
                border-color: {accent};
            }}
            QComboBox#categoryCombo QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {Palette.SELECTION};
                selection-color: white;
            }}
            QTabWidget#barcodeTabs::pane {{
                border: none;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {muted};
                padding: 8px 18px;
                margin-right: 2px;
                border-bottom: 3px solid transparent;
                font-weight: 600;
                font-size: 13px;
            }}
            QTabBar::tab:selected {{
                color: {accent};
                border-bottom: 3px solid {accent};
            }}
            QTabBar::tab:hover {{
                color: {accent};
            }}
            QLabel#barcodePreview {{
                background-color: {colors['bg']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}
            QLabel#barcodeValue {{
                color: {colors['text']};
            }}
        """)

    # ──────────────────────────────────────────────
    # API publique
    # ──────────────────────────────────────────────

    def update_product_form(self, product_data: dict):
        self.product_id_hidden.setText(str(product_data.get("id", "")))
        self.external_barcode_input.setText(product_data.get("barcode", ""))
        self.product_name_input.setText(product_data.get("name", ""))

        category = product_data.get("category", "Divers")
        idx = self.product_category_combo.findText(category)
        if idx >= 0:
            self.product_category_combo.setCurrentIndex(idx)

        self.product_price_input.setText(str(product_data.get("price", "0")))
        self.product_stock_input.setText(str(product_data.get("stock", "0")))

        if product_data.get("id"):
            self.save_product_btn.setText("Mettre a Jour")
            self.set_status_message(
                f"Produit trouve : <b>{product_data.get('name')}</b>"
            )
        else:
            self.save_product_btn.setText("Ajouter Produit")
            self.set_status_message(
                "Code-barres non trouve. Remplissez les details pour ajouter."
            )

    def clear_product_form(self):
        self.product_id_hidden.setText("")
        self.external_barcode_input.clear()
        self.product_name_input.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_price_input.clear()
        self.product_stock_input.clear()
        self.save_product_btn.setText("Ajouter Produit")
        self.scan_product_status.setText(
            "Saisissez un code-barres pour rechercher un produit."
        )
        self.barcode_preview.clear()
        self.barcode_value_display.setText("<i>Code-barres affiche ici</i>")
        self.print_internal_btn.setEnabled(False)

    def update_barcode_preview(self, barcode_value: str, image_path: str):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaledToWidth(
                min(pixmap.width(), 400), Qt.SmoothTransformation
            )
            self.barcode_preview.setPixmap(scaled)
        self.barcode_value_display.setText(f"<b>{barcode_value}</b>")
        self.print_internal_btn.setEnabled(True)
        self.set_status_message(
            f"Code genere : <b>{barcode_value}</b> — "
            "cliquez sur Imprimer l'Etiquette pour l'imprimer.",
            is_error=False,
        )

    def update_products_table(self, products: list):
        self.products_table.set_products(products)

    def set_status_message(self, message: str, is_error: bool = False):
        color = Palette.DANGER if is_error else Palette.SUCCESS
        self.scan_product_status.setText(
            f"<span style='color:{color};'>{message}</span>"
        )

    def switch_to_audit_tab(self):
        self.tab_widget.setCurrentIndex(1)