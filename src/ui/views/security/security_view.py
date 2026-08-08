"""
Vue roles / permissions — CustomButton + ThemedTable + Palette.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy,
)
from PySide6.QtCore import Signal

from src.ui.views.base.base_view import BaseView
from src.ui.views.base.palette import Palette
from src.ui.widgets.custom_button import (
    primary_btn, success_btn, warning_btn, danger_btn,
    outline_btn, CustomButton,
)
from src.ui.views.security.security_table import SecurityRolesTable


class SecurityView(BaseView):
    search_requested = Signal(str)
    add_role_requested = Signal()
    edit_role_requested = Signal(int)
    delete_role_requested = Signal(int)
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(
            parent=parent,
            title="Gestion des Roles et Permissions",
            icon_name="shield",
        )

        self.search_input = None
        self.table = None
        self._last_selected_row = -1

        self.main_layout.removeWidget(self.content_area)
        self.content_area.deleteLater()
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

        self._init_search()
        self._init_table()
        self._init_actions()
        self._connect_signals()
        self._restyle_all_buttons()
        self._apply_theme_styles()

    def _init_search(self):
        layout = QHBoxLayout()
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher un role...")
        self.search_input.setMinimumHeight(42)
        self.search_input.setObjectName("searchInput")

        search_btn = primary_btn("Rechercher", "search", self._on_search)
        search_btn.setMinimumWidth(140)
        search_btn.setMinimumHeight(42)

        add_btn = success_btn(
            "Nouveau Role", "shield",
            lambda: self.add_role_requested.emit(),
        )
        add_btn.setMinimumWidth(160)
        add_btn.setMinimumHeight(42)

        layout.addWidget(self.search_input, 3)
        layout.addWidget(search_btn)
        layout.addWidget(add_btn)
        self.content_layout.addLayout(layout)

    def _init_table(self):
        self.table = SecurityRolesTable()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumHeight(300)
        self.table.clicked.connect(self._on_row_clicked)
        self.content_layout.addWidget(self.table, 1)

    def _init_actions(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)

        edit_btn = warning_btn("Modifier", "edit", self._on_edit)
        edit_btn.setMinimumWidth(130)
        edit_btn.setMinimumHeight(42)

        delete_btn = danger_btn("Supprimer", "trash", self._on_delete)
        delete_btn.setMinimumWidth(130)
        delete_btn.setMinimumHeight(42)

        refresh_btn = outline_btn(
            "Actualiser", "refresh",
            lambda: self.refresh_requested.emit(),
        )
        refresh_btn.setMinimumWidth(130)
        refresh_btn.setMinimumHeight(42)

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()
        layout.addWidget(refresh_btn)
        self.content_layout.addLayout(layout)

    def _connect_signals(self):
        self.search_input.returnPressed.connect(self._on_search)

    def _on_row_clicked(self, index):
        row = index.row()
        sm = self.table.selectionModel()
        if sm.isRowSelected(row, index.parent()):
            sm.clearSelection()
            sm.clearCurrentIndex()
            self._last_selected_row = -1
        else:
            sm.clearSelection()
            self.table.selectRow(row)
            self._last_selected_row = row

    def _on_search(self):
        self.search_requested.emit(self.search_input.text())

    def _on_edit(self):
        row = self.table.currentRow()
        if row >= 0:
            self.edit_role_requested.emit(row)
        else:
            self.show_error("Veuillez selectionner un role.", "Selection requise")

    def _on_delete(self):
        row = self.table.currentRow()
        if row >= 0:
            self.delete_role_requested.emit(row)
        else:
            self.show_error("Veuillez selectionner un role.", "Selection requise")

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        try:
            self.table.apply_theme(is_dark)
        except Exception as e:
            print(f"[SecurityView] theme table: {e}")
        self._restyle_all_buttons()
        self._apply_theme_styles()

    def _restyle_all_buttons(self):
        is_dark = getattr(self, "_is_dark", False)
        for btn in self.findChildren(CustomButton):
            btn.apply_theme(is_dark)
            btn.setMinimumHeight(42)

    def _apply_theme_styles(self):
        super()._apply_theme_styles()
        colors = Palette.get_theme_colors(getattr(self, "_is_dark", False))
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        self.setStyleSheet(self.styleSheet() + f"""
            QLineEdit#searchInput {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 40px;
            }}
            QLineEdit#searchInput:focus {{
                border-color: {accent};
            }}
        """)

    def update_roles(self, roles: list):
        self.table.set_roles(roles)
        self._last_selected_row = -1

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def clear_search(self):
        self.search_input.clear()