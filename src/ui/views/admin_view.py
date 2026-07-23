"""
Vue de gestion des utilisateurs - Interface utilisateur responsive.
Style identique aux autres vues : palette unifiée, titre coloré, tableau propre.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QLabel, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
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


class AdminView(QWidget):
    """Vue de gestion des utilisateurs. Style identique aux autres vues."""

    search_requested    = Signal(str)
    add_user_requested  = Signal()
    edit_user_requested = Signal(int)
    delete_user_requested = Signal(int)
    refresh_requested   = Signal()
    reset_password_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.search_input = None
        self.table_view   = None
        self._last_selected_row = -1
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

        # Tableau — prend tout l'espace restant
        self.table_view = self._create_table()
        main_layout.addWidget(self.table_view, 1)

        main_layout.addLayout(self._create_action_buttons())
        self.setLayout(main_layout)
        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    # EN-TÊTE — titre coloré avec la palette unifiée
    # ──────────────────────────────────────────────────────────────────

    def _create_header(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(15)

        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(load_svg_icon("users", size=40))

        title = QLabel("Gestion des Utilisateurs")
        title.setStyleSheet(f"""
            font-size: 28px; 
            font-weight: bold;
            color: {Palette.ACCENT};
        """)

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
        self.search_input.setPlaceholderText("Rechercher un utilisateur...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 6px 12px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border-color: {Palette.ACCENT}; }}
        """)

        search_btn = self._make_btn(
            "Rechercher", "search", Palette.ACCENT, Palette.ACCENT_HOVER, Palette.ACCENT_PRESSED, w=140)
        search_btn.clicked.connect(self._on_search_clicked)

        add_btn = self._make_btn(
            "Nouvel Utilisateur", "user-plus", Palette.SUCCESS, Palette.SUCCESS_HOVER, Palette.SUCCESS_PRESSED, w=180)
        add_btn.clicked.connect(lambda: self.add_user_requested.emit())

        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn, 1)
        layout.addWidget(add_btn, 1)
        return layout

    # ──────────────────────────────────────────────────────────────────
    # TABLEAU — avec palette unifiée
    # ──────────────────────────────────────────────────────────────────

    def _create_table(self) -> QTableView:
        table = QTableView()
        table.setSelectionBehavior(QTableView.SelectRows)
        table.setSelectionMode(QTableView.SingleSelection)
        table.setAlternatingRowColors(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setMinimumHeight(300)
        table.setObjectName("adminTable")
        table.setEditTriggers(QTableView.NoEditTriggers)

        table.setStyleSheet(f"""
            QTableView#adminTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px;
                gridline-color: transparent;
            }}
            QTableView#adminTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
            }}
            QTableView#adminTable::item:selected {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableView#adminTable::item:selected:!active {{
                background-color: {Palette.SELECTION};
                color: white;
            }}
            QTableView#adminTable::item:hover {{
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

    # ──────────────────────────────────────────────────────────────────
    # BOUTONS D'ACTION — avec palette unifiée
    # ──────────────────────────────────────────────────────────────────

    def _create_action_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(self._make_btn(
            "Modifier", "edit", Palette.WARNING, Palette.WARNING_HOVER, 
            Palette.WARNING_PRESSED, w=130, slot=self._on_edit_clicked))
        
        layout.addWidget(self._make_btn(
            "Réinit. mot de passe", "key", Palette.INFO, Palette.INFO_HOVER, 
            Palette.INFO_PRESSED, w=180, slot=self._on_reset_password_clicked))
        
        layout.addWidget(self._make_btn(
            "Supprimer", "trash", Palette.DANGER, Palette.DANGER_HOVER, 
            Palette.DANGER_PRESSED, w=130, slot=self._on_delete_clicked))
        
        layout.addStretch()
        
        layout.addWidget(self._make_btn(
            "Actualiser", "refresh", Palette.SCROLLBAR_HANDLE, Palette.SCROLLBAR_HOVER, 
            "#7f8c8d", w=130, slot=lambda: self.refresh_requested.emit()))
        
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
            QPushButton:disabled {{ background-color: {Palette.SCROLLBAR_HANDLE}; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    # ──────────────────────────────────────────────────────────────────
    # SIGNAUX INTERNES
    # ──────────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.search_input.returnPressed.connect(self._on_search_clicked)
        # Sélection/désélection du tableau
        self.table_view.clicked.connect(self._on_row_clicked)

    def _on_row_clicked(self, index):
        """
        Gère le toggle sélection/désélection :
        - Si la ligne est déjà sélectionnée -> on la désélectionne
        - Si la ligne n'est pas sélectionnée -> on la sélectionne
        """
        row = index.row()
        selection_model = self.table_view.selectionModel()
        
        if selection_model.isRowSelected(row, index.parent()):
            selection_model.clearSelection()
            selection_model.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            selection_model.clearSelection()
            selection_model.select(index, selection_model.Select)
            self._last_selected_row = row

    def _on_search_clicked(self):
        self.search_requested.emit(self.search_input.text())

    def _on_edit_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.edit_user_requested.emit(idx.row())

    def _on_delete_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.delete_user_requested.emit(idx.row())

    def _on_reset_password_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.reset_password_requested.emit(idx.row())

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES POUR LE MANAGER
    # ──────────────────────────────────────────────────────────────────

    def set_table_model(self, model):
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._last_selected_row = -1

    def get_selected_row(self) -> int:
        idx = self.table_view.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear_search(self):
        self.search_input.clear()