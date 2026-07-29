"""
Formulaire pour la gestion des utilisateurs.
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox,
    QCheckBox, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt


class AdminUserForm(QWidget):
    """Formulaire de création/modification d'utilisateur."""

    def __init__(self, user=None, roles: list = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.roles = roles or []
        self.is_edit = user is not None
        self._init_ui()

    def _init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        input_style = """
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #2c3e50;
                min-height: 40px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #567ba1;
            }
        """

        def create_label(text):
            l = QLabel(text)
            l.setStyleSheet(label_style)
            return l

        # Nom d'utilisateur
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(input_style)
        self.username_input.setPlaceholderText("Nom d'utilisateur unique")
        if self.user:
            self.username_input.setText(self.user.username)
        layout.addRow(create_label("Nom d'utilisateur *:"), self.username_input)

        # Nom complet
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        self.name_input.setPlaceholderText("Nom complet")
        if self.user:
            self.name_input.setText(self.user.name)
        layout.addRow(create_label("Nom complet *:"), self.name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(input_style)
        self.email_input.setPlaceholderText("email@example.com")
        if self.user:
            self.email_input.setText(self.user.email)
        layout.addRow(create_label("Email:"), self.email_input)

        # Mot de passe
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(input_style)
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.is_edit:
            self.password_input.setPlaceholderText("Laisser vide pour ne pas changer")
        else:
            self.password_input.setPlaceholderText("Mot de passe (minimum 6 caractères)")
        pwd_label = "Mot de passe *:" if not self.is_edit else "Nouveau mot de passe:"
        layout.addRow(create_label(pwd_label), self.password_input)

        # Rôle
        self.role_combo = QComboBox()
        self.role_combo.setStyleSheet(input_style)
        for role in self.roles:
            self.role_combo.addItem(role)
        if self.user and self.user.role:
            idx = self.role_combo.findText(self.user.role)
            if idx >= 0:
                self.role_combo.setCurrentIndex(idx)
        layout.addRow(create_label("Rôle *:"), self.role_combo)

        # Actif
        self.active_checkbox = QCheckBox("Compte actif")
        self.active_checkbox.setStyleSheet("font-size: 14px; color: #2c3e50;")
        self.active_checkbox.setChecked(True if not self.user else self.user.is_active)
        layout.addRow(create_label(""), self.active_checkbox)

        self.setLayout(layout)

    def get_data(self) -> dict:
        """Récupère les données du formulaire."""
        return {
            'username': self.username_input.text().strip(),
            'full_name': self.name_input.text().strip(),
            'email': self.email_input.text().strip() or None,
            'password': self.password_input.text().strip(),
            'role': self.role_combo.currentText(),
            'is_active': self.active_checkbox.isChecked(),
        }

    def validate(self) -> tuple:
        """Valide les données du formulaire."""
        username = self.username_input.text().strip()
        name = self.name_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not name:
            return False, "Le nom d'utilisateur et le nom complet sont obligatoires."

        if not self.is_edit and not password:
            return False, "Le mot de passe est obligatoire pour un nouvel utilisateur."

        if not self.is_edit and len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères."

        return True, ""