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
    
    # Couleurs supplémentaires pour les boutons
    SUCCESS         = "#2ecc71"   # Vert
    SUCCESS_HOVER   = "#27ae60"
    SUCCESS_PRESSED = "#1e8449"
    INFO            = "#3498db"   # Bleu
    INFO_HOVER      = "#2980b9"
    INFO_PRESSED    = "#21618c"
    WARNING         = "#f39c12"   # Orange
    WARNING_HOVER   = "#e67e22"
    WARNING_PRESSED = "#d35400"
    DANGER          = "#e74c3c"   # Rouge
    DANGER_HOVER    = "#c0392b"
    DANGER_PRESSED  = "#a93226"
    PURPLE          = "#9b59b6"   # Violet
    PURPLE_HOVER    = "#8e44ad"
    PURPLE_PRESSED  = "#7d3c98"
    TEAL            = "#17a2b8"   # Turquoise
    TEAL_HOVER      = "#138496"
    TEAL_PRESSED    = "#117a8b"


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS ICÔNES
# ──────────────────────────────────────────────────────────────────────────────

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
    painter.setBrush(QBrush(QColor(Palette.ACCENT)))
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
        self._last_selected_row      = -1

        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ── TITRE ────────────────────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(12)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setPixmap(load_svg_icon("package", size=40))
        title = QLabel("Gestion des Codes-Barres")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: bold;
            color: {Palette.ACCENT};
        """)
        header.addWidget(icon_lbl)
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)
        # ─────────────────────────────────────────────────────────────

        # Onglets
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {Palette.ACCENT};
                color: white;
            }}
            QTabBar::tab:!selected {{
                background: {Palette.SCROLLBAR_HANDLE};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: {Palette.SCROLLBAR_HOVER};
                color: white;
            }}
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

        search_btn = self._make_btn("Rechercher", "search", Palette.ACCENT, Palette.ACCENT_HOVER, Palette.ACCENT_PRESSED, w=130)
        search_btn.clicked.connect(self._on_search_barcode)
        scan_row.addWidget(search_btn)

        scan_btn = self._make_btn("Scanner", "scan", Palette.INFO, Palette.INFO_HOVER, Palette.INFO_PRESSED, w=120)
        scan_btn.clicked.connect(lambda: self.scan_barcode_requested.emit())
        scan_row.addWidget(scan_btn)

        scan_v.addLayout(scan_row)

        self.scan_product_status = QLabel("Saisissez un code-barres pour rechercher un produit.")
        self.scan_product_status.setWordWrap(True)
        self.scan_product_status.setStyleSheet(f"""
            font-style: italic; 
            color: {Palette.SCROLLBAR_HANDLE}; 
            padding: 2px 0;
        """)
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

        lbl_s = f"font-size: 13px; color: {Palette.ACCENT};"

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(30)
        grid.setContentsMargins(20, 30, 20, 30)

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

        self.save_product_btn = self._make_btn("Ajouter Produit", "plus-circle", Palette.SUCCESS, Palette.SUCCESS_HOVER, Palette.SUCCESS_PRESSED, w=160)
        self.save_product_btn.clicked.connect(self._on_save_product)
        btn_row.addWidget(self.save_product_btn)

        gen_btn = self._make_btn("Générer Code Interne", "barcode", Palette.PURPLE, Palette.PURPLE_HOVER, Palette.PURPLE_PRESSED, w=180)
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
        self.barcode_preview.setStyleSheet(f"""
            background-color: white;
            border: 1px solid {Palette.BORDER_GRAY};
            border-radius: 6px;
            padding: 8px;
        """)
        preview_v.addWidget(self.barcode_preview)

        self.barcode_value_display = QLabel("<i>Code-barres affiché ici</i>")
        self.barcode_value_display.setAlignment(Qt.AlignCenter)
        self.barcode_value_display.setFont(QFont("Courier New", 12))
        preview_v.addWidget(self.barcode_value_display)

        self.print_internal_btn = self._make_btn("Imprimer l'Étiquette", "printer", Palette.TEAL, Palette.TEAL_HOVER, Palette.TEAL_PRESSED)
        self.print_internal_btn.setEnabled(False)
        self.print_internal_btn.clicked.connect(lambda: self.print_barcode_requested.emit())
        preview_v.addWidget(self.print_internal_btn)

        layout.addWidget(preview_group)
        layout.addStretch()

        return tab

    # ──────────────────────────────────────────────────────────────────
    # ONGLET 2 : AUDIT — même style que les autres vues
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
        self.products_table.setObjectName("barcodeTable")

        self.products_table.setStyleSheet(f"""
            QTableWidget#barcodeTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableWidget#barcodeTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }}
            QTableWidget#barcodeTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#barcodeTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableWidget#barcodeTable::item:hover {{
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

        layout.addWidget(self.products_table, 1)

        # Boutons d'action
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        refresh_btn = self._make_btn("Actualiser", "refresh", Palette.SCROLLBAR_HANDLE, Palette.SCROLLBAR_HOVER, "#7f8c8d", w=130)
        refresh_btn.clicked.connect(lambda: self.refresh_products_requested.emit())
        btn_row.addWidget(refresh_btn)

        edit_btn = self._make_btn("Éditer", "edit", Palette.WARNING, Palette.WARNING_HOVER, Palette.WARNING_PRESSED, w=130)
        edit_btn.clicked.connect(self._on_edit_product)
        btn_row.addWidget(edit_btn)

        delete_btn = self._make_btn("Supprimer", "trash", Palette.DANGER, Palette.DANGER_HOVER, Palette.DANGER_PRESSED, w=130)
        delete_btn.clicked.connect(self._on_delete_product)
        btn_row.addWidget(delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        return tab

    # ──────────────────────────────────────────────────────────────────
    # STYLES PARTAGÉS
    # ──────────────────────────────────────────────────────────────────

    def _groupbox_style(self) -> str:
        return f"""
            QGroupBox {{
                font-size: 13px;
                font-weight: bold;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                margin-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 3px 10px;
                color: {Palette.ACCENT};
                font-weight: bold;
            }}
        """

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                padding: 6px 10px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Palette.ACCENT}; }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                padding: 6px 10px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 6px;
                font-size: 13px;
            }}
            QComboBox:hover {{ border-color: {Palette.ACCENT}; }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
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
            QPushButton:disabled {{ background-color: {Palette.SCROLLBAR_HANDLE}; }}
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
        color = Palette.DANGER if is_error else Palette.SUCCESS
        self.scan_product_status.setText(f"<span style='color:{color};'>{message}</span>")

    def switch_to_audit_tab(self):
        """Bascule vers l'onglet Audit (utile après un ajout réussi)."""
        self.tab_widget.setCurrentIndex(1)