"""
Fenetre de saisie/activation de la cle de licence - Version finale agrandie.
Sans emojis. Dialogues = InfoDialog (plus de QMessageBox).
Light/Dark via Palette (meme source que BaseView / ModalForm).
"""

from src.utils.compat import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    Qt, QFont, Signal, QHBoxLayout, QFrame, QIcon,
)

from src.utils.helpers import get_asset_path
from src.ui.widgets.InfoDialog import InfoDialog

try:
    from src.ui.views.base.palette import Palette
except Exception:
    class Palette:
        TEAL = "#1abc9c"
        ACCENT = "#3498db"
        DANGER = "#e74c3c"
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
                }
            return {
                "bg": "#f5f5f5",
                "text": "#2c3e50",
                "border": "#bdc3c7",
                "hover": "rgba(52, 152, 219, 0.12)",
            }


class LicenseDialog(QDialog):
    """
    Boite de dialogue d'activation de licence - Version finale agrandie.
    Suit le theme clair/sombre de l'application.
    """

    license_activated = Signal()

    def __init__(
        self,
        license_manager,
        message: str = "",
        theme_manager=None,
        parent=None,
        is_dark: bool = None,
    ):
        super().__init__(parent)
        self.license_manager = license_manager
        self.theme_manager = theme_manager

        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif theme_manager is not None:
            try:
                self._is_dark = theme_manager.get_current_theme() == "dark"
            except Exception:
                self._is_dark = False
        else:
            self._is_dark = False

        self._setup_window()
        self._setup_ui(message)
        self._apply_theme()

    def _setup_window(self):
        """Configure la fenetre - AGRANDIE."""
        self.setWindowTitle("Activation de licence - Siledje")
        self.setFixedSize(560, 420)
        self.setWindowFlags(
            Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )

        app_icon_path = get_asset_path("icons", "app.png")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))

    def _setup_ui(self, message: str = ""):
        """Construit l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(20)

        self.title_label = QLabel("Activation de la licence")
        self.title_label.setObjectName("licenseTitle")
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.info_label = None
        if message:
            self.info_label = QLabel(message)
            self.info_label.setObjectName("licenseError")
            self.info_label.setWordWrap(True)
            self.info_label.setAlignment(Qt.AlignCenter)
            self.info_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            layout.addWidget(self.info_label)

        self.subtitle_label = QLabel(
            "Veuillez saisir votre cle de licence pour continuer."
        )
        self.subtitle_label.setObjectName("licenseSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setFont(QFont("Segoe UI", 13))
        layout.addWidget(self.subtitle_label)

        layout.addSpacing(15)

        self.txt_key = QLineEdit()
        self.txt_key.setObjectName("licenseInput")
        self.txt_key.setPlaceholderText("SILEDJE-PRO-XXXXXXXX-XXXXXXXX")
        self.txt_key.setMinimumHeight(52)
        self.txt_key.setFont(QFont("Segoe UI", 15))
        layout.addWidget(self.txt_key)

        layout.addSpacing(15)

        self.btn_activate = QPushButton("Activer la licence")
        self.btn_activate.setObjectName("licenseActivateBtn")
        self.btn_activate.setMinimumHeight(52)
        self.btn_activate.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_activate.setCursor(Qt.PointingHandCursor)
        self.btn_activate.clicked.connect(self._activate)
        layout.addWidget(self.btn_activate)

        layout.addSpacing(15)

        self.contact_frame = QFrame()
        self.contact_frame.setObjectName("licenseContactFrame")
        contact_layout = QHBoxLayout(self.contact_frame)
        contact_layout.setContentsMargins(10, 6, 10, 6)

        self.contact_label = QLabel("support@siledje.cm  |  +237 694 122 436")
        self.contact_label.setObjectName("licenseContact")
        self.contact_label.setAlignment(Qt.AlignCenter)
        self.contact_label.setFont(QFont("Segoe UI", 13))
        contact_layout.addWidget(self.contact_label)

        layout.addWidget(self.contact_frame)
        layout.addStretch()

        self.txt_key.setFocus()
        self.txt_key.returnPressed.connect(self._activate)

    def _apply_theme(self):
        """Applique light/dark via Palette (comme BaseView / ModalForm)."""
        colors = Palette.get_theme_colors(self._is_dark)
        accent = Palette.TEAL if self._is_dark else Palette.ACCENT
        accent_hover = (
            getattr(Palette, "TEAL_HOVER", "#16a085")
            if self._is_dark
            else getattr(Palette, "ACCENT_HOVER", "#2980b9")
        )
        text = colors["text"]
        bg = colors["bg"]
        border = colors["border"]
        text_sec = "#95a5a6" if self._is_dark else "#7f8c8d"
        danger = getattr(Palette, "DANGER", "#e74c3c")
        contact_bg = (
            "rgba(26, 188, 156, 0.12)"
            if self._is_dark
            else "rgba(52, 152, 219, 0.08)"
        )

        self.setProperty("theme", "dark" if self._is_dark else "light")

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg};
                color: {text};
            }}
            QLabel#licenseTitle {{
                color: {text};
                background: transparent;
            }}
            QLabel#licenseSubtitle {{
                color: {text_sec};
                background: transparent;
            }}
            QLabel#licenseError {{
                color: {danger};
                background: transparent;
                font-weight: bold;
            }}
            QLineEdit#licenseInput {{
                background-color: {bg};
                color: {text};
                border: 2px solid {accent};
                border-radius: 10px;
                padding: 10px 16px;
                selection-background-color: {accent};
            }}
            QLineEdit#licenseInput:focus {{
                border: 2px solid {accent_hover};
            }}
            QPushButton#licenseActivateBtn {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }}
            QPushButton#licenseActivateBtn:hover {{
                background-color: {accent_hover};
            }}
            QPushButton#licenseActivateBtn:pressed {{
                background-color: {accent_hover};
            }}
            QPushButton#licenseActivateBtn:disabled {{
                background-color: {text_sec};
                color: {bg};
            }}
            QFrame#licenseContactFrame {{
                background-color: {contact_bg};
                border-radius: 8px;
                border: 1px solid {border};
            }}
            QLabel#licenseContact {{
                color: {text_sec};
                background: transparent;
            }}
        """)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def apply_theme(self, is_dark: bool = None):
        """API publique pour la propagation de theme (comme les vues)."""
        if is_dark is not None:
            self._is_dark = bool(is_dark)
        elif self.theme_manager is not None:
            try:
                self._is_dark = self.theme_manager.get_current_theme() == "dark"
            except Exception:
                pass
        self._apply_theme()

    def _activate(self):
        """Active la licence."""
        key = self.txt_key.text().strip()
        if not key:
            InfoDialog.warning(
                self,
                "Champ requis",
                "Veuillez saisir une cle de licence.",
                is_dark=self._is_dark,
            )
            return

        if self.license_manager.activate_license(key):
            InfoDialog.success(
                self,
                "Succes",
                "Licence activee avec succes.",
                is_dark=self._is_dark,
            )
            self.license_activated.emit()
            self.accept()
        else:
            InfoDialog.error(
                self,
                "Cle invalide",
                "Cette cle de licence est invalide ou expiree.\n"
                "Verifiez la saisie ou contactez le support.",
                is_dark=self._is_dark,
            )
            self.txt_key.clear()
            self.txt_key.setFocus()