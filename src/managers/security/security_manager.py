"""
Gestionnaire de gestion des rôles et permissions.
Connecté à UserRepository (table roles réelle, conforme au schéma SILEDJE).
Version finale - combine structure optimisée et fonctionnalités complètes.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import (
    QMessageBox, QWidget, QFormLayout, QLineEdit, QLabel, 
    QVBoxLayout, QCheckBox, QGroupBox, QHBoxLayout, QPushButton
)

from src.database.repositories.user_repository import UserRepository


# Permissions réelles du schéma (colonne technique, libellé affiché)
AVAILABLE_PERMISSIONS = [
    ("can_manage_stock",       "Gestion du stock"),
    ("can_manage_users",       "Gestion des utilisateurs"),
    ("can_view_reports",       "Rapports et statistiques"),
    ("can_manage_cameras",     "Vidéosurveillance"),
    ("can_process_returns",    "Traitement des retours"),
    ("can_manage_suppliers",   "Gestion des fournisseurs"),
    ("can_configure_system",   "Configuration système"),
]

SYSTEM_ROLES = {"admin", "gérant", "employé"}


class RoleTableModel(QAbstractTableModel):
    """Modèle de table pour les rôles — lit directement les dicts du repository."""

    HEADERS = ["ID", "Nom du rôle", "Description", "Permissions actives"]

    def __init__(self, roles: list = None):
        super().__init__()
        self._roles = roles or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._roles)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        r = self._roles[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(r.get("id", ""))
            elif col == 1:
                return r.get("name", "")
            elif col == 2:
                return r.get("description") or "—"
            elif col == 3:
                active_count = sum(1 for key, _ in AVAILABLE_PERMISSIONS if r.get(key, 0))
                return f"{active_count}/{len(AVAILABLE_PERMISSIONS)} permission(s)"
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_role(self, row):
        return self._roles[row] if 0 <= row < len(self._roles) else None

    def set_roles(self, roles):
        self.beginResetModel()
        self._roles = roles
        self.endResetModel()


class SecurityManager(QObject):
    """
    Gestionnaire de gestion des rôles et permissions.
    Version finale avec support complet CRUD.
    """

    version = "2.0.0"

    def __init__(self, parent=None, user_repo=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None

        self.user_repo = user_repo if user_repo else UserRepository()

        self.roles = self.user_repo.get_all_roles()
        self.model = RoleTableModel(self.roles)

        print(f"[SecurityManager v{self.version}] Initialisé avec {len(self.roles)} rôles")

    def get_ui(self):
        """Retourne la vue de gestion des rôles et permissions."""
        if self.view is None:
            from src.ui.views.security_view import SecurityView
            self.view = SecurityView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            print("[SecurityManager] Vue créée et initialisée")
        return self.view

    def _initialize_view(self):
        """Initialise la vue avec le modèle."""
        self.view.set_table_model(self.model)

    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_role_requested.connect(self.add_role)
        self.view.edit_role_requested.connect(self.edit_role)
        self.view.delete_role_requested.connect(self.delete_role)
        self.view.refresh_requested.connect(self.refresh)

    # ========== FORMULAIRE ==========

    def _create_role_form(self, role: dict = None):
        """
        Crée un formulaire modale pour l'ajout ou la modification d'un rôle.
        Utilise ModalView pour une expérience utilisateur cohérente.
        """
        from src.ui.widgets.ModalView import ModalView

        is_edit = role is not None
        modal = ModalView(
            title="Modifier le rôle" if is_edit else "Nouveau rôle",
            parent=self.view, width=800, height=700,
            ok_text="Enregistrer", cancel_text="Annuler"
        )

        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)

        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        input_style = """
            font-size: 14px; padding: 10px; border: 2px solid #bdc3c7;
            border-radius: 8px; background-color: #ffffff; color: #2c3e50; min-height: 40px;
        """

        def create_label(text):
            l = QLabel(text)
            l.setStyleSheet(label_style)
            return l

        # Section informations
        info_layout = QFormLayout()
        info_layout.setSpacing(15)

        name_input = QLineEdit()
        name_input.setStyleSheet(input_style)
        name_input.setPlaceholderText("Nom du rôle")
        if is_edit:
            name_input.setText(role.get("name", ""))
            if role.get("name") in SYSTEM_ROLES:
                name_input.setEnabled(False)
                name_input.setToolTip("Le nom des rôles système ne peut pas être modifié.")

        description_input = QLineEdit()
        description_input.setStyleSheet(input_style)
        description_input.setPlaceholderText("Description du rôle")
        if is_edit:
            description_input.setText(role.get("description") or "")

        info_layout.addRow(create_label("Nom du rôle *:"), name_input)
        info_layout.addRow(create_label("Description:"), description_input)
        form_layout.addLayout(info_layout)

        # Section permissions
        perm_group = QGroupBox("Permissions")
        perm_group.setStyleSheet("""
            QGroupBox { 
                font-size: 15px; font-weight: bold; 
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

        permission_checkboxes = {}
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
            if is_edit and role.get(perm_key, 0):
                checkbox.setChecked(True)
            permission_checkboxes[perm_key] = checkbox
            perm_layout.addWidget(checkbox)

        perm_group.setLayout(perm_layout)
        form_layout.addWidget(perm_group)

        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)

        # Stocker les références pour validation
        modal.name_input = name_input
        modal.description_input = description_input
        modal.permission_checkboxes = permission_checkboxes

        return modal

    def _validate_role_form(self, modal, exclude_id=None):
        """Valide les données du formulaire."""
        name = modal.name_input.text().strip()
        if not name:
            QMessageBox.warning(self.view, "Validation", "Le nom du rôle est obligatoire.")
            return False

        if self.user_repo.role_name_exists(name, exclude_id=exclude_id):
            QMessageBox.warning(self.view, "Validation",
                                f"Le rôle '{name}' existe déjà.")
            return False

        selected = [k for k, cb in modal.permission_checkboxes.items() if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self.view, "Validation",
                                "Veuillez sélectionner au moins une permission.")
            return False

        return True

    # ========== SLOTS ==========

    @Slot(str)
    def on_search_requested(self, search_text: str):
        """Recherche un rôle par nom."""
        search_text = search_text.strip().lower()
        all_roles = self.user_repo.get_all_roles()
        if search_text:
            all_roles = [r for r in all_roles if search_text in r.get("name", "").lower()]
        self.roles = all_roles
        self.model.set_roles(self.roles)
        print(f"[SecurityManager] Recherche: {len(all_roles)} rôles trouvés")

    @Slot()
    def add_role(self):
        """Ajoute un nouveau rôle."""
        try:
            modal = self._create_role_form()

            def on_save():
                if not self._validate_role_form(modal):
                    return

                perms = {k: cb.isChecked() for k, cb in modal.permission_checkboxes.items()}
                name = modal.name_input.text().strip()

                self.user_repo.create_role(
                    name=name,
                    description=modal.description_input.text().strip(),
                    **perms
                )

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"Le rôle '{name}' a été créé avec succès.")
                print(f"[SecurityManager] Rôle créé: {name}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de l'ajout du rôle:\n{e}")
            print(f"[SecurityManager] ERREUR ajout rôle: {e}")

    @Slot(int)
    def edit_role(self, row: int):
        """Modifie un rôle existant."""
        role = self.model.get_role(row)
        if not role:
            QMessageBox.warning(self.view, "Sélection requise", "Sélectionnez un rôle à modifier.")
            return

        try:
            modal = self._create_role_form(role)

            def on_save():
                if not self._validate_role_form(modal, exclude_id=role["id"]):
                    return

                perms = {k: cb.isChecked() for k, cb in modal.permission_checkboxes.items()}
                new_name = modal.name_input.text().strip()

                # Si c'est un rôle système, on ne modifie pas le nom
                name_to_update = None if role.get("name") in SYSTEM_ROLES else new_name

                self.user_repo.update_role(
                    role["id"],
                    name=name_to_update,
                    description=modal.description_input.text().strip(),
                    **perms
                )

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"Le rôle '{role['name']}' a été modifié avec succès.")
                print(f"[SecurityManager] Rôle modifié: ID {role['id']}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la modification:\n{e}")
            print(f"[SecurityManager] ERREUR modification rôle: {e}")

    @Slot(int)
    def delete_role(self, row: int):
        """Supprime un rôle."""
        role = self.model.get_role(row)
        if not role:
            QMessageBox.warning(self.view, "Sélection requise", "Sélectionnez un rôle à supprimer.")
            return

        # Vérification des rôles système
        if role.get("name") in SYSTEM_ROLES:
            QMessageBox.warning(self.view, "Suppression impossible",
                f"Le rôle '{role['name']}' est un rôle système et ne peut pas être supprimé.")
            return

        # Vérification des utilisateurs associés
        users_count = self.user_repo.count_users_with_role(role["id"])
        if users_count > 0:
            QMessageBox.warning(self.view, "Suppression impossible",
                f"{users_count} utilisateur(s) ont encore ce rôle.\n"
                "Réassignez-les à un autre rôle avant de supprimer celui-ci.")
            return

        # Confirmation
        reply = QMessageBox.question(
            self.view, "Confirmer la suppression",
            f"Supprimer le rôle '{role['name']}' ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.user_repo.db.get_cursor()
                cursor.execute("DELETE FROM roles WHERE id = ?", (role["id"],))
                self.user_repo.db.commit()
                self.refresh()
                QMessageBox.information(self.view, "Succès", f"Rôle '{role['name']}' supprimé.")
                print(f"[SecurityManager] Rôle supprimé: ID {role['id']}")
            except Exception as e:
                QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la suppression:\n{e}")

    @Slot()
    def refresh(self):
        """Rafraîchit la liste des rôles depuis la base de données."""
        self.roles = self.user_repo.get_all_roles()
        self.model.set_roles(self.roles)
        print(f"[SecurityManager] Vue rafraîchie: {len(self.roles)} rôles")