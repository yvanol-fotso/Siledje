"""
Fenetre de saisie/activation de la cle de licence - Version finale agrandie.
Sans emojis. Dialogues = InfoDialog (plus de QMessageBox).
"""

from src.utils.compat import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    Qt, QFont, Signal, QHBoxLayout, QFrame, QIcon
)

from src.utils.helpers import get_asset_path
from src.ui.widgets.InfoDialog import InfoDialog


class LicenseDialog(QDialog):
    """
    Boite de dialogue d'activation de licence - Version finale agrandie.
    """

    license_activated = Signal()

    def __init__(self, license_manager, message: str = "", parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self._setup_window()
        self._setup_ui(message)

    def _setup_window(self):
        """Configure la fenetre - AGRANDIE."""
        self.setWindowTitle("Activation de licence - Siledje")
        self.setFixedSize(560, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        app_icon_path = get_asset_path("icons", "app.png")
        if app_icon_path.exists():
            self.setWindowIcon(QIcon(str(app_icon_path)))

    def _setup_ui(self, message: str = ""):
        """Construit l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(20)

        # Titre
        title = QLabel("Activation de la licence")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Message d'erreur eventuel
        if message:
            info = QLabel(message)
            info.setWordWrap(True)
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
            layout.addWidget(info)

        # Sous-titre
        subtitle = QLabel("Veuillez saisir votre cle de licence pour continuer.")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 13))
        layout.addWidget(subtitle)

        layout.addSpacing(15)

        # Champ de saisie
        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("SILEDJE-PRO-XXXXXXXX-XXXXXXXX")
        self.txt_key.setMinimumHeight(52)
        self.txt_key.setFont(QFont("Segoe UI", 15))
        layout.addWidget(self.txt_key)

        layout.addSpacing(15)

        # Bouton activer
        btn_activate = QPushButton("Activer la licence")
        btn_activate.setMinimumHeight(52)
        btn_activate.setFont(QFont("Segoe UI", 13, QFont.Bold))
        btn_activate.setCursor(Qt.PointingHandCursor)
        btn_activate.clicked.connect(self._activate)
        layout.addWidget(btn_activate)

        layout.addSpacing(15)

        # Contact
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(52, 152, 219, 0.08);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        contact_layout = QHBoxLayout(contact_frame)
        contact_layout.setContentsMargins(10, 6, 10, 6)

        contact = QLabel("support@siledje.cm  |  +237 694 122 436")
        contact.setAlignment(Qt.AlignCenter)
        contact.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        contact_layout.addWidget(contact)

        layout.addWidget(contact_frame)
        layout.addStretch()

        # Focus sur le champ
        self.txt_key.setFocus()

    def _activate(self):
        """Active la licence."""
        key = self.txt_key.text().strip()
        if not key:
            InfoDialog.warning(self, "Champ requis", "Veuillez saisir une cle de licence.")
            return

        if self.license_manager.activate_license(key):
            InfoDialog.success(self, "Succes", "Licence activee avec succes.")
            self.license_activated.emit()
            self.accept()
        else:
            InfoDialog.error(
                self, "Cle invalide",
                "Cette cle de licence est invalide ou expiree.\n"
                "Verifiez la saisie ou contactez le support."
            )
            self.txt_key.clear()
            self.txt_key.setFocus()