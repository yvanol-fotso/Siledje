"""
InfoDialog - Widget générique léger pour alertes, infos et confirmations simples.
Inspiré de ModalView.py mais SANS boutons OK/Annuler complexes et SANS manager.

Emplacement: src/ui/widgets/InfoDialog.py

Usage rapide (statique):
    InfoDialog.info(parent, "Titre", "Message")
    InfoDialog.warning(parent, "Titre", "Message")
    InfoDialog.error(parent, "Titre", "Message")
    InfoDialog.success(parent, "Titre", "Message")

Usage avec widget personnalisé:
    dialog = InfoDialog(parent, title="Titre", content_widget=mon_widget)
    dialog.exec()
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QWidget, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer


# ========== TYPES DE DIALOG ==========

class DialogType:
    INFO    = "info"
    WARNING = "warning"
    ERROR   = "error"
    SUCCESS = "success"


# ========== THÈMES PAR TYPE ==========

_THEMES = {
    DialogType.INFO: {
        "header_bg":    "#3498db",
        "header_hover": "#2980b9",
        "border":       "#3498db",
        "btn_ok_bg":    "#3498db",
        "btn_ok_hover": "#2980b9",
    },
    DialogType.WARNING: {
        "header_bg":    "#e67e22",
        "header_hover": "#d35400",
        "border":       "#e67e22",
        "btn_ok_bg":    "#e67e22",
        "btn_ok_hover": "#d35400",
    },
    DialogType.ERROR: {
        "header_bg":    "#e74c3c",
        "header_hover": "#c0392b",
        "border":       "#e74c3c",
        "btn_ok_bg":    "#e74c3c",
        "btn_ok_hover": "#c0392b",
    },
    DialogType.SUCCESS: {
        "header_bg":    "#2ecc71",
        "header_hover": "#27ae60",
        "border":       "#2ecc71",
        "btn_ok_bg":    "#2ecc71",
        "btn_ok_hover": "#27ae60",
    },
}


class InfoDialog(QDialog):
    """
    Dialog générique léger.
    Utiliser pour tout affichage simple qui ne nécessite PAS de manager/view dédié.
    """

    ok_clicked     = Signal()
    cancel_clicked = Signal()

    def __init__(
        self,
        parent=None,
        title: str = "Information",
        message: str = "",
        dialog_type: str = DialogType.INFO,
        width: int = 580,
        height: int = 360,
        show_cancel: bool = False,
        ok_text: str = "Fermer",
        cancel_text: str = "Annuler",
        content_widget: QWidget = None,
    ):
        super().__init__(parent)

        self._title        = title
        self._message      = message
        self._type         = dialog_type
        self._width        = width
        self._height       = height
        self._show_cancel  = show_cancel
        self._ok_text      = ok_text
        self._cancel_text  = cancel_text
        self._custom       = content_widget
        self._theme        = _THEMES.get(dialog_type, _THEMES[DialogType.INFO])

        self._build()

    # ------------------------------------------------------------------
    # Construction UI (même pattern que ModalView)
    # ------------------------------------------------------------------

    def _build(self):
        self.setWindowTitle(self._title)
        self.setModal(True)
        self.setMinimumSize(self._width, self._height)
        self.resize(self._width, self._height)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Cadre principal
        frame = QFrame()
        frame.setObjectName("infoFrame")
        frame.setStyleSheet(f"""
            QFrame#infoFrame {{
                background-color: #ffffff;
                border: 3px solid {self._theme['border']};
                border-radius: 15px;
            }}
        """)

        inner = QVBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        inner.addWidget(self._make_header())
        inner.addWidget(self._make_sep())
        inner.addWidget(self._make_body(), 1)
        inner.addWidget(self._make_footer())

        frame.setLayout(inner)
        root.addWidget(frame)
        self.setLayout(root)

    def _make_header(self) -> QWidget:
        hdr = QWidget()
        hdr.setObjectName("infoHeader")
        hdr.setFixedHeight(60)
        hdr.setStyleSheet(f"""
            QWidget#infoHeader {{
                background-color: {self._theme['header_bg']};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)

        lay = QHBoxLayout()
        lay.setContentsMargins(25, 0, 20, 0)

        lbl = QLabel(self._title)
        lbl.setStyleSheet("font-size: 19px; font-weight: bold; color: white;")

        close = QPushButton("✕")
        close.setFixedSize(34, 34)
        close.setCursor(Qt.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: white;
                font-size: 20px; font-weight: bold;
                border: none; border-radius: 17px;
            }}
            QPushButton:hover {{ background: rgba(0,0,0,0.25); }}
        """)
        close.clicked.connect(self.reject)

        lay.addWidget(lbl)
        lay.addStretch()
        lay.addWidget(close)
        hdr.setLayout(lay)
        return hdr

    def _make_sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {self._theme['border']}; max-height: 2px;")
        return sep

    def _make_body(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: #ffffff; border: none; }
            QScrollBar:vertical { border: none; background: #f0f0f0;
                width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #bdc3c7;
                border-radius: 6px; min-height: 30px; }
            QScrollBar::handle:vertical:hover { background: #95a5a6; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { border: none; background: none; }
        """)

        wrapper = QWidget()
        wrapper.setStyleSheet("background: #ffffff;")
        lay = QVBoxLayout()
        lay.setContentsMargins(30, 25, 30, 20)
        lay.setSpacing(15)

        # Message texte simple
        if self._message:
            msg = QLabel(self._message)
            msg.setWordWrap(True)
            msg.setStyleSheet("font-size: 14px; color: #2c3e50; line-height: 1.6;")
            msg.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            lay.addWidget(msg)

        # Widget personnalisé
        if self._custom:
            lay.addWidget(self._custom)

        lay.addStretch()
        wrapper.setLayout(lay)
        scroll.setWidget(wrapper)
        return scroll

    def _make_footer(self) -> QWidget:
        ftr = QWidget()
        ftr.setFixedHeight(75)
        ftr.setObjectName("infoFooter")
        ftr.setStyleSheet("""
            QWidget#infoFooter {
                background: #ecf0f1;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)

        lay = QHBoxLayout()
        lay.setContentsMargins(25, 12, 25, 12)
        lay.setSpacing(12)
        lay.addStretch()

        if self._show_cancel:
            btn_c = QPushButton(self._cancel_text)
            btn_c.setMinimumSize(130, 48)
            btn_c.setCursor(Qt.PointingHandCursor)
            btn_c.setStyleSheet("""
                QPushButton { background:#95a5a6; color:white; padding:10px 22px;
                    border:none; border-radius:10px; font-weight:bold; font-size:14px; }
                QPushButton:hover { background:#7f8c8d; }
            """)
            btn_c.clicked.connect(self._do_cancel)
            lay.addWidget(btn_c)

        btn_ok = QPushButton(self._ok_text)
        btn_ok.setMinimumSize(130, 48)
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setStyleSheet(f"""
            QPushButton {{ background:{self._theme['btn_ok_bg']}; color:white;
                padding:10px 22px; border:none; border-radius:10px;
                font-weight:bold; font-size:14px; }}
            QPushButton:hover {{ background:{self._theme['btn_ok_hover']}; }}
        """)
        btn_ok.clicked.connect(self._do_ok)
        lay.addWidget(btn_ok)

        ftr.setLayout(lay)
        return ftr

    # ------------------------------------------------------------------
    # Centrage (même logique que ModalView)
    # ------------------------------------------------------------------

    def _center(self):
        if self.parent() and self.parent().window():
            pg = self.parent().window().frameGeometry()
            self.move(
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2
            )
        else:
            sg = QApplication.primaryScreen().availableGeometry()
            self.move(
                sg.x() + (sg.width()  - self.width())  // 2,
                sg.y() + (sg.height() - self.height()) // 2
            )

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._center)   # même trick que ModalView

    # ------------------------------------------------------------------
    # Slots privés
    # ------------------------------------------------------------------

    def _do_ok(self):
        self.ok_clicked.emit()
        self.accept()

    def _do_cancel(self):
        self.cancel_clicked.emit()
        self.reject()

    # ------------------------------------------------------------------
    # API statique pratique (4 méthodes)
    # ------------------------------------------------------------------

    @staticmethod
    def info(parent, title: str, message: str,
             width: int = 580, height: int = 340):
        InfoDialog(parent, title, message,
                   DialogType.INFO, width, height,
                   ok_text="Fermer").exec()

    @staticmethod
    def warning(parent, title: str, message: str,
                width: int = 580, height: int = 340):
        InfoDialog(parent, title, message,
                   DialogType.WARNING, width, height,
                   ok_text="Compris").exec()

    @staticmethod
    def error(parent, title: str, message: str,
              width: int = 580, height: int = 340):
        InfoDialog(parent, title, message,
                   DialogType.ERROR, width, height,
                   ok_text="Fermer").exec()

    @staticmethod
    def success(parent, title: str, message: str,
                width: int = 580, height: int = 340):
        InfoDialog(parent, title, message,
                   DialogType.SUCCESS, width, height,
                   ok_text="Fermer").exec()

    @staticmethod
    def rich(parent, title: str, widget: QWidget,
             dialog_type: str = DialogType.INFO,
             width: int = 680, height: int = 500,
             ok_text: str = "Fermer"):
        """Affiche un InfoDialog avec un widget personnalisé dans le corps."""
        InfoDialog(parent, title,
                   content_widget=widget,
                   dialog_type=dialog_type,
                   width=width, height=height,
                   ok_text=ok_text).exec()