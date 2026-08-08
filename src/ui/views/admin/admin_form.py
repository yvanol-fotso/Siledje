"""
Formulaire création / modification utilisateur.
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel,
)


class AdminUserForm(QWidget):
    def __init__(self, user=None, roles: list = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.roles = roles or []
        self.is_edit = user is not None
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(8, 8, 8, 8)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur unique")
        self.username_input.setMinimumHeight(40)
        if self.user:
            self.username_input.setText(self.user.username)
        layout.addRow(QLabel("Nom d'utilisateur *:"), self.username_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom complet")
        self.name_input.setMinimumHeight(40)
        if self.user:
            self.name_input.setText(self.user.name)
        layout.addRow(QLabel("Nom complet *:"), self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.setMinimumHeight(40)
        if self.user:
            self.email_input.setText(self.user.email)
        layout.addRow(QLabel("Email:"), self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        if self.is_edit:
            self.password_input.setPlaceholderText("Laisser vide pour ne pas changer")
        else:
            self.password_input.setPlaceholderText("Mot de passe (min. 6 caracteres)")
        pwd_label = "Mot de passe *:" if not self.is_edit else "Nouveau mot de passe:"
        layout.addRow(QLabel(pwd_label), self.password_input)

        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(40)
        for role in self.roles:
            self.role_combo.addItem(role)
        if self.user and self.user.role:
            idx = self.role_combo.findText(self.user.role)
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)
        layout.addRow(QLabel("Role *:"), self.role_combo)

        self.active_checkbox = QCheckBox("Compte actif")
        self.active_checkbox.setChecked(
            True if not self.user else self.user.is_active
        )
        layout.addRow(QLabel(""), self.active_checkbox)

        self.setLayout(layout)

    def get_data(self) -> dict:
        return {
            "username": self.username_input.text().strip(),
            "full_name": self.name_input.text().strip(),
            "email": self.email_input.text().strip() or None,
            "password": self.password_input.text().strip(),
            "role": self.role_combo.currentText(),
            "is_active": self.active_checkbox.isChecked(),
        }

    def validate(self) -> tuple:
        username = self.username_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not name:
            return False, "Le nom d'utilisateur et le nom complet sont obligatoires."
        if not self.is_edit and not password:
            return False, "Le mot de passe est obligatoire pour un nouvel utilisateur."
        if not self.is_edit and len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caracteres."
        return True, ""