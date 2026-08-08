"""
InfoDialog — alertes / infos / confirmations thémées.
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
    from src.ui.views.base.base_view import Palette
except Exception:
    class Palette:  # fallback minimal
        TEAL = "#1abc9c"
        ACCENT = "#567ba1"
        DANGER = "#e74c3c"
        WARNING = "#e67e22"
        SUCCESS = "#2ecc71"
        INFO = "#3498db"
        DARK_BG = "#2c3e50"
        LIGHT_BG = "#ffffff"
        DARK_TEXT = "#e0e0e0"
        LIGHT_TEXT = "#2c3e50"


class DialogType:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    QUESTION = "question"


def _detect_dark(parent) -> bool:
    """Essaie de détecter le thème dark via parent / MainWindow."""
    w = parent
    while w is not None:
        if hasattr(w, "_is_dark"):
            return bool(w._is_dark)
        if hasattr(w, "theme_manager"):
            try:
                return w.theme_manager.current_theme == "dark"
            except Exception:
                pass
        w = w.parent() if hasattr(w, "parent") else None
    return True  # app Siledje est souvent en dark par défaut


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
        self._is_dark = _detect_dark(parent) if is_dark is None else is_dark
        self._theme = self._resolve_theme(dialog_type)
        self._build()

    def _resolve_theme(self, dialog_type: str) -> dict:
        accent_map = {
            DialogType.INFO: Palette.INFO if hasattr(Palette, "INFO") else "#3498db",
            DialogType.WARNING: Palette.WARNING if hasattr(Palette, "WARNING") else "#e67e22",
            DialogType.ERROR: Palette.DANGER,
            DialogType.SUCCESS: Palette.SUCCESS,
            DialogType.QUESTION: Palette.TEAL if self._is_dark else Palette.ACCENT,
        }
        accent = accent_map.get(dialog_type, "#3498db")
        hover = {
            DialogType.INFO: "#2980b9",
            DialogType.WARNING: "#d35400",
            DialogType.ERROR: "#c0392b",
            DialogType.SUCCESS: "#27ae60",
            DialogType.QUESTION: "#16a085" if self._is_dark else "#46648a",
        }.get(dialog_type, "#2980b9")

        if self._is_dark:
            return {
                "header_bg": accent,
                "header_hover": hover,
                "border": accent,
                "btn_ok_bg": accent,
                "btn_ok_hover": hover,
                "body_bg": "#1e2a38",
                "footer_bg": "#243447",
                "text": Palette.DARK_TEXT,
                "frame_bg": "#1e2a38",
            }
        return {
            "header_bg": accent,
            "header_hover": hover,
            "border": accent,
            "btn_ok_bg": accent,
            "btn_ok_hover": hover,
            "body_bg": "#ffffff",
            "footer_bg": "#ecf0f1",
            "text": Palette.LIGHT_TEXT,
            "frame_bg": "#ffffff",
        }

    def _build(self):
        self.setWindowTitle(self._title)
        self.setModal(True)
        self.setMinimumSize(self._width, self._height)
        self.resize(self._width, self._height)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

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
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        close = QPushButton("✕")
        close.setFixedSize(32, 32)
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet("""
            QPushButton {
                background: transparent; color: white;
                font-size: 16px; font-weight: bold;
                border: none; border-radius: 16px;
            }
            QPushButton:hover { background: rgba(0,0,0,0.25); }
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
            QScrollArea {{ background: {self._theme['body_bg']}; border: none; }}
            QScrollBar:vertical {{
                border: none; background: transparent; width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: #7f8c8d; border-radius: 5px; min-height: 24px;
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
                f"font-size: 14px; color: {self._theme['text']}; line-height: 1.5;"
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

        if self._show_cancel:
            btn_c = QPushButton(self._cancel_text)
            btn_c.setMinimumSize(110, 40)
            btn_c.setCursor(Qt.PointingHandCursor)
            btn_c.setStyleSheet(f"""
                QPushButton {{
                    background: {"#3d4f61" if self._is_dark else "#95a5a6"};
                    color: white; padding: 8px 18px;
                    border: none; border-radius: 8px;
                    font-weight: bold; font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {"#4a6178" if self._is_dark else "#7f8c8d"};
                }}
            """)
            btn_c.clicked.connect(self._do_cancel)
            lay.addWidget(btn_c)

        btn_ok = QPushButton(self._ok_text)
        btn_ok.setMinimumSize(110, 40)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: {self._theme['btn_ok_bg']}; color: white;
                padding: 8px 18px; border: none; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {self._theme['btn_ok_hover']}; }}
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
    def info(parent, title: str, message: str, width: int = 480, height: int = 240):
        InfoDialog(
            parent, title, message, DialogType.INFO, width, height, ok_text="OK"
        ).exec()

    @staticmethod
    def information(parent, title: str, message: str, **kw):
        InfoDialog.info(parent, title, message, **kw)

    @staticmethod
    def warning(parent, title: str, message: str, width: int = 480, height: int = 240):
        InfoDialog(
            parent, title, message, DialogType.WARNING, width, height, ok_text="Compris"
        ).exec()

    @staticmethod
    def error(parent, title: str, message: str, width: int = 480, height: int = 260):
        InfoDialog(
            parent, title, message, DialogType.ERROR, width, height, ok_text="Fermer"
        ).exec()

    @staticmethod
    def critical(parent, title: str, message: str, **kw):
        InfoDialog.error(parent, title, message, **kw)

    @staticmethod
    def success(parent, title: str, message: str, width: int = 480, height: int = 240):
        InfoDialog(
            parent, title, message, DialogType.SUCCESS, width, height, ok_text="OK"
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
        )
        return dlg.exec() == QDialog.Accepted


    @staticmethod
    def rich(parent, title: str, content_widget: QWidget,
            dialog_type: str = DialogType.INFO,
            width: int = 600, height: int = 400,
            ok_text: str = "OK"):
        """Affiche un dialogue avec un widget de contenu personnalisé (au lieu d'un simple message)."""
        InfoDialog(
            parent, title, "", dialog_type, width, height,
            ok_text=ok_text, content_widget=content_widget
        ).exec()