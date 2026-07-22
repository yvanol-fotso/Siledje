"""
Gestionnaire de gestion des utilisateurs.
Connecté à la vraie base de données via UserRepository + AuthManager.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox, QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel

from src.database.repositories.user_repository import UserRepository


class AdminUserRow:
    """Ligne d'affichage pour le tableau admin (pas le Bean d'auth)."""
    def __init__(self, id, username, name, email, role, is_active, last_login):
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        self.is_active = bool(is_active)
        self.last_login = last_login

    @classmethod
    def from_row(cls, row: dict) -> "AdminUserRow":
        return cls(
            id=row["id"],
            username=row["username"],
            name=row.get("full_name") or row["username"],
            email=row.get("email") or "",
            role=row.get("role_name") or "—",
            is_active=row.get("is_active", 1),
            last_login=row.get("last_login_at"),
        )


class UserTableModel(QAbstractTableModel):
    """Modèle de table pour les utilisateurs."""

    def __init__(self, users, headers):
        super().__init__()
        self._users = users
        self._headers = headers

    def rowCount(self, parent=None):
        return len(self._users)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        user = self._users[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0: return str(user.id)
            elif col == 1: return user.username
            elif col == 2: return user.name
            elif col == 3: return user.email
            elif col == 4: return user.role
            elif col == 5: return "Actif" if user.is_active else "Inactif"
            elif col == 6: return user.last_login or "Jamais"
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def get_user(self, row):
        if 0 <= row < len(self._users):
            return self._users[row]
        return None

    def set_users(self, users):
        """Remplace toutes les données et rafraîchit le tableau."""
        self.beginResetModel()
        self._users = users
        self.endResetModel()


class AdminManager(QObject):
    """Gestionnaire de gestion des utilisateurs — connecté à la BDD réelle."""

    version = "1.1.0"

    def __init__(self, parent=None, auth_manager=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user

        # auth_manager est injecté depuis MainWindow (voir instructions)
        self.auth_manager = auth_manager
        self.user_repo = auth_manager.user_repo if auth_manager else UserRepository()

        self.headers = ["ID", "Nom d'utilisateur", "Nom complet", "Email",
                         "Rôle", "Statut", "Dernière connexion"]

        self.roles = self._load_role_names()
        self.rows = self._load_users_from_db()
        self.model = UserTableModel(self.rows, self.headers)

        print(f"[AdminManager v{self.version}] Initialisé avec {len(self.rows)} utilisateurs")

    def _load_role_names(self):
        roles = self.user_repo.get_all_roles()
        return [r["name"] for r in roles] if roles else ["admin", "gérant", "employé"]

    def _load_users_from_db(self):
        rows = self.user_repo.get_all_users()
        return [AdminUserRow.from_row(r) for r in rows]

    def get_ui(self):
        if self.view is None:
            from src.ui.views.admin_view import AdminView
            self.view = AdminView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            print("[AdminManager] Vue créée et initialisée")
        return self.view

    def _initialize_view(self):
        self.view.set_table_model(self.model)

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_user_requested.connect(self.add_user)
        self.view.edit_user_requested.connect(self.edit_user)
        self.view.delete_user_requested.connect(self.delete_user)
        self.view.refresh_requested.connect(self.refresh)
        self.view.reset_password_requested.connect(self.reset_password)

    # ========== FORMULAIRE ==========

    def _create_user_form(self, row: AdminUserRow = None):
        from src.ui.widgets.ModalView import ModalView

        is_edit = row is not None
        title = "Modifier l'utilisateur" if is_edit else "Nouvel utilisateur"

        modal = ModalView(title=title, parent=self.view, width=700, height=600,
                          ok_text="Enregistrer", cancel_text="Annuler")

        form_widget = QWidget()
        form_layout = QFormLayout()
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

        username_input = QLineEdit()
        username_input.setStyleSheet(input_style)
        username_input.setPlaceholderText("Nom d'utilisateur unique")
        if is_edit:
            username_input.setText(row.username)

        name_input = QLineEdit()
        name_input.setStyleSheet(input_style)
        name_input.setPlaceholderText("Nom complet")
        if is_edit:
            name_input.setText(row.name)

        email_input = QLineEdit()
        email_input.setStyleSheet(input_style)
        email_input.setPlaceholderText("email@example.com")
        if is_edit:
            email_input.setText(row.email)

        password_input = QLineEdit()
        password_input.setStyleSheet(input_style)
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText(
            "Mot de passe" if not is_edit else "Laisser vide pour ne pas changer")

        role_combo = QComboBox()
        role_combo.setStyleSheet(input_style)
        role_combo.addItems(self.roles)
        if is_edit:
            role_combo.setCurrentText(row.role)

        active_checkbox = QCheckBox("Compte actif")
        active_checkbox.setStyleSheet("font-size: 14px; color: #2c3e50;")
        active_checkbox.setChecked(True if not is_edit else row.is_active)

        form_layout.addRow(create_label("Nom d'utilisateur *:"), username_input)
        form_layout.addRow(create_label("Nom complet *:"), name_input)
        form_layout.addRow(create_label("Email:"), email_input)
        pwd_label = "Mot de passe *:" if not is_edit else "Nouveau mot de passe:"
        form_layout.addRow(create_label(pwd_label), password_input)
        form_layout.addRow(create_label("Rôle *:"), role_combo)
        form_layout.addRow(create_label(""), active_checkbox)

        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)

        modal.username_input = username_input
        modal.name_input = name_input
        modal.email_input = email_input
        modal.password_input = password_input
        modal.role_combo = role_combo
        modal.active_checkbox = active_checkbox

        return modal

    def _validate_user_form(self, modal, is_edit=False, exclude_id=None):
        username = modal.username_input.text().strip()
        name = modal.name_input.text().strip()
        password = modal.password_input.text().strip()

        if not username or not name:
            QMessageBox.warning(self.view, "Validation",
                                "Le nom d'utilisateur et le nom complet sont obligatoires.")
            return False

        if not is_edit and not password:
            QMessageBox.warning(self.view, "Validation",
                                "Le mot de passe est obligatoire pour un nouvel utilisateur.")
            return False

        if not is_edit and len(password) < 6:
            QMessageBox.warning(self.view, "Validation",
                                "Le mot de passe doit contenir au moins 6 caractères.")
            return False

        if self.user_repo.username_exists(username, exclude_id=exclude_id):
            QMessageBox.warning(self.view, "Validation",
                                f"Le nom d'utilisateur '{username}' est déjà utilisé.")
            return False

        return True

    # ========== SLOTS ==========

    @Slot(str)
    def on_search_requested(self, search_text: str):
        search_text = search_text.strip().lower()
        if not search_text:
            filtered = self._load_users_from_db()
        else:
            all_rows = self._load_users_from_db()
            filtered = [r for r in all_rows
                       if search_text in r.username.lower()
                       or search_text in r.name.lower()
                       or search_text in r.email.lower()]
        self.rows = filtered
        self.model.set_users(self.rows)

    @Slot()
    def add_user(self):
        try:
            modal = self._create_user_form()

            def on_save():
                if not self._validate_user_form(modal, is_edit=False):
                    return

                role = self.user_repo.get_role_by_name(modal.role_combo.currentText())
                password_hash = self.auth_manager.hash_password(
                    modal.password_input.text().strip())

                new_id = self.user_repo.create_user(
                    username=modal.username_input.text().strip(),
                    password_hash=password_hash,
                    role_id=role["id"] if role else None,
                    full_name=modal.name_input.text().strip(),
                    email=modal.email_input.text().strip() or None,
                )
                if not modal.active_checkbox.isChecked():
                    self.user_repo.set_active(new_id, False)

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"L'utilisateur '{modal.name_input.text().strip()}' a été créé avec succès.")
                print(f"[AdminManager] Utilisateur créé: ID {new_id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de l'ajout de l'utilisateur:\n{str(e)}")
            print(f"[AdminManager] ERREUR ajout utilisateur: {e}")

    @Slot(int)
    def edit_user(self, row_index: int):
        if row_index < 0 or row_index >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un utilisateur à modifier.")
            return

        try:
            row = self.model.get_user(row_index)
            if not row:
                return

            modal = self._create_user_form(row)

            def on_save():
                if not self._validate_user_form(modal, is_edit=True, exclude_id=row.id):
                    return

                role = self.user_repo.get_role_by_name(modal.role_combo.currentText())
                fields = {
                    "username": modal.username_input.text().strip(),
                    "full_name": modal.name_input.text().strip(),
                    "email": modal.email_input.text().strip() or None,
                    "role_id": role["id"] if role else None,
                    "is_active": 1 if modal.active_checkbox.isChecked() else 0,
                }

                password = modal.password_input.text().strip()
                if password:
                    fields["password_hash"] = self.auth_manager.hash_password(password)

                self.user_repo.update_user(row.id, **fields)
                self.user_repo.log_audit(row.id, "UPDATE", "users", row.id,
                                         description=f"Modification de l'utilisateur {row.username}")

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"L'utilisateur '{fields['full_name']}' a été modifié avec succès.")
                print(f"[AdminManager] Utilisateur modifié: ID {row.id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de la modification:\n{str(e)}")
            print(f"[AdminManager] ERREUR modification utilisateur: {e}")

    @Slot(int)
    def delete_user(self, row_index: int):
        """Désactive l'utilisateur (pas de suppression physique, voir schéma FK)."""
        if row_index < 0 or row_index >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un utilisateur à désactiver.")
            return

        try:
            row = self.model.get_user(row_index)
            if not row:
                return

            reply = QMessageBox.question(
                self.view, "Confirmer la désactivation",
                f"Désactiver le compte de '{row.name}' ?\n\n"
                "Le compte ne sera pas supprimé (pour préserver l'historique "
                "des ventes et l'audit), mais il ne pourra plus se connecter.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.user_repo.set_active(row.id, False)
                self.user_repo.log_audit(row.id, "DEACTIVATE", "users", row.id,
                                         description=f"Compte {row.username} désactivé")
                self.refresh()
                QMessageBox.information(self.view, "Succès",
                    f"Le compte de '{row.name}' a été désactivé.")
                print(f"[AdminManager] Utilisateur désactivé: ID {row.id}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de la désactivation:\n{str(e)}")
            print(f"[AdminManager] ERREUR désactivation utilisateur: {e}")

    @Slot()
    def refresh(self):
        self.rows = self._load_users_from_db()
        self.model.set_users(self.rows)
        print("[AdminManager] Vue rafraîchie depuis la BDD")



    @Slot(int)
    def reset_password(self, row_index: int):
        if row_index < 0 or row_index >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un utilisateur.")
            return

        row = self.model.get_user(row_index)
        if not row:
            return

        from PySide6.QtWidgets import QInputDialog, QLineEdit as QLE
        new_password, ok = QInputDialog.getText(
            self.view, "Réinitialiser le mot de passe",
            f"Nouveau mot de passe pour '{row.name}' :",
            QLE.Password
        )
        if not ok or not new_password.strip():
            return

        success = self.auth_manager.admin_reset_password(
            self.current_user, row.username, new_password.strip()
        )

        if success:
            QMessageBox.information(self.view, "Succès",
                f"Mot de passe réinitialisé pour '{row.name}'.\n"
                "Le compte a également été débloqué s'il était verrouillé.")
            print(f"[AdminManager] Mot de passe réinitialisé pour {row.username}")
        else:
            QMessageBox.critical(self.view, "Erreur", self.auth_manager.last_error)