"""
Formulaire de gestion des fournisseurs.
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QLabel, QTextEdit
)
from PySide6.QtCore import Qt


class SupplierForm(QWidget):
    """Formulaire de creation/modification d'un fournisseur."""

    def __init__(self, supplier: dict = None, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.is_edit = supplier is not None
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        inp_s = """
            font-size: 14px;
            padding: 8px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            min-height: 36px;
        """
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(label_style)
            return l

        # Nom
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(inp_s)
        self.name_input.setPlaceholderText("Nom du fournisseur")
        if self.supplier:
            self.name_input.setText(self.supplier.get("name", ""))
        layout.addRow(lbl("Nom *:"), self.name_input)

        # Contact
        self.contact_input = QLineEdit()
        self.contact_input.setStyleSheet(inp_s)
        self.contact_input.setPlaceholderText("Nom du contact")
        if self.supplier:
            self.contact_input.setText(self.supplier.get("contact_name", ""))
        layout.addRow(lbl("Contact:"), self.contact_input)

        # Telephone
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet(inp_s)
        self.phone_input.setPlaceholderText("Telephone principal")
        if self.supplier:
            self.phone_input.setText(self.supplier.get("phone", ""))
        layout.addRow(lbl("Telephone:"), self.phone_input)

        # Telephone 2
        self.phone2_input = QLineEdit()
        self.phone2_input.setStyleSheet(inp_s)
        self.phone2_input.setPlaceholderText("Telephone secondaire")
        if self.supplier:
            self.phone2_input.setText(self.supplier.get("phone2", ""))
        layout.addRow(lbl("Telephone 2:"), self.phone2_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(inp_s)
        self.email_input.setPlaceholderText("email@example.com")
        if self.supplier:
            self.email_input.setText(self.supplier.get("email", ""))
        layout.addRow(lbl("Email:"), self.email_input)

        # Ville
        self.city_input = QLineEdit()
        self.city_input.setStyleSheet(inp_s)
        self.city_input.setPlaceholderText("Ville")
        if self.supplier:
            self.city_input.setText(self.supplier.get("city", ""))
        layout.addRow(lbl("Ville:"), self.city_input)

        # Adresse
        self.address_input = QLineEdit()
        self.address_input.setStyleSheet(inp_s)
        self.address_input.setPlaceholderText("Adresse complete")
        if self.supplier:
            self.address_input.setText(self.supplier.get("address", ""))
        layout.addRow(lbl("Adresse:"), self.address_input)

        # Conditions de paiement
        self.terms_input = QLineEdit()
        self.terms_input.setStyleSheet(inp_s)
        self.terms_input.setPlaceholderText("Conditions de paiement")
        if self.supplier:
            self.terms_input.setText(self.supplier.get("payment_terms", ""))
        layout.addRow(lbl("Conditions de paiement:"), self.terms_input)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(inp_s)
        self.notes_input.setMaximumHeight(70)
        if self.supplier:
            self.notes_input.setText(self.supplier.get("notes", ""))
        layout.addRow(lbl("Notes:"), self.notes_input)

        self.setLayout(layout)

    def get_data(self) -> dict:
        """Recupere les donnees du formulaire."""
        return {
            'name': self.name_input.text().strip(),
            'contact_name': self.contact_input.text().strip() or None,
            'phone': self.phone_input.text().strip() or None,
            'phone2': self.phone2_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'city': self.city_input.text().strip() or None,
            'address': self.address_input.text().strip() or None,
            'payment_terms': self.terms_input.text().strip() or None,
            'notes': self.notes_input.toPlainText().strip() or None,
        }

    def validate(self) -> tuple:
        """Valide les donnees du formulaire."""
        if not self.name_input.text().strip():
            return False, "Le nom du fournisseur est obligatoire."
        return True, ""