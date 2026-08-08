"""
Widget de tableau réutilisable, thémable (light/dark), avec le style
standard de l'application : header accent, coin forcé, scrollbars stylées,
sélection, hover.

UTILISATION :
=============
from src.ui.widgets.themed_table import ThemedTable

table = ThemedTable(["Nom", "Date", "Taille"], object_name="backupTable")
table.set_column_resize_modes({0: QHeaderView.Stretch, 1: QHeaderView.ResizeToContents})

table.set_rows([
    {"Nom": "backup1.zip", "Date": "2026-08-01", "Taille": "12 KB"},
    {"Nom": "backup2.zip", "Date": "2026-08-02", "Taille": "14 KB"},
])
# ou avec des listes/tuples dans l'ordre des colonnes :
table.set_rows([["backup1.zip", "2026-08-01", "12 KB"]])

table.set_empty_message("Aucune sauvegarde")   # ligne unique fusionnée

# Au changement de thème :
table.apply_theme(is_dark)
"""

"""
Widget de tableau réutilisable, thémable (light/dark).
IMPORTANT : ne jamais définir update(data) — ça écrase QWidget.update().
"""

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QAbstractItemView, QAbstractButton, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from src.ui.views.base.base_view import Palette


class ThemedTable(QTableWidget):
    def __init__(self, headers: list, parent=None, object_name: str = None,
                 row_height: int = 42, corner_width: int = 35):
        super().__init__(parent)
        self._is_dark = False
        self._headers = list(headers)
        self._object_name = object_name or f"themedTable_{id(self)}"
        self.setObjectName(self._object_name)
        self._row_height = row_height
        self._corner_width = corner_width
        self._init_ui()

    def _init_ui(self):
        self.setColumnCount(len(self._headers))
        self.setHorizontalHeaderLabels(self._headers)
        self.setAlternatingRowColors(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)

        header = self.horizontalHeader()
        for col in range(len(self._headers)):
            header.setSectionResizeMode(col, QHeaderView.Interactive)

        v_header = self.verticalHeader()
        v_header.setFixedWidth(self._corner_width)
        v_header.setDefaultSectionSize(self._row_height)

        self._apply_style()
        self._apply_palette()

    def set_column_widths(self, widths: dict):
        for col, w in widths.items():
            self.setColumnWidth(col, w)

    def set_column_resize_modes(self, modes: dict):
        header = self.horizontalHeader()
        for col, mode in modes.items():
            header.setSectionResizeMode(col, mode)

    def _colors(self):
        if self._is_dark:
            return {
                "border": Palette.DARK_BORDER,
                "bg": Palette.DARK_BG,
                "text": Palette.DARK_TEXT,
                "hover": Palette.DARK_ROW_HOVER,
                "selection": Palette.DARK_SELECTION,
                "header": Palette.DARK_HEADER,
                "header_hover": Palette.ACCENT_HOVER,
                "scroll_bg": Palette.DARK_SCROLLBAR_BG,
                "scroll_handle": Palette.DARK_SCROLLBAR_HANDLE,
                "scroll_hover": Palette.DARK_SCROLLBAR_HOVER,
            }
        return {
            "border": Palette.BORDER_GRAY,
            "bg": Palette.LIGHT_BG,
            "text": Palette.LIGHT_TEXT,
            "hover": Palette.ROW_HOVER,
            "selection": Palette.SELECTION,
            "header": Palette.ACCENT,
            "header_hover": Palette.ACCENT_HOVER,
            "scroll_bg": Palette.SCROLLBAR_BG,
            "scroll_handle": Palette.SCROLLBAR_HANDLE,
            "scroll_hover": Palette.SCROLLBAR_HOVER,
        }

    def _apply_style(self):
        c = self._colors()
        obj = self._object_name
        self.setStyleSheet(f"""
            QTableWidget#{obj} {{
                font-size: 13px;
                border: 2px solid {c['border']};
                border-radius: 8px;
                gridline-color: transparent;
                background-color: {c['bg']};
                color: {c['text']};
                outline: none;
            }}
            QTableWidget#{obj} QTableCornerButton::section {{
                background-color: {c['header']};
                border: none;
            }}
            QTableWidget#{obj}::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                background-color: {c['bg']};
                color: {c['text']};
            }}
            QTableWidget#{obj}::item:selected {{
                background-color: {c['selection']};
                color: white;
            }}
            QTableWidget#{obj}::item:hover {{
                background-color: {c['hover']};
            }}
            QTableWidget#{obj} QHeaderView::section {{
                background-color: {c['header']};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {c['header_hover']};
            }}
            QTableWidget#{obj} QHeaderView::section:hover {{
                background-color: {c['header_hover']};
            }}
            QTableWidget#{obj} QHeaderView::section:last {{
                border-right: none;
            }}
            QTableWidget#{obj} QHeaderView::section:vertical {{
                background-color: {c['header']};
                color: white;
                border: none;
                border-bottom: 1px solid {c['header_hover']};
                font-weight: bold;
            }}
            QTableWidget#{obj} QScrollBar:vertical {{
                border: none; background: {c['scroll_bg']};
                width: 12px; border-radius: 6px; margin: 2px;
            }}
            QTableWidget#{obj} QScrollBar::handle:vertical {{
                background: {c['scroll_handle']}; min-height: 20px; border-radius: 6px;
            }}
            QTableWidget#{obj} QScrollBar::handle:vertical:hover {{
                background: {c['scroll_hover']};
            }}
            QTableWidget#{obj} QScrollBar::add-line:vertical,
            QTableWidget#{obj} QScrollBar::sub-line:vertical {{ height: 0px; }}
            QTableWidget#{obj} QScrollBar:horizontal {{
                border: none; background: {c['scroll_bg']};
                height: 12px; border-radius: 6px; margin: 2px;
            }}
            QTableWidget#{obj} QScrollBar::handle:horizontal {{
                background: {c['scroll_handle']}; min-width: 30px; border-radius: 6px;
            }}
            QTableWidget#{obj} QScrollBar::handle:horizontal:hover {{
                background: {c['scroll_hover']};
            }}
            QTableWidget#{obj} QScrollBar::add-line:horizontal,
            QTableWidget#{obj} QScrollBar::sub-line:horizontal {{ width: 0px; }}
        """)
        self._style_corner()

    def _style_corner(self):
        c = self._colors()
        corner = self.findChild(QAbstractButton)
        if corner is not None:
            corner.setStyleSheet(
                f"background-color: {c['header']}; border: none; border-radius: 0px;"
            )

    def _apply_palette(self):
        c = self._colors()
        base = QColor(c["bg"])
        text = QColor(c["text"])
        highlight = QColor(c["selection"])

        palette = self.palette()
        palette.setColor(QPalette.Base, base)
        palette.setColor(QPalette.AlternateBase, base)
        palette.setColor(QPalette.Window, base)
        palette.setColor(QPalette.Text, text)
        palette.setColor(QPalette.Highlight, highlight)
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        self.setPalette(palette)

        self.viewport().setAutoFillBackground(True)
        self.viewport().setPalette(palette)

    def set_rows(self, rows: list):
        self.clearSpans()
        self.setRowCount(len(rows))
        c = self._colors()
        bg, text = QColor(c["bg"]), QColor(c["text"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, header in enumerate(self._headers):
                if isinstance(row_data, dict):
                    value = row_data.get(header, "")
                else:
                    value = row_data[col_idx] if col_idx < len(row_data) else ""
                value = str(value)
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(value)
                item.setBackground(bg)
                item.setForeground(text)
                self.setItem(row_idx, col_idx, item)

        self._apply_palette()

    def set_empty_message(self, message: str):
        """Message centré — fond thémé (plus de bande blanche)."""
        self.clearSpans()
        self.setRowCount(1)
        c = self._colors()
        item = QTableWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        item.setBackground(QColor(c["bg"]))
        item.setForeground(QColor(c["text"]))
        self.setItem(0, 0, item)
        self.setSpan(0, 0, 1, max(self.columnCount(), 1))
        self._apply_palette()
        self._style_corner()

    def clear_table(self):
        self.clearSpans()
        self.setRowCount(0)
        self._apply_palette()

    def apply_theme(self, is_dark: bool):
        self._is_dark = bool(is_dark)
        self._apply_style()
        self._apply_palette()

        c = self._colors()
        bg, text = QColor(c["bg"]), QColor(c["text"])
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item is not None:
                    item.setBackground(bg)
                    item.setForeground(text)

        self._style_corner()
        # ✅ Appel explicite QWidget — ne jamais self.update() si une sous-classe
        # a un update(data) quelque part dans le projet
        self.viewport().update()
        QWidget.update(self)