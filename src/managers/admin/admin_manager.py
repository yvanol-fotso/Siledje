"""
Gestionnaire utilisateurs — UserRepository + AuthManager.
Messages : InfoDialog.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QInputDialog, QLineEdit as QLE

from src.database.repositories.user_repository import UserRepository
from src.ui.views.admin.admin_table import AdminUserRow
from src.ui.views.admin.admin_form import AdminUserForm
from src.ui.widgets.ModalView import ModalView
from src.ui.widgets.InfoDialog import InfoDialog


class AdminManager(QObject):
    version = "2.0.0"

    def __init__(self, parent=None, auth_manager=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user
        self.auth_manager = auth_manager
        self.user_repo = (
            auth_manager.user_repo if auth_manager else UserRepository()
        )
        self.roles = self._load_role_names()
        self.rows = self._load_users_from_db()
        print(
            f"[AdminManager v{self.version}] Initialise avec "
            f"{len(self.rows)} utilisateurs"
        )

    def _load_role_names(self):
        roles = self.user_repo.get_all_roles()
        return [r["name"] for r in roles] if roles else [
            "admin", "gerant", "employe"
        ]

    def _load_users_from_db(self):
        rows = self.user_repo.get_all_users()
        return [AdminUserRow.from_row(r) for r in rows]

    def get_ui(self):
        if self.view is None:
            from src.ui.views.admin.admin_view import AdminView

            self.view = AdminView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            print("[AdminManager] Vue creee et initialisee")
        return self.view

    def _initialize_view(self):
        self.view.update_users(self.rows)

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_user_requested.connect(self.add_user)
        self.view.edit_user_requested.connect(self.edit_user)
        self.view.delete_user_requested.connect(self.delete_user)
        self.view.refresh_requested.connect(self.refresh)
        self.view.reset_password_requested.connect(self.reset_password)

    @Slot(str)
    def on_search_requested(self, search_text: str):
        search_text = search_text.strip().lower()
        all_rows = self._load_users_from_db()
        if not search_text:
            filtered = all_rows
        else:
            filtered = [
                r for r in all_rows
                if search_text in r.username.lower()
                or search_text in r.name.lower()
                or search_text in (r.email or "").lower()
            ]
        self.rows = filtered
        self.view.update_users(self.rows)

    @Slot()
    def add_user(self):
        try:
            form = AdminUserForm(roles=self.roles)
            modal = ModalView(
                title="Nouvel utilisateur",
                parent=self.view,
                width=700,
                height=600,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return

                data = form.get_data()
                if self.user_repo.username_exists(data["username"]):
                    InfoDialog.warning(
                        self.view, "Validation",
                        f"Le nom d'utilisateur '{data['username']}' "
                        f"est deja utilise.",
                    )
                    return

                role = self.user_repo.get_role_by_name(data["role"])
                password_hash = self.auth_manager.hash_password(data["password"])
                new_id = self.user_repo.create_user(
                    username=data["username"],
                    password_hash=password_hash,
                    role_id=role["id"] if role else None,
                    full_name=data["full_name"],
                    email=data["email"],
                )
                if not data["is_active"]:
                    self.user_repo.set_active(new_id, False)

                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"L'utilisateur '{data['full_name']}' a ete cree.",
                )
                print(f"[AdminManager] Utilisateur cree: ID {new_id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de l'ajout:\n{e}",
            )
            print(f"[AdminManager] ERREUR ajout: {e}")

    @Slot(int)
    def edit_user(self, row_index: int):
        if row_index < 0 or row_index >= len(self.rows):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Veuillez selectionner un utilisateur a modifier.",
            )
            return
        try:
            row = self.rows[row_index]
            form = AdminUserForm(user=row, roles=self.roles)
            modal = ModalView(
                title="Modifier l'utilisateur",
                parent=self.view,
                width=700,
                height=600,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return

                data = form.get_data()
                if self.user_repo.username_exists(
                    data["username"], exclude_id=row.id
                ):
                    InfoDialog.warning(
                        self.view, "Validation",
                        f"Le nom d'utilisateur '{data['username']}' "
                        f"est deja utilise.",
                    )
                    return

                role = self.user_repo.get_role_by_name(data["role"])
                fields = {
                    "username": data["username"],
                    "full_name": data["full_name"],
                    "email": data["email"],
                    "role_id": role["id"] if role else None,
                    "is_active": 1 if data["is_active"] else 0,
                }
                if data["password"]:
                    fields["password_hash"] = self.auth_manager.hash_password(
                        data["password"]
                    )

                self.user_repo.update_user(row.id, **fields)
                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"L'utilisateur '{data['full_name']}' a ete modifie.",
                )
                print(f"[AdminManager] Utilisateur modifie: ID {row.id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la modification:\n{e}",
            )
            print(f"[AdminManager] ERREUR modification: {e}")

    @Slot(int)
    def delete_user(self, row_index: int):
        if row_index < 0 or row_index >= len(self.rows):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Veuillez selectionner un utilisateur a desactiver.",
            )
            return
        try:
            row = self.rows[row_index]
            ok = InfoDialog.question(
                self.view,
                "Confirmer la desactivation",
                f"Desactiver le compte de '{row.name}' ?\n\n"
                "Le compte ne sera pas supprime (historique / audit), "
                "mais il ne pourra plus se connecter.",
                ok_text="Yes",
                cancel_text="No",
            )
            if not ok:
                return
            self.user_repo.set_active(row.id, False)
            self.refresh()
            InfoDialog.success(
                self.view, "Succes",
                f"Le compte de '{row.name}' a ete desactive.",
            )
            print(f"[AdminManager] Utilisateur desactive: ID {row.id}")
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la desactivation:\n{e}",
            )
            print(f"[AdminManager] ERREUR desactivation: {e}")

    @Slot(int)
    def reset_password(self, row_index: int):
        if row_index < 0 or row_index >= len(self.rows):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Veuillez selectionner un utilisateur.",
            )
            return

        row = self.rows[row_index]
        new_password, ok = QInputDialog.getText(
            self.view,
            "Reinitialiser le mot de passe",
            f"Nouveau mot de passe pour '{row.name}' :",
            QLE.Password,
        )
        if not ok or not new_password.strip():
            return

        success = self.auth_manager.admin_reset_password(
            self.current_user, row.username, new_password.strip()
        )
        if success:
            InfoDialog.success(
                self.view, "Succes",
                f"Mot de passe reinitialise pour '{row.name}'.\n"
                "Le compte a egalement ete debloque s'il etait verrouille.",
            )
            print(
                f"[AdminManager] Mot de passe reinitialise pour {row.username}"
            )
        else:
            err = getattr(self.auth_manager, "last_error", "Erreur inconnue")
            InfoDialog.error(self.view, "Erreur", err)

    @Slot()
    def refresh(self):
        self.rows = self._load_users_from_db()
        if self.view:
            self.view.update_users(self.rows)
        print("[AdminManager] Vue rafraichie depuis la BDD")

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(
                f"[AdminManager] Theme applique: "
                f"{'dark' if is_dark else 'light'}"
            )