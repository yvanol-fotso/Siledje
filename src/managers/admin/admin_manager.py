"""
Gestionnaire de gestion des utilisateurs.
Connecté à la vraie base de données via UserRepository + AuthManager.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit as QLE

from src.database.repositories.user_repository import UserRepository
from src.ui.views.admin.admin_table import AdminUserRow, AdminTableModel
from src.ui.views.admin.admin_form import AdminUserForm
from src.ui.widgets.ModalView import ModalView


class AdminManager(QObject):
    """Gestionnaire de gestion des utilisateurs — connecté à la BDD réelle."""

    version = "1.1.0"

    def __init__(self, parent=None, auth_manager=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user

        self.auth_manager = auth_manager
        self.user_repo = auth_manager.user_repo if auth_manager else UserRepository()

        self.roles = self._load_role_names()
        self.rows = self._load_users_from_db()
        self.model = AdminTableModel(self.rows)

        print(f"[AdminManager v{self.version}] Initialisé avec {len(self.rows)} utilisateurs")

    def _load_role_names(self):
        roles = self.user_repo.get_all_roles()
        return [r["name"] for r in roles] if roles else ["admin", "gérant", "employé"]

    def _load_users_from_db(self):
        rows = self.user_repo.get_all_users()
        return [AdminUserRow.from_row(r) for r in rows]

    def get_ui(self):
        if self.view is None:
            from src.ui.views.admin.admin_view import AdminView
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

    # ========== RECHERCHE ==========

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

    # ========== AJOUT ==========

    @Slot()
    def add_user(self):
        try:
            form = AdminUserForm(roles=self.roles)
            
            modal = ModalView(
                title="Nouvel utilisateur",
                parent=self.view,
                width=700, height=600,
                ok_text="Enregistrer", cancel_text="Annuler"
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    QMessageBox.warning(self.view, "Validation", msg)
                    return

                data = form.get_data()

                if self.user_repo.username_exists(data['username']):
                    QMessageBox.warning(self.view, "Validation",
                                        f"Le nom d'utilisateur '{data['username']}' est déjà utilisé.")
                    return

                role = self.user_repo.get_role_by_name(data['role'])
                password_hash = self.auth_manager.hash_password(data['password'])

                new_id = self.user_repo.create_user(
                    username=data['username'],
                    password_hash=password_hash,
                    role_id=role["id"] if role else None,
                    full_name=data['full_name'],
                    email=data['email'],
                )
                if not data['is_active']:
                    self.user_repo.set_active(new_id, False)

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"L'utilisateur '{data['full_name']}' a été créé avec succès.")
                print(f"[AdminManager] Utilisateur créé: ID {new_id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de l'ajout de l'utilisateur:\n{str(e)}")
            print(f"[AdminManager] ERREUR ajout utilisateur: {e}")

    # ========== MODIFICATION ==========

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

            form = AdminUserForm(user=row, roles=self.roles)
            
            modal = ModalView(
                title="Modifier l'utilisateur",
                parent=self.view,
                width=700, height=600,
                ok_text="Enregistrer", cancel_text="Annuler"
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    QMessageBox.warning(self.view, "Validation", msg)
                    return

                data = form.get_data()

                if self.user_repo.username_exists(data['username'], exclude_id=row.id):
                    QMessageBox.warning(self.view, "Validation",
                                        f"Le nom d'utilisateur '{data['username']}' est déjà utilisé.")
                    return

                role = self.user_repo.get_role_by_name(data['role'])
                fields = {
                    "username": data['username'],
                    "full_name": data['full_name'],
                    "email": data['email'],
                    "role_id": role["id"] if role else None,
                    "is_active": 1 if data['is_active'] else 0,
                }

                if data['password']:
                    fields["password_hash"] = self.auth_manager.hash_password(data['password'])

                self.user_repo.update_user(row.id, **fields)

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès",
                    f"L'utilisateur '{data['full_name']}' a été modifié avec succès.")
                print(f"[AdminManager] Utilisateur modifié: ID {row.id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de la modification:\n{str(e)}")
            print(f"[AdminManager] ERREUR modification utilisateur: {e}")

    # ========== SUPPRESSION ==========

    @Slot(int)
    def delete_user(self, row_index: int):
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
                self.refresh()
                QMessageBox.information(self.view, "Succès",
                    f"Le compte de '{row.name}' a été désactivé.")
                print(f"[AdminManager] Utilisateur désactivé: ID {row.id}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur",
                f"Erreur lors de la désactivation:\n{str(e)}")
            print(f"[AdminManager] ERREUR désactivation utilisateur: {e}")

    # ========== RÉINITIALISATION MOT DE PASSE ==========

    @Slot(int)
    def reset_password(self, row_index: int):
        if row_index < 0 or row_index >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un utilisateur.")
            return

        row = self.model.get_user(row_index)
        if not row:
            return

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
            QMessageBox.critical(self.view, "Erreur", 
                self.auth_manager.last_error if hasattr(self.auth_manager, 'last_error') else "Erreur inconnue")

    # ========== RAFRAÎCHISSEMENT ==========

    @Slot()
    def refresh(self):
        self.rows = self._load_users_from_db()
        self.model.set_users(self.rows)
        print("[AdminManager] Vue rafraîchie depuis la BDD")

    # ========== THEME ==========

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[AdminManager] Theme appliqué: {'dark' if is_dark else 'light'}")