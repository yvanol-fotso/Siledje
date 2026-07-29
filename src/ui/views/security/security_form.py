"""
Formulaire de gestion des roles et permissions.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QGroupBox, QLabel
)
from PySide6.QtCore import Qt


# Permissions disponibles
AVAILABLE_PERMISSIONS = [
    ("can_manage_stock", "Gestion du stock"),
    ("can_manage_users", "Gestion des utilisateurs"),
    ("can_view_reports", "Rapports et statistiques"),
    ("can_manage_cameras", "Videosurveillance"),
    ("can_process_returns", "Traitement des retours"),
    ("can_manage_suppliers", "Gestion des fournisseurs"),
    ("can_configure_system", "Configuration systeme"),
]

SYSTEM_ROLES = {"admin", "gerant", "employe"}


class SecurityRoleForm(QWidget):
    """Formulaire de creation/modification d'un role."""

    def __init__(self, role: dict = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.is_edit = role is not None
        self._permission_checkboxes = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        input_style = """
            font-size: 14px;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2c3e50;
            min-height: 40px;
        """

        def create_label(text):
            l = QLabel(text)
            l.setStyleSheet(label_style)
            return l

        # Section informations
        info_layout = QFormLayout()
        info_layout.setSpacing(15)

        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        self.name_input.setPlaceholderText("Nom du role")
        if self.is_edit:
            self.name_input.setText(self.role.get("name", ""))
            if self.role.get("name") in SYSTEM_ROLES:
                self.name_input.setEnabled(False)
                self.name_input.setToolTip("Le nom des roles systeme ne peut pas etre modifie.")

        self.description_input = QLineEdit()
        self.description_input.setStyleSheet(input_style)
        self.description_input.setPlaceholderText("Description du role")
        if self.is_edit:
            self.description_input.setText(self.role.get("description") or "")

        info_layout.addRow(create_label("Nom du role *:"), self.name_input)
        info_layout.addRow(create_label("Description:"), self.description_input)
        layout.addLayout(info_layout)

        # Section permissions
        perm_group = QGroupBox("Permissions")
        perm_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: #ffffff;
            }
        """)
        perm_layout = QVBoxLayout()
        perm_layout.setSpacing(10)

        for perm_key, perm_label in AVAILABLE_PERMISSIONS:
            checkbox = QCheckBox(perm_label)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #2c3e50;
                    spacing: 8px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: #ffffff;
                }
                QCheckBox::indicator:checked {
                    background-color: #3498db;
                    border-color: #3498db;
                }
            """)
            if self.is_edit and self.role.get(perm_key, 0):
                checkbox.setChecked(True)
            self._permission_checkboxes[perm_key] = checkbox
            perm_layout.addWidget(checkbox)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        self.setLayout(layout)

    def get_data(self) -> dict:
        """Recupere les donnees du formulaire."""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.text().strip(),
            'permissions': {k: cb.isChecked() for k, cb in self._permission_checkboxes.items()}
        }

    def validate(self, existing_names: list = None, exclude_id: int = None) -> tuple:
        """Valide les donnees du formulaire."""
        name = self.name_input.text().strip()
        if not name:
            return False, "Le nom du role est obligatoire."

        # Verifier si le nom existe deja
        if existing_names:
            for n in existing_names:
                if n.lower() == name.lower():
                    return False, f"Le role '{name}' existe deja."

        selected = [k for k, cb in self._permission_checkboxes.items() if cb.isChecked()]
        if not selected:
            return False, "Veuillez selectionner au moins une permission."

        return True, ""