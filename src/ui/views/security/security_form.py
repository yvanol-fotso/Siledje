"""
Formulaire role / permissions — sans CSS hardcode massif.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QGroupBox, QLabel,
)

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
    def __init__(self, role: dict = None, parent=None):
        super().__init__(parent)
        self.role = role
        self.is_edit = role is not None
        self._permission_checkboxes = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(8, 8, 8, 8)

        info = QFormLayout()
        info.setSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du role")
        self.name_input.setMinimumHeight(40)
        if self.is_edit:
            self.name_input.setText(self.role.get("name", ""))
            if self.role.get("name") in SYSTEM_ROLES:
                self.name_input.setEnabled(False)
                self.name_input.setToolTip(
                    "Le nom des roles systeme ne peut pas etre modifie."
                )
        info.addRow(QLabel("Nom du role *:"), self.name_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description du role")
        self.description_input.setMinimumHeight(40)
        if self.is_edit:
            self.description_input.setText(self.role.get("description") or "")
        info.addRow(QLabel("Description:"), self.description_input)
        layout.addLayout(info)

        perm_group = QGroupBox("Permissions")
        perm_layout = QVBoxLayout()
        perm_layout.setSpacing(8)

        for perm_key, perm_label in AVAILABLE_PERMISSIONS:
            cb = QCheckBox(perm_label)
            if self.is_edit and self.role.get(perm_key, 0):
                cb.setChecked(True)
            self._permission_checkboxes[perm_key] = cb
            perm_layout.addWidget(cb)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)
        self.setLayout(layout)

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "permissions": {
                k: cb.isChecked() for k, cb in self._permission_checkboxes.items()
            },
        }

    def validate(self, existing_names: list = None, exclude_id: int = None) -> tuple:
        name = self.name_input.text().strip()
        if not name:
            return False, "Le nom du role est obligatoire."
        if existing_names:
            for n in existing_names:
                if n and n.lower() == name.lower():
                    return False, f"Le role '{name}' existe deja."
        selected = [
            k for k, cb in self._permission_checkboxes.items() if cb.isChecked()
        ]
        if not selected:
            return False, "Veuillez selectionner au moins une permission."
        return True, ""