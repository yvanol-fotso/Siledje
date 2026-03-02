"""
Vue de gestion des fournisseurs - Interface utilisateur responsive.
Style identique à stock_view. Utilise ModalView générique.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QLabel, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
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
    painter.setBrush(QBrush(QColor("#16a085")))
    painter.setPen(QPen(Qt.NoPen))
    painter.drawRoundedRect(0, 0, size, size, 4, 4)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
    painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
    painter.end()
    return pixmap


class SupplierView(QWidget):
    """Vue de gestion des fournisseurs. Style identique à stock_view."""

    search_requested      = Signal(str)
    add_supplier_requested    = Signal()
    edit_supplier_requested   = Signal(int)
    delete_supplier_requested = Signal(int)
    refresh_requested     = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.search_input = None
        self.table_view   = None
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
        icon_label.setPixmap(load_svg_icon("truck", size=40))

        title = QLabel("Configuration des Fournisseurs")
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
        self.search_input.setPlaceholderText("Rechercher un fournisseur...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #16a085; }
        """)

        search_btn = self._make_btn(
            "Rechercher", "search", "#16a085", "#1abc9c", "#0e8070", w=140)
        search_btn.clicked.connect(self._on_search_clicked)

        add_btn = self._make_btn(
            "Nouveau Fournisseur", "plus-circle", "#2ecc71", "#27ae60", "#1e8449", w=190)
        add_btn.clicked.connect(lambda: self.add_supplier_requested.emit())

        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn, 1)
        layout.addWidget(add_btn, 1)
        return layout

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU — copie exacte du style stock_view
    # ──────────────────────────────────────────────────────────────────

    def _create_table(self) -> QTableView:
        table = QTableView()
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setMinimumHeight(300)
        table.setObjectName("supplierTable")

        table.setStyleSheet("""
            QTableView#supplierTable {
                font-size: 13px;
                font-weight: normal;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                gridline-color: transparent;
            }
            QTableView#supplierTable::item {
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }
            QTableView#supplierTable::item:selected {
                background-color: #16a085;
                color: white;
            }
            QTableView#supplierTable::item:hover {
                background-color: rgba(22, 160, 133, 0.10);
            }
            QHeaderView::section {
                background-color: #16a085;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid #0e8070;
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
        return table

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION
    # ──────────────────────────────────────────────────────────────────

    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(self._make_btn(
            "Modifier",   "edit",    "#f39c12", "#e67e22", "#d35400", w=130,
            slot=self._on_edit_clicked))
        layout.addWidget(self._make_btn(
            "Supprimer",  "trash",   "#e74c3c", "#c0392b", "#a93226", w=130,
            slot=self._on_delete_clicked))
        layout.addStretch()
        layout.addWidget(self._make_btn(
            "Actualiser", "refresh", "#95a5a6", "#7f8c8d", "#707b7c", w=130,
            slot=lambda: self.refresh_requested.emit()))
        return layout

    # ──────────────────────────────────────────────────────────────────
    # HELPER BOUTON
    # ──────────────────────────────────────────────────────────────────

    def _make_btn(self, label, icon_name, bg, hover, pressed, w=None, slot=None) -> QPushButton:
        btn = QPushButton(label)
        btn.setMinimumHeight(42)
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
                padding: 6px 14px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover   {{ background-color: {hover};   }}
            QPushButton:pressed {{ background-color: {pressed}; }}
            QPushButton:disabled {{ background-color: #95a5a6; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    # ──────────────────────────────────────────────────────────────────
    # SIGNAUX INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.search_input.returnPressed.connect(self._on_search_clicked)

    def _on_search_clicked(self):
        self.search_requested.emit(self.search_input.text())

    def _on_edit_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.edit_supplier_requested.emit(idx.row())

    def _on_delete_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.delete_supplier_requested.emit(idx.row())

    # ──────────────────────────────────────────────────────────────────
    # METHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def set_table_model(self, model):
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def get_selected_row(self) -> int:
        idx = self.table_view.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear_search(self):
        self.search_input.clear()