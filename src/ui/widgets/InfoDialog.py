"""
InfoDialog — alertes / infos / confirmations thémées.
Même source de couleurs que BaseView / ModalForm : Palette.
Usage:
    InfoDialog.info(parent, "Titre", "Message")
    InfoDialog.warning(parent, "Titre", "Message")
    InfoDialog.error(parent, "Titre", "Message")
    InfoDialog.success(parent, "Titre", "Message")
    ok = InfoDialog.question(parent, "Confirmation", "Voulez-vous continuer ?")
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
        DANGER = "#e74c3c"
        WARNING = "#e67e22"
        SUCCESS = "#2ecc71"
        INFO = "#3498db"
        TEAL_HOVER = "#16a085"
        ACCENT_HOVER = "#2980b9"

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


class DialogType:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    QUESTION = "question"


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


class InfoDialog(QDialog):
    ok_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(
        self,
        parent=None,
        title: str = "Information",
        message: str = "",
        dialog_type: str = DialogType.INFO,
        width: int = 480,
        height: int = 260,
        show_cancel: bool = False,
        ok_text: str = "OK",
        cancel_text: str = "Annuler",
        content_widget: QWidget = None,
        is_dark: bool = None,
    ):
        super().__init__(parent)
        self._title = title
        self._message = message
        self._type = dialog_type
        self._width = width
        self._height = height
        self._show_cancel = show_cancel
        self._ok_text = ok_text
        self._cancel_text = cancel_text
        self._custom = content_widget
        self._is_dark = _detect_dark(parent) if is_dark is None else bool(is_dark)
        self._theme = self._resolve_theme(dialog_type)
        self._build()

    def _resolve_theme(self, dialog_type: str) -> dict:
        colors = Palette.get_theme_colors(self._is_dark)

        accent_map = {
            DialogType.INFO: getattr(Palette, "INFO", "#3498db"),
            DialogType.WARNING: getattr(Palette, "WARNING", "#e67e22"),
            DialogType.ERROR: getattr(Palette, "DANGER", "#e74c3c"),
            DialogType.SUCCESS: getattr(Palette, "SUCCESS", "#2ecc71"),
            DialogType.QUESTION: Palette.TEAL if self._is_dark else Palette.ACCENT,
        }
        accent = accent_map.get(dialog_type, Palette.ACCENT)

        hover_map = {
            DialogType.INFO: getattr(Palette, "ACCENT_HOVER", "#2980b9"),
            DialogType.WARNING: "#d35400",
            DialogType.ERROR: "#c0392b",
            DialogType.SUCCESS: "#27ae60",
            DialogType.QUESTION: (
                getattr(Palette, "TEAL_HOVER", "#16a085")
                if self._is_dark
                else getattr(Palette, "ACCENT_HOVER", "#2980b9")
            ),
        }
        hover = hover_map.get(dialog_type, "#2980b9")

        footer_bg = "#243447" if self._is_dark else "#ecf0f1"

        return {
            "header_bg": accent,
            "header_hover": hover,
            "border": accent,
            "btn_ok_bg": accent,
            "btn_ok_hover": hover,
            "body_bg": colors["bg"],
            "footer_bg": footer_bg,
            "text": colors["text"],
            "frame_bg": colors["bg"],
            "scrollbar_bg": colors.get("scrollbar_bg", "transparent"),
            "scrollbar_handle": colors.get("scrollbar_handle", "#7f8c8d"),
            "scrollbar_hover": colors.get("scrollbar_hover", "#95a5a6"),
        }

    def _build(self):
        self.setWindowTitle(self._title)
        self.setModal(True)
        self.setMinimumSize(self._width, self._height)
        self.resize(self._width, self._height)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setProperty("theme", "dark" if self._is_dark else "light")

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("infoFrame")
        frame.setStyleSheet(f"""
            QFrame#infoFrame {{
                background-color: {self._theme['frame_bg']};
                border: 2px solid {self._theme['border']};
                border-radius: 14px;
            }}
        """)

        inner = QVBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        inner.addWidget(self._make_header())
        inner.addWidget(self._make_body(), 1)
        inner.addWidget(self._make_footer())
        frame.setLayout(inner)
        root.addWidget(frame)
        self.setLayout(root)

    def _make_header(self) -> QWidget:
        hdr = QWidget()
        hdr.setObjectName("infoHeader")
        hdr.setFixedHeight(52)
        hdr.setStyleSheet(f"""
            QWidget#infoHeader {{
                background-color: {self._theme['header_bg']};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)
        lay = QHBoxLayout()
        lay.setContentsMargins(20, 0, 12, 0)

        lbl = QLabel(self._title)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background: transparent;")

        close = QPushButton("✕")
        close.setFixedSize(32, 32)
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.25);
            }
        """)
        close.clicked.connect(self.reject)

        lay.addWidget(lbl)
        lay.addStretch()
        lay.addWidget(close)
        hdr.setLayout(lay)
        return hdr

    def _make_body(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {self._theme['body_bg']};
                border: none;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self._theme['scrollbar_bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {self._theme['scrollbar_handle']};
                border-radius: 5px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self._theme['scrollbar_hover']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        wrapper = QWidget()
        wrapper.setStyleSheet(f"background: {self._theme['body_bg']};")
        lay = QVBoxLayout()
        lay.setContentsMargins(24, 20, 24, 16)
        lay.setSpacing(12)

        if self._message:
            msg = QLabel(self._message)
            msg.setWordWrap(True)
            msg.setStyleSheet(
                f"font-size: 14px; color: {self._theme['text']}; "
                f"line-height: 1.5; background: transparent;"
            )
            msg.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            lay.addWidget(msg)

        if self._custom:
            lay.addWidget(self._custom)

        lay.addStretch()
        wrapper.setLayout(lay)
        scroll.setWidget(wrapper)
        return scroll

    def _make_footer(self) -> QWidget:
        ftr = QWidget()
        ftr.setFixedHeight(70)
        ftr.setObjectName("infoFooter")
        ftr.setStyleSheet(f"""
            QWidget#infoFooter {{
                background: {self._theme['footer_bg']};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)
        lay = QHBoxLayout()
        lay.setContentsMargins(20, 10, 20, 10)
        lay.setSpacing(10)
        lay.addStretch()

        cancel_bg = "#3d4f61" if self._is_dark else "#95a5a6"
        cancel_hover = "#4a6178" if self._is_dark else "#7f8c8d"

        if self._show_cancel:
            btn_c = QPushButton(self._cancel_text)
            btn_c.setMinimumSize(110, 40)
            btn_c.setCursor(Qt.PointingHandCursor)
            btn_c.setStyleSheet(f"""
                QPushButton {{
                    background: {cancel_bg};
                    color: white;
                    padding: 8px 18px;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {cancel_hover};
                }}
            """)
            btn_c.clicked.connect(self._do_cancel)
            lay.addWidget(btn_c)

        btn_ok = QPushButton(self._ok_text)
        btn_ok.setMinimumSize(110, 40)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: {self._theme['btn_ok_bg']};
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {self._theme['btn_ok_hover']};
            }}
        """)
        btn_ok.clicked.connect(self._do_ok)
        lay.addWidget(btn_ok)

        ftr.setLayout(lay)
        return ftr

    def _center(self):
        if self.parent() and self.parent().window():
            pg = self.parent().window().frameGeometry()
            self.move(
                pg.x() + (pg.width() - self.width()) // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )
        else:
            sg = QApplication.primaryScreen().availableGeometry()
            self.move(
                sg.x() + (sg.width() - self.width()) // 2,
                sg.y() + (sg.height() - self.height()) // 2,
            )

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._center)

    def _do_ok(self):
        self.ok_clicked.emit()
        self.accept()

    def _do_cancel(self):
        self.cancel_clicked.emit()
        self.reject()

    # ---------- API statique ----------

    @staticmethod
    def info(parent, title: str, message: str,
             width: int = 480, height: int = 240, is_dark: bool = None):
        InfoDialog(
            parent, title, message, DialogType.INFO, width, height,
            ok_text="OK", is_dark=is_dark,
        ).exec()

    @staticmethod
    def information(parent, title: str, message: str, **kw):
        InfoDialog.info(parent, title, message, **kw)

    @staticmethod
    def warning(parent, title: str, message: str,
                width: int = 480, height: int = 240, is_dark: bool = None):
        InfoDialog(
            parent, title, message, DialogType.WARNING, width, height,
            ok_text="Compris", is_dark=is_dark,
        ).exec()

    @staticmethod
    def error(parent, title: str, message: str,
              width: int = 480, height: int = 260, is_dark: bool = None):
        InfoDialog(
            parent, title, message, DialogType.ERROR, width, height,
            ok_text="Fermer", is_dark=is_dark,
        ).exec()

    @staticmethod
    def critical(parent, title: str, message: str, **kw):
        InfoDialog.error(parent, title, message, **kw)

    @staticmethod
    def success(parent, title: str, message: str,
                width: int = 480, height: int = 240, is_dark: bool = None):
        InfoDialog(
            parent, title, message, DialogType.SUCCESS, width, height,
            ok_text="OK", is_dark=is_dark,
        ).exec()

    @staticmethod
    def question(
        parent,
        title: str,
        message: str,
        ok_text: str = "Yes",
        cancel_text: str = "No",
        width: int = 480,
        height: int = 240,
        is_dark: bool = None,
    ) -> bool:
        """Retourne True si l'utilisateur confirme (Yes)."""
        dlg = InfoDialog(
            parent,
            title,
            message,
            DialogType.QUESTION,
            width,
            height,
            show_cancel=True,
            ok_text=ok_text,
            cancel_text=cancel_text,
            is_dark=is_dark,
        )
        return dlg.exec() == QDialog.Accepted

    @staticmethod
    def rich(
        parent,
        title: str,
        content_widget: QWidget,
        dialog_type: str = DialogType.INFO,
        width: int = 600,
        height: int = 400,
        ok_text: str = "OK",
        is_dark: bool = None,
    ):
        """Affiche un dialogue avec un widget de contenu personnalise."""
        InfoDialog(
            parent, title, "", dialog_type, width, height,
            ok_text=ok_text, content_widget=content_widget, is_dark=is_dark,
        ).exec()