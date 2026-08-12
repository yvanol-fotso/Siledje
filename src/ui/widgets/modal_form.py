"""
Modal Dialog 100% GÉNÉRIQUE - Réutilisable partout.
✅ CENTRAGE PARFAIT (QTimer)
✅ Scroll automatique
✅ Light/Dark via Palette (même source que BaseView)
✅ AUCUN code métier - juste la structure
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QScrollArea, QFrame, QApplication,
)
from PySide6.QtCore import Qt, Signal, QTimer

try:
    from src.ui.views.base.palette import Palette
except Exception:
    class Palette:
        TEAL = "#1abc9c"
        ACCENT = "#3498db"
        ACCENT_HOVER = "#2980b9"
        TEAL_HOVER = "#16a085"
        SELECTION = "#3498db"
        DARK_SELECTION = "#1abc9c"
        DARK_HEADER = "#1abc9c"

        @staticmethod
        def get_theme_colors(is_dark: bool) -> dict:
            if is_dark:
                return {
                    "bg": "#1e2a38",
                    "text": "#ecf0f1",
                    "border": "#3d4f61",
                    "hover": "rgba(26, 188, 156, 0.15)",
                    "scrollbar_bg": "#1a2430",
                    "scrollbar_handle": "#1abc9c",
                    "scrollbar_hover": "#16a085",
                }
            return {
                "bg": "#ffffff",
                "text": "#2c3e50",
                "border": "#bdc3c7",
                "hover": "rgba(52, 152, 219, 0.12)",
                "scrollbar_bg": "#f0f0f0",
                "scrollbar_handle": "#3498db",
                "scrollbar_hover": "#2980b9",
            }


def _detect_dark(parent) -> bool:
    """Detecte le theme dark via parent / ThemeManager / QApplication."""
    w = parent
    while w is not None:
        if hasattr(w, "_is_dark"):
            return bool(w._is_dark)

        tm = getattr(w, "theme_manager", None)
        if tm is not None:
            try:
                if hasattr(tm, "get_current_theme"):
                    return tm.get_current_theme() == "dark"
                if hasattr(tm, "current_theme"):
                    return tm.current_theme == "dark"
                if hasattr(tm, "_current_theme"):
                    return tm._current_theme == "dark"
            except Exception:
                pass

        try:
            prop = w.property("theme")
            if prop in ("dark", "light"):
                return prop == "dark"
        except Exception:
            pass

        parent_fn = getattr(w, "parent", None)
        w = parent_fn() if callable(parent_fn) else None

    app = QApplication.instance()
    if app is not None:
        css = app.styleSheet() or ""
        if "#1e2a38" in css:
            return True
        if "#f5f5f5" in css:
            return False

    return False


class ModalForm(QDialog):
    """
    Modal Dialog 100% GÉNÉRIQUE.

    Usage:
        modal = ModalForm(title="Mon Titre", parent=self, is_dark=self._is_dark)
        modal.set_content(mon_widget)
        modal.ok_clicked.connect(ma_fonction)
        modal.exec()
    """

    ok_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(
        self,
        title: str = "Dialog",
        parent: QWidget = None,
        width: int = 900,
        height: int = 700,
        show_ok_button: bool = True,
        show_cancel_button: bool = True,
        ok_text: str = "OK",
        cancel_text: str = "Annuler",
        theme_manager=None,
        is_dark: bool = None,
    ):
        super().__init__(parent)

        self.title_text = title
        self.modal_width = width
        self.modal_height = height
        self.show_ok = show_ok_button
        self.show_cancel = show_cancel_button
        self.ok_button_text = ok_text
        self.cancel_button_text = cancel_text
        self.theme_manager = theme_manager or getattr(parent, "theme_manager", None)

        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif self.theme_manager is not None:
            try:
                self._is_dark = self.theme_manager.get_current_theme() == "dark"
            except Exception:
                self._is_dark = _detect_dark(parent)
        else:
            self._is_dark = _detect_dark(parent)

        self.content_widget = None
        self._header = None
        self._footer = None
        self._container = None
        self._title_label = None
        self._ok_btn = None
        self._cancel_btn = None
        self._close_btn = None
        self._separator = None

        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        self.setWindowTitle(self.title_text)
        self.setModal(True)
        self.setMinimumSize(self.modal_width, self.modal_height)
        self.resize(self.modal_width, self.modal_height)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._container = QFrame()
        self._container.setObjectName("modalContainer")

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self._header = self._create_header()
        container_layout.addWidget(self._header)

        self._separator = QFrame()
        self._separator.setObjectName("modalSeparator")
        self._separator.setFrameShape(QFrame.HLine)
        self._separator.setFixedHeight(2)
        container_layout.addWidget(self._separator)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("modalScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.content_container = QWidget()
        self.content_container.setObjectName("modalContent")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(20)
        self.content_container.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_container)
        container_layout.addWidget(self.scroll_area, 1)

        self._footer = self._create_footer()
        container_layout.addWidget(self._footer)

        self._container.setLayout(container_layout)
        main_layout.addWidget(self._container)
        self.setLayout(main_layout)

    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("modalHeader")
        header.setFixedHeight(60)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(25, 0, 25, 0)

        self._title_label = QLabel(self.title_text)
        self._title_label.setObjectName("modalTitle")

        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("modalCloseBtn")
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setFixedSize(35, 35)
        self._close_btn.clicked.connect(self.reject)

        header_layout.addWidget(self._title_label)
        header_layout.addStretch()
        header_layout.addWidget(self._close_btn)
        header.setLayout(header_layout)
        return header

    def _create_footer(self) -> QWidget:
        footer = QWidget()
        footer.setObjectName("modalFooter")
        footer.setFixedHeight(80)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(30, 15, 30, 15)
        footer_layout.setSpacing(15)
        footer_layout.addStretch()

        if self.show_cancel:
            self._cancel_btn = QPushButton(self.cancel_button_text)
            self._cancel_btn.setObjectName("modalCancelBtn")
            self._cancel_btn.setCursor(Qt.PointingHandCursor)
            self._cancel_btn.setMinimumSize(140, 50)
            self._cancel_btn.clicked.connect(self._on_cancel)
            footer_layout.addWidget(self._cancel_btn)

        if self.show_ok:
            self._ok_btn = QPushButton(self.ok_button_text)
            self._ok_btn.setObjectName("modalOkBtn")
            self._ok_btn.setCursor(Qt.PointingHandCursor)
            self._ok_btn.setMinimumSize(140, 50)
            self._ok_btn.clicked.connect(self._on_ok)
            footer_layout.addWidget(self._ok_btn)

        footer.setLayout(footer_layout)
        return footer

    def _apply_theme(self):
        """Meme source de couleurs que BaseView : Palette.get_theme_colors."""
        colors = Palette.get_theme_colors(self._is_dark)
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        accent_hover = (
            getattr(Palette, "TEAL_HOVER", "#16a085")
            if self._is_dark
            else getattr(Palette, "ACCENT_HOVER", "#2980b9")
        )
        selection = (
            getattr(Palette, "DARK_SELECTION", accent)
            if self._is_dark
            else getattr(Palette, "SELECTION", accent)
        )
        footer_bg = "#243447" if self._is_dark else "#ecf0f1"
        cancel_bg = "#3d4f61" if self._is_dark else "#95a5a6"
        cancel_hover = "#4a6178" if self._is_dark else "#7f8c8d"

        self.setProperty("theme", "dark" if self._is_dark else "light")

        self.setStyleSheet(f"""
            QDialog {{
                background: transparent;
            }}
            QFrame#modalContainer {{
                background-color: {colors['bg']};
                border: 3px solid {accent};
                border-radius: 15px;
            }}
            QWidget#modalHeader {{
                background-color: {accent};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QLabel#modalTitle {{
                font-size: 20px;
                font-weight: bold;
                color: white;
                background: transparent;
            }}
            QPushButton#modalCloseBtn {{
                background-color: transparent;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 17px;
            }}
            QPushButton#modalCloseBtn:hover {{
                background-color: #e74c3c;
            }}
            QPushButton#modalCloseBtn:pressed {{
                background-color: #c0392b;
            }}
            QFrame#modalSeparator {{
                background-color: {colors['border']};
                border: none;
                max-height: 2px;
            }}
            QScrollArea#modalScroll {{
                background-color: {colors['bg']};
                border: none;
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
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
                background: none;
            }}
            QWidget#modalContent {{
                background-color: {colors['bg']};
                color: {colors['text']};
            }}
            QWidget#modalContent QLabel {{
                color: {colors['text']};
                background: transparent;
            }}
            QWidget#modalContent QLineEdit {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 28px;
            }}
            QWidget#modalContent QLineEdit:focus {{
                border-color: {accent};
            }}
            QWidget#modalContent QTextEdit,
            QWidget#modalContent QPlainTextEdit {{
                font-size: 14px;
                padding: 8px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QWidget#modalContent QTextEdit:focus,
            QWidget#modalContent QPlainTextEdit:focus {{
                border-color: {accent};
            }}
            QWidget#modalContent QComboBox {{
                padding: 6px 12px;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                font-size: 14px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QWidget#modalContent QComboBox:hover {{
                border-color: {accent};
            }}
            QWidget#modalContent QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QWidget#modalContent QComboBox QAbstractItemView {{
                background: {colors['bg']};
                color: {colors['text']};
                selection-background-color: {selection};
                selection-color: white;
                border: 1px solid {colors['border']};
            }}
            QWidget#modalContent QSpinBox,
            QWidget#modalContent QDoubleSpinBox {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
                min-height: 36px;
            }}
            QWidget#modalContent QSpinBox:focus,
            QWidget#modalContent QDoubleSpinBox:focus {{
                border-color: {accent};
            }}
            QWidget#modalContent QDateEdit {{
                font-size: 14px;
                padding: 6px 8px;
                border: 2px solid {colors['border']};
                border-radius: 6px;
                background: {colors['bg']};
                color: {colors['text']};
            }}
            QWidget#modalContent QDateEdit:hover {{
                border-color: {accent};
            }}
            QWidget#modalContent QCheckBox {{
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
                color: {colors['text']};
                background: transparent;
            }}
            QWidget#modalContent QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background: {colors['bg']};
            }}
            QWidget#modalContent QRadioButton {{
                font-size: 14px;
                spacing: 8px;
                color: {colors['text']};
                background: transparent;
            }}
            QWidget#modalContent QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {colors['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 14px;
                color: {colors['text']};
                background: transparent;
            }}
            QWidget#modalContent QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: {accent};
            }}
            QWidget#modalFooter {{
                background-color: {footer_bg};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
            QPushButton#modalCancelBtn {{
                background-color: {cancel_bg};
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton#modalCancelBtn:hover {{
                background-color: {cancel_hover};
            }}
            QPushButton#modalOkBtn {{
                background-color: {accent};
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton#modalOkBtn:hover {{
                background-color: {accent_hover};
            }}
            QPushButton#modalOkBtn:pressed {{
                background-color: {accent_hover};
            }}
        """)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def apply_theme(self, is_dark: bool = None):
        """API publique pour re-appliquer le theme."""
        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif self.theme_manager is not None:
            try:
                self._is_dark = self.theme_manager.get_current_theme() == "dark"
            except Exception:
                pass
        self._apply_theme()

    def set_content(self, widget: QWidget):
        """Definit le contenu du modal."""
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()

        self.content_widget = widget
        self.content_layout.addWidget(self.content_widget)

    def _on_ok(self):
        self.ok_clicked.emit()

    def _on_cancel(self):
        self.cancel_clicked.emit()
        self.reject()

    def _center_on_parent(self):
        if self.parent() and self.parent().window():
            parent_window = self.parent().window()
            parent_geo = parent_window.frameGeometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.x() + (screen.width() - self.width()) // 2
            y = screen.y() + (screen.height() - self.height()) // 2
            self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._center_on_parent)