"""
Manager roles / permissions — UserRepository + InfoDialog.
"""

from PySide6.QtCore import QObject, Slot

from src.database.repositories.user_repository import UserRepository
from src.ui.views.security.security_form import SecurityRoleForm
from src.ui.widgets.modal_form import ModalForm
from src.ui.widgets.InfoDialog import InfoDialog

SYSTEM_ROLES = {"admin", "gerant", "employe"}


class SecurityManager(QObject):
    version = "3.0.0"

    def __init__(self, parent=None, user_repo=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.user_repo = user_repo if user_repo else UserRepository()
        self.roles = self.user_repo.get_all_roles()
        print(
            f"[SecurityManager v{self.version}] Initialise avec "
            f"{len(self.roles)} roles"
        )

    def get_ui(self):
        if self.view is None:
            from src.ui.views.security.security_view import SecurityView

            self.view = SecurityView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            print("[SecurityManager] Vue creee et initialisee")
        return self.view

    def _initialize_view(self):
        self.view.update_roles(self.roles)

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_role_requested.connect(self.add_role)
        self.view.edit_role_requested.connect(self.edit_role)
        self.view.delete_role_requested.connect(self.delete_role)
        self.view.refresh_requested.connect(self.refresh)

    @Slot(str)
    def on_search_requested(self, search_text: str):
        search_text = search_text.strip().lower()
        all_roles = self.user_repo.get_all_roles()
        if search_text:
            all_roles = [
                r for r in all_roles
                if search_text in r.get("name", "").lower()
            ]
        self.roles = all_roles
        self.view.update_roles(self.roles)
        print(f"[SecurityManager] Recherche: {len(all_roles)} roles")

    @Slot()
    def add_role(self):
        try:
            existing_names = [
                r.get("name") for r in self.user_repo.get_all_roles()
            ]
            form = SecurityRoleForm()
            modal = ModalForm(
                title="Nouveau role",
                parent=self.view,
                width=800,
                height=700,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate(existing_names)
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return
                data = form.get_data()
                self.user_repo.create_role(
                    name=data["name"],
                    description=data["description"],
                    **data["permissions"],
                )
                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"Le role '{data['name']}' a ete cree.",
                )
                print(f"[SecurityManager] Role cree: {data['name']}")

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur", f"Erreur lors de l'ajout:\n{e}"
            )
            print(f"[SecurityManager] ERREUR ajout: {e}")

    @Slot(int)
    def edit_role(self, row: int):
        if row < 0 or row >= len(self.roles):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Selectionnez un role a modifier.",
            )
            return
        role = self.roles[row]
        try:
            existing_names = [
                r.get("name")
                for r in self.user_repo.get_all_roles()
                if r["id"] != role["id"]
            ]
            form = SecurityRoleForm(role)
            modal = ModalForm(
                title="Modifier le role",
                parent=self.view,
                width=800,
                height=700,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate(
                    existing_names, exclude_id=role["id"]
                )
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return
                data = form.get_data()
                name_to_update = (
                    None if role.get("name") in SYSTEM_ROLES else data["name"]
                )
                self.user_repo.update_role(
                    role["id"],
                    name=name_to_update,
                    description=data["description"],
                    **data["permissions"],
                )
                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"Le role '{role['name']}' a ete modifie.",
                )
                print(f"[SecurityManager] Role modifie: ID {role['id']}")

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la modification:\n{e}",
            )
            print(f"[SecurityManager] ERREUR modification: {e}")

    @Slot(int)
    def delete_role(self, row: int):
        if row < 0 or row >= len(self.roles):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Selectionnez un role a supprimer.",
            )
            return
        role = self.roles[row]

        if role.get("name") in SYSTEM_ROLES:
            InfoDialog.warning(
                self.view, "Suppression impossible",
                f"Le role '{role['name']}' est un role systeme "
                "et ne peut pas etre supprime.",
            )
            return

        users_count = self.user_repo.count_users_with_role(role["id"])
        if users_count > 0:
            InfoDialog.warning(
                self.view, "Suppression impossible",
                f"{users_count} utilisateur(s) ont encore ce role.\n"
                "Reassignez-les avant de supprimer.",
            )
            return

        ok = InfoDialog.question(
            self.view,
            "Confirmer la suppression",
            f"Supprimer le role '{role['name']}' ?\n\n"
            "Cette action est irreversible.",
            ok_text="Yes",
            cancel_text="No",
        )
        if not ok:
            return
        try:
            cursor = self.user_repo.db.get_cursor()
            cursor.execute("DELETE FROM roles WHERE id = ?", (role["id"],))
            self.user_repo.db.commit()
            self.refresh()
            InfoDialog.success(
                self.view, "Succes",
                f"Role '{role['name']}' supprime.",
            )
            print(f"[SecurityManager] Role supprime: ID {role['id']}")
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la suppression:\n{e}",
            )

    @Slot()
    def refresh(self):
        self.roles = self.user_repo.get_all_roles()
        if self.view:
            self.view.update_roles(self.roles)
        print(f"[SecurityManager] Rafraichi: {len(self.roles)} roles")

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(
                f"[SecurityManager] Theme: "
                f"{'dark' if is_dark else 'light'}"
            )