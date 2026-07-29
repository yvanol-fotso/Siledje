"""
Vue d'administration - Gestion des utilisateurs.
Herite de BaseView pour une structure coherente.
Support complet mode Dark/Light avec design moderne.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QLineEdit, QLabel, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

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


class AdminView(BaseView):
    """
    Vue de gestion des utilisateurs.
    Herite de BaseView pour une structure coherente.
    """

    search_requested = Signal(str)
    add_user_requested = Signal()
    edit_user_requested = Signal(int)
    delete_user_requested = Signal(int)
    refresh_requested = Signal()
    reset_password_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion des Utilisateurs",
            icon_name="users"
        )

        self.search_input = None
        self.table_view = None
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
        self._init_table()
        self._init_action_buttons()
        
        self._connect_signals()
        self._apply_theme_styles()

    def _init_search_section(self):
        """Section de recherche et ajout."""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un utilisateur...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setObjectName("searchInput")

        search_btn = self._make_btn(
            "Rechercher", "search", Palette.ACCENT, Palette.ACCENT_HOVER,
            Palette.ACCENT_PRESSED, w=140, slot=self._on_search_clicked
        )

        add_btn = self._make_btn(
            "Nouvel Utilisateur", "user-plus", "#2ecc71", "#27ae60",
            "#1e8449", w=180, slot=lambda: self.add_user_requested.emit()
        )

        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn, 1)
        layout.addWidget(add_btn, 1)
        self.content_layout.addLayout(layout)

    def _init_table(self):
        """Tableau des utilisateurs."""
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setMinimumHeight(300)
        self.table_view.setObjectName("adminTable")
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.clicked.connect(self._on_row_clicked)
        
        self.content_layout.addWidget(self.table_view, 1)

    def _init_action_buttons(self):
        """Actions en bas du tableau."""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(self._make_btn(
            "Modifier", "edit", "#f39c12", "#e67e22",
            "#d35400", w=130, slot=self._on_edit_clicked))

        layout.addWidget(self._make_btn(
            "Réinit. mot de passe", "key", "#3498db", "#2980b9",
            "#21618c", w=180, slot=self._on_reset_password_clicked))

        layout.addWidget(self._make_btn(
            "Supprimer", "trash", "#e74c3c", "#c0392b",
            "#a93226", w=130, slot=self._on_delete_clicked))

        layout.addStretch()

        layout.addWidget(self._make_btn(
            "Actualiser", "refresh", "#aab7b8", "#95a5a6",
            "#7f8c8d", w=130, slot=lambda: self.refresh_requested.emit()))

        self.content_layout.addLayout(layout)

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
            QPushButton:disabled {{ background-color: #aab7b8; }}
        """)
        if slot:
            btn.clicked.connect(slot)
        return btn

    def _connect_signals(self):
        self.search_input.returnPressed.connect(self._on_search_clicked)

    def _on_row_clicked(self, index):
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
        else:
            self.show_error("Veuillez sélectionner un utilisateur.", "Sélection requise")

    def _on_delete_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.delete_user_requested.emit(idx.row())
        else:
            self.show_error("Veuillez sélectionner un utilisateur.", "Sélection requise")

    def _on_reset_password_clicked(self):
        idx = self.table_view.currentIndex()
        if idx.isValid():
            self.reset_password_requested.emit(idx.row())
        else:
            self.show_error("Veuillez sélectionner un utilisateur.", "Sélection requise")

    # ========== SUPPORT THEME ==========

    def set_theme(self, is_dark: bool):
        """Applique le theme."""
        super().set_theme(is_dark)
        self._apply_theme_styles()

    def _apply_theme_styles(self):
        """Applique les styles selon le theme."""
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

        table_style = f"""
            QTableView#adminTable {{
                font-size: 13px;
                font-weight: normal;
                border: 2px solid {border};
                border-radius: 8px;
                gridline-color: transparent;
                background: {bg};
                color: {text};
            }}
            QTableView#adminTable::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {text};
            }}
            QTableView#adminTable::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableView#adminTable::item:selected:!active {{
                background-color: {selection};
                color: white;
            }}
            QTableView#adminTable::item:hover {{
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
        self.table_view.setStyleSheet(table_style)

        if self._is_dark:
            self.setStyleSheet(self.styleSheet() + """
                QLineEdit#searchInput {
                    padding: 6px 12px;
                    border: 2px solid #3d3d5c;
                    border-radius: 8px;
                    font-size: 14px;
                    background: #2d2d44;
                    color: #e0e0e0;
                }
                QLineEdit#searchInput:focus {
                    border-color: #567ba1;
                }
            """)
        else:
            self.setStyleSheet(self.styleSheet() + """
                QLineEdit#searchInput {
                    padding: 6px 12px;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    font-size: 14px;
                    background: white;
                    color: #2c3e50;
                }
                QLineEdit#searchInput:focus {
                    border-color: #567ba1;
                }
            """)

    # ========== API PUBLIQUE ==========

    def set_table_model(self, model):
        self.table_view.setModel(model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._last_selected_row = -1
        self._apply_theme_styles()

    def get_selected_row(self) -> int:
        idx = self.table_view.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear_search(self):
        self.search_input.clear()