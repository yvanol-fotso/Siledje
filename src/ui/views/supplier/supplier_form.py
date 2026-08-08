"""
Formulaire fournisseur — sans styles hardcodés (thème global / modal).
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QLabel, QTextEdit,
)


class SupplierForm(QWidget):
    def __init__(self, supplier: dict = None, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.is_edit = supplier is not None
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(8, 8, 8, 8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du fournisseur")
        self.name_input.setMinimumHeight(36)
        if self.supplier:
            self.name_input.setText(self.supplier.get("name", ""))
        layout.addRow(QLabel("Nom *:"), self.name_input)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Nom du contact")
        self.contact_input.setMinimumHeight(36)
        if self.supplier:
            self.contact_input.setText(self.supplier.get("contact_name") or "")
        layout.addRow(QLabel("Contact:"), self.contact_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Telephone principal")
        self.phone_input.setMinimumHeight(36)
        if self.supplier:
            self.phone_input.setText(self.supplier.get("phone") or "")
        layout.addRow(QLabel("Telephone:"), self.phone_input)

        self.phone2_input = QLineEdit()
        self.phone2_input.setPlaceholderText("Telephone secondaire")
        self.phone2_input.setMinimumHeight(36)
        if self.supplier:
            self.phone2_input.setText(self.supplier.get("phone2") or "")
        layout.addRow(QLabel("Telephone 2:"), self.phone2_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.setMinimumHeight(36)
        if self.supplier:
            self.email_input.setText(self.supplier.get("email") or "")
        layout.addRow(QLabel("Email:"), self.email_input)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Ville")
        self.city_input.setMinimumHeight(36)
        if self.supplier:
            self.city_input.setText(self.supplier.get("city") or "")
        layout.addRow(QLabel("Ville:"), self.city_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Adresse complete")
        self.address_input.setMinimumHeight(36)
        if self.supplier:
            self.address_input.setText(self.supplier.get("address") or "")
        layout.addRow(QLabel("Adresse:"), self.address_input)

        self.terms_input = QLineEdit()
        self.terms_input.setPlaceholderText("Conditions de paiement")
        self.terms_input.setMinimumHeight(36)
        if self.supplier:
            self.terms_input.setText(self.supplier.get("payment_terms") or "")
        layout.addRow(QLabel("Conditions de paiement:"), self.terms_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(70)
        if self.supplier:
            self.notes_input.setText(self.supplier.get("notes") or "")
        layout.addRow(QLabel("Notes:"), self.notes_input)

        self.setLayout(layout)

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "contact_name": self.contact_input.text().strip() or None,
            "phone": self.phone_input.text().strip() or None,
            "phone2": self.phone2_input.text().strip() or None,
            "email": self.email_input.text().strip() or None,
            "city": self.city_input.text().strip() or None,
            "address": self.address_input.text().strip() or None,
            "payment_terms": self.terms_input.text().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

    def validate(self) -> tuple:
        if not self.name_input.text().strip():
            return False, "Le nom du fournisseur est obligatoire."
        return True, ""