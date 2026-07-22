"""Fenêtre de saisie/activation de la clé de licence."""

from src.utils.compat import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    Qt, QFont, Signal
)


class LicenseDialog(QDialog):

    license_activated = Signal()

    def __init__(self, license_manager, message: str = "", parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("Activation de licence - Siledje")
        self.setFixedSize(440, 320)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(14)

        title = QLabel("Activation requise")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        if message:
            info = QLabel(message)
            info.setWordWrap(True)
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(info)

        subtitle = QLabel("Veuillez saisir votre clé de licence pour continuer.")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("SILEDJE-PRO-XXXXXXXX-XXXXXXXX")
        self.txt_key.setMinimumHeight(42)
        layout.addWidget(self.txt_key)

        btn_activate = QPushButton("Activer")
        btn_activate.setMinimumHeight(42)
        btn_activate.clicked.connect(self._activate)
        layout.addWidget(btn_activate)

        contact = QLabel("Pour obtenir une licence : support@siledje.cm")
        contact.setAlignment(Qt.AlignCenter)
        contact.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(contact)

        layout.addStretch()

    def _activate(self):
        key = self.txt_key.text().strip()
        if not key:
            QMessageBox.warning(self, "Champ requis", "Veuillez saisir une clé de licence.")
            return

        if self.license_manager.activate_license(key):
            QMessageBox.information(self, "Succès", "Licence activée avec succès !")
            self.license_activated.emit()
            self.accept()
        else:
            QMessageBox.critical(
                self, "Clé invalide",
                "Cette clé de licence est invalide ou expirée.\n"
                "Vérifiez la saisie ou contactez le support."
            )