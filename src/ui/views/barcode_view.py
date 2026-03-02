"""
Vue de gestion des codes-barres - Interface utilisateur uniquement.
Séparation complète de la logique métier.
Responsive, Dark/Light, sans modal de confirmation.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGridLayout, QTabWidget, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QDoubleValidator, QIntValidator
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _placeholder(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _placeholder(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        return pixmap if not pixmap.isNull() else _placeholder(size, icon_name[0].upper())
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _placeholder(size, icon_name[0].upper())


def _placeholder(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#9b59b6")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class BarcodeView(QWidget):
    """Vue de gestion des codes-barres. Responsive, Dark/Light."""

    search_barcode_requested          = Signal(str)
    scan_barcode_requested            = Signal()
    save_product_requested            = Signal(dict)
    generate_internal_barcode_requested = Signal(dict)
    print_barcode_requested           = Signal()
    refresh_products_requested        = Signal()
    edit_product_requested            = Signal(int)
    delete_product_requested          = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.tab_widget              = None
        self.external_barcode_input  = None
        self.scan_product_status     = None
        self.product_id_hidden       = None
        self.product_name_input      = None
        self.product_category_combo  = None
        self.product_price_input     = None
        self.product_stock_input     = None
        self.save_product_btn        = None
        self.barcode_preview         = None
        self.barcode_value_display   = None
        self.print_internal_btn      = None
        self.products_table          = None

        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ── TITRE ────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(12)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setPixmap(load_svg_icon("package", size=40))
        title = QLabel("Gestion des Codes-Barres")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header.addWidget(icon_lbl)
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        # ─────────────────────────────────────────────────────────────

        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
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
            }
            QTabBar::tab:selected {
                background: #9b59b6;
                color: white;
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

        self.tab_widget.addTab(self._create_product_management_tab(), "Ajouter/Gérer Codes-Barres")
        self.tab_widget.addTab(self._create_audit_tab(), "Audit & Édition Produits")

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    # ──────────────────────────────────────────────────────────────────
    # ONGLET 1 : GESTION PRODUITS
    # ──────────────────────────────────────────────────────────────────

    def _create_product_management_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ── Recherche ────────────────────────────────────────────────
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit")
        scan_group.setStyleSheet(self._groupbox_style())
        scan_v = QVBoxLayout(scan_group)
        scan_v.setSpacing(8)

        scan_row = QHBoxLayout()
        scan_row.setSpacing(10)

        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText("Scannez ou saisissez un code-barres...")
        self.external_barcode_input.setMinimumHeight(38)
        self.external_barcode_input.setStyleSheet(self._input_style())
        self.external_barcode_input.returnPressed.connect(self._on_search_barcode)
        scan_row.addWidget(self.external_barcode_input, 1)

        search_btn = self._make_btn("Rechercher", "search", "#3498db", "#2980b9", "#21618c", w=130)
        search_btn.clicked.connect(self._on_search_barcode)
        scan_row.addWidget(search_btn)

        scan_btn = self._make_btn("Scanner", "scan", "#2196F3", "#1976D2", "#1565C0", w=120)
        scan_btn.clicked.connect(lambda: self.scan_barcode_requested.emit())
        scan_row.addWidget(scan_btn)

        scan_v.addLayout(scan_row)

        self.scan_product_status = QLabel("Saisissez un code-barres pour rechercher un produit.")
        self.scan_product_status.setWordWrap(True)
        self.scan_product_status.setStyleSheet("font-style: italic; color: #7f8c8d; padding: 2px 0;")
        scan_v.addWidget(self.scan_product_status)

        layout.addWidget(scan_group)

        # ── Détails produit — 2 colonnes bien espacées ───────────────
        form_group = QGroupBox("Détails du Produit")
        form_group.setStyleSheet(self._groupbox_style())
        form_group.setMinimumHeight(160)

        self.product_id_hidden = QLabel("")
        self.product_id_hidden.setVisible(False)

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nom du produit")
        self.product_name_input.setMinimumHeight(38)
        self.product_name_input.setStyleSheet(self._input_style())

        self.product_category_combo = QComboBox()
        self.product_category_combo.addItems(["Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"])
        self.product_category_combo.setMinimumHeight(38)
        self.product_category_combo.setStyleSheet(self._combo_style())

        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText("0.00")
        self.product_price_input.setValidator(QDoubleValidator(0, 99999.99, 2))
        self.product_price_input.setMinimumHeight(38)
        self.product_price_input.setStyleSheet(self._input_style())

        self.product_stock_input = QLineEdit()
        self.product_stock_input.setPlaceholderText("0")
        self.product_stock_input.setValidator(QIntValidator(0, 999999))
        self.product_stock_input.setMinimumHeight(38)
        self.product_stock_input.setStyleSheet(self._input_style())

        lbl_s = "font-size: 13px;"

        # ── CORRECTIF : espacement vertical augmenté ─────────────────
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(30)
        grid.setContentsMargins(20, 30, 20, 30)
        # ─────────────────────────────────────────────────────────────

        lbl_nom = QLabel("Nom :") ; lbl_nom.setStyleSheet(lbl_s)
        lbl_prix = QLabel("Prix unitaire :") ; lbl_prix.setStyleSheet(lbl_s)
        lbl_cat = QLabel("Catégorie :") ; lbl_cat.setStyleSheet(lbl_s)
        lbl_stock = QLabel("Stock :") ; lbl_stock.setStyleSheet(lbl_s)

        grid.addWidget(lbl_nom,                     0, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_name_input,     0, 1)
        grid.addWidget(lbl_cat,                     0, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_category_combo, 0, 3)

        grid.addWidget(lbl_prix,                    1, 0, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_price_input,    1, 1)
        grid.addWidget(lbl_stock,                   1, 2, Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(self.product_stock_input,    1, 3)

        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(3, 1)
        grid.setColumnMinimumWidth(0, 100)
        grid.setColumnMinimumWidth(2, 70)

        form_group.setLayout(grid)
        layout.addWidget(form_group)

        # ── Boutons d'action ─────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.save_product_btn = self._make_btn("Ajouter Produit", "plus-circle", "#28a745", "#218838", "#1e7e34", w=160)
        self.save_product_btn.clicked.connect(self._on_save_product)
        btn_row.addWidget(self.save_product_btn)

        gen_btn = self._make_btn("Générer Code Interne", "barcode", "#9b59b6", "#8e44ad", "#7d3c98", w=180)
        gen_btn.clicked.connect(self._on_generate_internal)
        btn_row.addWidget(gen_btn)

        layout.addLayout(btn_row)

        # ── Aperçu code-barres ───────────────────────────────────────
        preview_group = QGroupBox("Aperçu du Code-Barres")
        preview_group.setStyleSheet(self._groupbox_style())
        preview_v = QVBoxLayout(preview_group)
        preview_v.setSpacing(8)

        self.barcode_preview = QLabel()
        self.barcode_preview.setAlignment(Qt.AlignCenter)
        self.barcode_preview.setMinimumHeight(100)
        self.barcode_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.barcode_preview.setStyleSheet("""
            background-color: white;
            border: 1px solid rgba(150,150,150,0.3);
            border-radius: 6px;
            padding: 8px;
        """)
        preview_v.addWidget(self.barcode_preview)

        self.barcode_value_display = QLabel("<i>Code-barres affiché ici</i>")
        self.barcode_value_display.setAlignment(Qt.AlignCenter)
        self.barcode_value_display.setFont(QFont("Courier New", 12))
        preview_v.addWidget(self.barcode_value_display)

        self.print_internal_btn = self._make_btn("Imprimer l'Étiquette", "printer", "#17a2b8", "#138496", "#117a8b")
        self.print_internal_btn.setEnabled(False)
        self.print_internal_btn.clicked.connect(lambda: self.print_barcode_requested.emit())
        preview_v.addWidget(self.print_internal_btn)

        layout.addWidget(preview_group)
        layout.addStretch()

        return tab

    # ──────────────────────────────────────────────────────────────────
    # ONGLET 2 : AUDIT — même style que stock_view
    # ──────────────────────────────────────────────────────────────────

    def _create_audit_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Tableau
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Code-Barres", "Nom", "Catégorie", "Prix", "Stock", "Interne"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.setAlternatingRowColors(False)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.products_table.verticalHeader().setDefaultSectionSize(38)

        self.products_table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                font-weight: normal;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }
            QTableWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(155, 89, 182, 0.10);
            }
            QHeaderView::section {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid #8e44ad;
            }
            QHeaderView::section:last { border-right: none; }
            QScrollBar:vertical {
                border: none; background: transparent;
                width: 12px; border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60; min-height: 20px; border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #2ecc71; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal {
                border: none;
                background: rgba(150, 150, 150, 0.15);
                height: 10px; border-radius: 5px; margin-bottom: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #27ae60; min-width: 30px; border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover { background: #2ecc71; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """)

        layout.addWidget(self.products_table, 1)

        # Boutons d'action
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = self._make_btn("Actualiser", "refresh", "#95a5a6", "#7f8c8d", "#707b7c", w=130)
        refresh_btn.clicked.connect(lambda: self.refresh_products_requested.emit())
        btn_row.addWidget(refresh_btn)

        edit_btn = self._make_btn("Éditer", "edit", "#f39c12", "#e67e22", "#d35400", w=130)
        edit_btn.clicked.connect(self._on_edit_product)
        btn_row.addWidget(edit_btn)

        delete_btn = self._make_btn("Supprimer", "trash", "#e74c3c", "#c0392b", "#a93226", w=130)
        delete_btn.clicked.connect(self._on_delete_product)
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        return tab

    # ──────────────────────────────────────────────────────────────────
    # STYLES PARTAGÉS
    # ──────────────────────────────────────────────────────────────────

    def _groupbox_style(self) -> str:
        return """
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 10px;
                color: #3498db;
                font-weight: bold;
            }
        """

    def _input_style(self) -> str:
        return """
            QLineEdit {
                padding: 6px 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus { border-color: #9b59b6; }
        """

    def _combo_style(self) -> str:
        return """
            QComboBox {
                padding: 6px 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
            }
            QComboBox:hover { border-color: #9b59b6; }
            QComboBox::drop-down { border: none; padding-right: 8px; }
        """

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None) -> QPushButton:
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
            QPushButton:disabled {{ background-color: #95a5a6; }}
        """)
        return btn

    # ──────────────────────────────────────────────────────────────────
    # SLOTS INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _on_search_barcode(self):
        barcode = self.external_barcode_input.text().strip()
        if barcode:
            self.search_barcode_requested.emit(barcode)

    def _on_save_product(self):
        data = {
            'id':       self.product_id_hidden.text(),
            'barcode':  self.external_barcode_input.text().strip(),
            'name':     self.product_name_input.text().strip(),
            'category': self.product_category_combo.currentText(),
            'price':    self.product_price_input.text().strip(),
            'stock':    self.product_stock_input.text().strip()
        }
        self.save_product_requested.emit(data)

    def _on_generate_internal(self):
        data = {
            'name':     self.product_name_input.text().strip(),
            'category': self.product_category_combo.currentText(),
            'price':    self.product_price_input.text().strip(),
            'stock':    self.product_stock_input.text().strip()
        }
        # Émettre directement — pas de modal
        self.generate_internal_barcode_requested.emit(data)

    def _on_edit_product(self):
        rows = self.products_table.selectionModel().selectedRows()
        if rows:
            product_id = int(self.products_table.item(rows[0].row(), 0).text())
            self.edit_product_requested.emit(product_id)

    def _on_delete_product(self):
        rows = self.products_table.selectionModel().selectedRows()
        if rows:
            product_id = int(self.products_table.item(rows[0].row(), 0).text())
            self.delete_product_requested.emit(product_id)

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

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
            self.set_status_message(f"Produit trouvé : <b>{product_data.get('name')}</b>")
        else:
            self.save_product_btn.setText("Ajouter Produit")
            self.set_status_message("Code-barres non trouvé. Remplissez les détails pour ajouter.")

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
        """
        Met à jour l'aperçu du code-barres directement dans la vue.
        Pas de modal — le code s'affiche immédiatement et reste visible.
        """
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
            f"Code généré : <b>{barcode_value}</b> — cliquez sur Imprimer l'Étiquette pour l'imprimer.",
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
        color = "#e74c3c" if is_error else "#27ae60"
        self.scan_product_status.setText(f"<span style='color:{color};'>{message}</span>")

    def switch_to_audit_tab(self):
        """Bascule vers l'onglet Audit (utile après un ajout réussi)."""
        self.tab_widget.setCurrentIndex(1)