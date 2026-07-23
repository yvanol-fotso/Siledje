"""
Vue de la gestion du stock - Interface utilisateur ultra-responsive.
Séparation complète de la logique métier.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QComboBox, QLabel,
    QDateEdit, QRadioButton, QButtonGroup, QGroupBox,
    QGridLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return _make_placeholder(size, icon_name[0].upper())
        icon = QIcon(str(icon_path))
        if icon.isNull():
            return _make_placeholder(size, icon_name[0].upper())
        pixmap = icon.pixmap(size, size)
        if pixmap.isNull():
            return _make_placeholder(size, icon_name[0].upper())
        return pixmap
    except Exception as e:
        print(f"Erreur icône {icon_name}: {e}")
        return _make_placeholder(size, icon_name[0].upper())


def _make_placeholder(size: int, letter: str) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#3498db")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class StockView(QWidget):
    """Vue de gestion du stock. S'adapte automatiquement aux modes Dark/Light."""

    search_requested         = Signal(str)
    category_filter_changed  = Signal(str)
    supplier_filter_changed  = Signal(str)
    packaging_filter_changed = Signal(str)
    class_filter_changed     = Signal(str)
    date_range_changed       = Signal(QDate, QDate)
    add_product_requested    = Signal()
    edit_product_requested   = Signal(int)
    delete_product_requested = Signal(int)
    refresh_requested        = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.search_input          = None
        self.category_filter_combo = None
        self.supplier_filter_combo = None
        self.packaging_group       = None
        self.class_filter_combo    = None
        self.start_date_edit       = None
        self.end_date_edit         = None
        self.table_view            = None
        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_search_section())
        main_layout.addWidget(self._create_filters_section())

        self.table_view = self._create_table()
        main_layout.addWidget(self.table_view, 1)

        main_layout.addLayout(self._create_action_buttons())
        self.setLayout(main_layout)
        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("package", size=40))

        title = QLabel("Gestion du Stock")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addStretch()
        return layout

    # ──────────────────────────────────────────────────────────────────
    # RECHERCHE + BOUTON AJOUTER
    # ──────────────────────────────────────────────────────────────────

    def _create_search_section(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un produit...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)

        search_btn = QPushButton("Rechercher")
        search_btn.setMinimumHeight(42)
        search_btn.setMinimumWidth(140)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setIcon(QIcon(load_svg_icon("search", size=16)))
        search_btn.setIconSize(QSize(16, 16))
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover   { background-color: #2980b9; }
            QPushButton:pressed { background-color: #21618c; }
        """)
        search_btn.clicked.connect(self._on_search_clicked)

        add_btn = QPushButton("Ajouter Produit")
        add_btn.setMinimumHeight(42)
        add_btn.setMinimumWidth(160)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setIcon(QIcon(load_svg_icon("plus-circle", size=16)))
        add_btn.setIconSize(QSize(16, 16))
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover   { background-color: #27ae60; }
            QPushButton:pressed { background-color: #1e8449; }
        """)
        add_btn.clicked.connect(lambda: self.add_product_requested.emit())

        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn, 1)
        layout.addWidget(add_btn, 1)
        return layout

    # ──────────────────────────────────────────────────────────────────
    # FILTRES
    # ──────────────────────────────────────────────────────────────────

    def _create_filters_section(self) -> QGroupBox:
        group = QGroupBox("Filtres de Recherche")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 18px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
            }
        """)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(16, 16, 16, 16)

        lbl_style = "font-size: 14px; font-weight: normal;"

        combo_style = """
            QComboBox {
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QComboBox:hover   { border-color: #3498db; }
            QComboBox::drop-down { border: none; padding-right: 8px; }
        """

        lbl_cat = QLabel("Catégorie:")
        lbl_cat.setStyleSheet(lbl_style)
        grid.addWidget(lbl_cat, 0, 0)

        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItem("Toutes")
        self.category_filter_combo.setMinimumHeight(36)
        self.category_filter_combo.setStyleSheet(combo_style)
        grid.addWidget(self.category_filter_combo, 0, 1)

        lbl_sup = QLabel("Fournisseur:")
        lbl_sup.setStyleSheet(lbl_style)
        grid.addWidget(lbl_sup, 0, 2)

        self.supplier_filter_combo = QComboBox()
        self.supplier_filter_combo.addItem("Tous")
        self.supplier_filter_combo.setMinimumHeight(36)
        self.supplier_filter_combo.setStyleSheet(combo_style)
        grid.addWidget(self.supplier_filter_combo, 0, 3)

        lbl_pack = QLabel("Type d'emballage:")
        lbl_pack.setStyleSheet(lbl_style)
        grid.addWidget(lbl_pack, 1, 0)

        pack_layout = QHBoxLayout()
        pack_layout.setSpacing(20)
        self.packaging_group = QButtonGroup(self)

        radio_style = """
            QRadioButton {
                font-size: 13px;
                font-weight: normal;
                spacing: 5px;
            }
        """
        for option in ["Tous", "Carton", "Unité", "Pièce", "Lot", "Autre"]:
            rb = QRadioButton(option)
            rb.setStyleSheet(radio_style)
            pack_layout.addWidget(rb)
            self.packaging_group.addButton(rb)
            if option == "Tous":
                rb.setChecked(True)

        pack_layout.addStretch()
        grid.addLayout(pack_layout, 1, 1, 1, 3)

        lbl_cls = QLabel("Classe:")
        lbl_cls.setStyleSheet(lbl_style)
        grid.addWidget(lbl_cls, 2, 0)

        self.class_filter_combo = QComboBox()
        self.class_filter_combo.addItem("Toutes")
        self.class_filter_combo.setMinimumHeight(36)
        self.class_filter_combo.setStyleSheet(combo_style)
        grid.addWidget(self.class_filter_combo, 2, 1)

        lbl_date = QLabel("Période:")
        lbl_date.setStyleSheet(lbl_style)
        grid.addWidget(lbl_date, 2, 2)

        date_style = """
            QDateEdit {
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
            }
            QDateEdit:hover { border-color: #3498db; }
        """

        dates_layout = QHBoxLayout()
        dates_layout.setSpacing(8)

        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.start_date_edit.setDate(QDate(2024, 1, 1))
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setMinimumHeight(36)
        self.start_date_edit.setStyleSheet(date_style)

        arrow = QLabel("à")
        arrow.setStyleSheet("font-size: 14px; padding: 0 4px;")

        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setMinimumHeight(36)
        self.end_date_edit.setStyleSheet(date_style)

        dates_layout.addWidget(self.start_date_edit)
        dates_layout.addWidget(arrow)
        dates_layout.addWidget(self.end_date_edit)
        grid.addLayout(dates_layout, 2, 3)

        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(3, 2)

        group.setLayout(grid)
        return group

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU
    # ──────────────────────────────────────────────────────────────────

    def _create_table(self) -> QTableView:
        table = QTableView()
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setMinimumHeight(300)
        table.setObjectName("stockTable")

        table.setStyleSheet("""
            QTableView#stockTable {
                font-size: 13px;
                font-weight: normal;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableView#stockTable::item {
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }
            QTableView#stockTable::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableView#stockTable::item:hover {
                background-color: rgba(52, 152, 219, 0.10);
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid #2980b9;
            }
            QHeaderView::section:last { border-right: none; }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #27ae60;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover { background: #2ecc71; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal {
                border: none;
                background: rgba(150, 150, 150, 0.15);
                height: 10px;
                border-radius: 5px;
                margin-bottom: 2px;
            }
            QScrollBar::handle:horizontal {
                background: #27ae60;
                min-width: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover { background: #2ecc71; }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal { width: 0px; }
        """)
        table.setContentsMargins(0, 0, 0, 12)

        return table

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION
    # ──────────────────────────────────────────────────────────────────

    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        def _btn(label, icon_name, bg, hover, pressed, slot):
            b = QPushButton(label)
            b.setMinimumHeight(42)
            b.setMinimumWidth(130)
            b.setCursor(Qt.PointingHandCursor)
            b.setIcon(QIcon(load_svg_icon(icon_name, size=16)))
            b.setIconSize(QSize(16, 16))
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: white;
                    padding: 6px 14px;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover   {{ background-color: {hover};   }}
                QPushButton:pressed {{ background-color: {pressed}; }}
            """)
            b.clicked.connect(slot)
            return b

        layout.addWidget(_btn("Modifier",   "edit",    "#f39c12","#e67e22","#d35400", self._on_edit_clicked))
        layout.addWidget(_btn("Supprimer",  "trash",   "#e74c3c","#c0392b","#a93226", self._on_delete_clicked))
        layout.addStretch()
        layout.addWidget(_btn("Actualiser","refresh",  "#95a5a6","#7f8c8d","#707b7c", lambda: self.refresh_requested.emit()))
        return layout

    # ──────────────────────────────────────────────────────────────────
    # SIGNAUX INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.search_input.returnPressed.connect(self._on_search_clicked)
        self.category_filter_combo.currentTextChanged.connect(
            lambda t: self.category_filter_changed.emit(t))
        self.supplier_filter_combo.currentTextChanged.connect(
            lambda t: self.supplier_filter_changed.emit(t))
        self.packaging_group.buttonClicked.connect(
            lambda btn: self.packaging_filter_changed.emit(btn.text()))
        self.class_filter_combo.currentTextChanged.connect(
            lambda t: self.class_filter_changed.emit(t))
        self.start_date_edit.dateChanged.connect(self._on_date_changed)
        self.end_date_edit.dateChanged.connect(self._on_date_changed)

    def _on_search_clicked(self):
        self.search_requested.emit(self.search_input.text())

    def _on_edit_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.edit_product_requested.emit(idx.row())

    def _on_delete_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.delete_product_requested.emit(idx.row())

    def _on_date_changed(self):
        self.date_range_changed.emit(
            self.start_date_edit.date(),
            self.end_date_edit.date()
        )

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def set_table_model(self, model):
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()

    def update_categories(self, categories: list):
        current = self.category_filter_combo.currentText()
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem("Toutes")
        self.category_filter_combo.addItems(categories)
        idx = self.category_filter_combo.findText(current)
        if idx >= 0:
            self.category_filter_combo.setCurrentIndex(idx)

    def update_suppliers(self, suppliers: list):
        current = self.supplier_filter_combo.currentText()
        self.supplier_filter_combo.clear()
        self.supplier_filter_combo.addItem("Tous")
        self.supplier_filter_combo.addItems(suppliers)
        idx = self.supplier_filter_combo.findText(current)
        if idx >= 0:
            self.supplier_filter_combo.setCurrentIndex(idx)

    def update_classes(self, classes: list):
        current = self.class_filter_combo.currentText()
        self.class_filter_combo.clear()
        self.class_filter_combo.addItem("Toutes")
        self.class_filter_combo.addItems(classes)
        idx = self.class_filter_combo.findText(current)
        if idx >= 0:
            self.class_filter_combo.setCurrentIndex(idx)

    def get_selected_row(self) -> int:
        idx = self.table_view.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear_search(self):
        self.search_input.clear()