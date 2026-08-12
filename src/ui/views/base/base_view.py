"""
Vue de base — structure commune à toutes les vues.
Light / Dark, InfoDialog, CustomButton, titres GroupBox teal en dark.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QColor

from src.ui.views.base.palette import Palette
from src.ui.widgets.modal_form import ModalForm
from src.ui.widgets.custom_button import outline_btn, CustomButton
from src.ui.widgets.InfoDialog import InfoDialog


class BaseView(QWidget):
    refresh_requested = Signal()
    error_occurred = Signal(str)
    success_occurred = Signal(str)

    def __init__(self, parent=None, title: str = "", icon_name: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.icon_name = icon_name
        self._is_dark = False
        self._title_label = None
        self._refresh_btn = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self._create_header()
        self._create_toolbar()
        self._create_content_area()

        self.setLayout(self.main_layout)
        self._apply_styles()

    # ──────────────────────────────────────────────
    # Structure
    # ──────────────────────────────────────────────

    def _create_header(self):
        header = QHBoxLayout()
        header.setSpacing(15)

        if self.icon_name:
            icon_label = QLabel()
            icon_label.setFixedSize(40, 40)
            icon_label.setPixmap(self._load_icon(self.icon_name, size=40))
            header.addWidget(icon_label)

        self._title_label = QLabel(self.title)
        self._title_label.setObjectName("viewTitle")
        self._title_label.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {Palette.ACCENT};"
        )
        header.addWidget(self._title_label)
        header.addStretch()
        self.main_layout.addLayout(header)

    def _create_toolbar(self):
        self.toolbar = QHBoxLayout()
        self.toolbar.setSpacing(10)

        self._refresh_btn = outline_btn(
            "Actualiser", "refresh",
            lambda: self.refresh_requested.emit(),
        )
        self._refresh_btn.setMinimumHeight(36)
        self._refresh_btn.setMinimumWidth(120)
        self.toolbar.addWidget(self._refresh_btn)
        self.toolbar.addStretch()
        self.main_layout.addLayout(self.toolbar)

    def _create_content_area(self):
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area, 1)

    # ──────────────────────────────────────────────
    # Icônes
    # ──────────────────────────────────────────────

    def _load_icon(self, icon_name: str, size: int = 24) -> QPixmap:
        try:
            from src.utils.helpers import get_asset_path
            icon_path = get_asset_path("icons", f"{icon_name}.svg")
            if not icon_path.exists():
                return self._make_placeholder(size, icon_name[0].upper())
            icon = QIcon(str(icon_path))
            return (
                icon.pixmap(size, size)
                if not icon.isNull()
                else self._make_placeholder(size, icon_name[0].upper())
            )
        except Exception:
            return self._make_placeholder(size, icon_name[0].upper())

    def _make_placeholder(self, size: int, letter: str) -> QPixmap:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        color = Palette.TEAL if self._is_dark else Palette.ACCENT
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(0, 0, size, size, 4, 4)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", int(size * 0.5), QFont.Bold))
        painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
        painter.end()
        return pixmap

    # ──────────────────────────────────────────────
    # Styles de base
    # ──────────────────────────────────────────────

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                font-family: "Segoe UI", sans-serif;
            }
        """)

    def set_theme(self, is_dark: bool):
        self._is_dark = is_dark
        self._apply_theme_styles()
        # Bouton Actualiser (CustomButton)
        if self._refresh_btn is not None:
            self._refresh_btn.apply_theme(is_dark)
        # Titre
        if self._title_label is not None:
            accent = Palette.TEAL if is_dark else Palette.ACCENT
            self._title_label.setStyleSheet(
                f"font-size: 28px; font-weight: bold; color: {accent};"
            )

    def _apply_theme_styles(self):
        colors = Palette.get_theme_colors(self._is_dark)
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        selection = Palette.DARK_SELECTION if self._is_dark else Palette.SELECTION
        header_bg = Palette.DARK_HEADER if self._is_dark else Palette.ACCENT
        check_icon = "check_green" if self._is_dark else "check_blue"

        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                font-family: "Segoe UI", sans-serif;
                color: {colors['text']};
            }}
            QLineEdit {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QLineEdit:focus {{
                border-color: {accent};
            }}
            QComboBox {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QComboBox:hover {{
                border-color: {accent};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {selection};
                selection-color: white;
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                color: {colors['text']};
                background: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}
            QTableView {{
                font-size: 13px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                gridline-color: transparent;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QTableView::item {{
                padding: 6px 8px;
                border-bottom: 1px solid rgba(150, 150, 150, 0.18);
                color: {colors['text']};
            }}
            QTableView::item:selected {{
                background-color: {selection};
                color: white;
            }}
            QTableView::item:hover {{
                background-color: {colors['hover']};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                border: none;
                border-right: 1px solid {Palette.ACCENT_HOVER};
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {colors['scrollbar_bg']};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['scrollbar_handle']};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {colors['scrollbar_bg']};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {colors['scrollbar_handle']};
                min-width: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {colors['scrollbar_hover']};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QCheckBox {{
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
                color: {colors['text']};
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background: {colors['bg']};
            }}
            QDateEdit {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QDateEdit:hover {{
                border-color: {accent};
            }}
            QSpinBox, QDoubleSpinBox {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {accent};
            }}
            QTextEdit {{
                font-size: 14px;
                padding: 8px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QTextEdit:focus {{
                border-color: {accent};
            }}
        """)

    # ──────────────────────────────────────────────
    # Messages (InfoDialog uniquement)
    # ──────────────────────────────────────────────

    def show_error(self, message: str, title: str = "Erreur"):
        InfoDialog.warning(self, title, message)
        self.error_occurred.emit(message)

    def show_success(self, message: str, title: str = "Succes"):
        InfoDialog.success(self, title, message)
        self.success_occurred.emit(message)

    def show_info(self, message: str, title: str = "Information"):
        InfoDialog.info(self, title, message)

    def show_confirm(
        self,
        message: str,
        title: str = "Confirmation",
        ok_text: str = "Yes",
        cancel_text: str = "No",
    ) -> bool:
        return InfoDialog.question(
            self, title, message, ok_text=ok_text, cancel_text=cancel_text
        )

    def show_modal(
        self,
        title: str,
        content: QWidget,
        ok_text: str = "OK",
        cancel_text: str = "Annuler",
        width: int = 600,
        height: int = 400,
    ) -> ModalForm:
        modal = ModalForm(
            title=title,
            parent=self,
            width=width,
            height=height,
            ok_text=ok_text,
            cancel_text=cancel_text,
            is_dark=self._is_dark,
        )
        modal.set_content(content)
        return modal