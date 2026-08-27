"""
Tableau utilisateurs admin — ThemedTable + AdminUserRow.
"""

from PySide6.QtWidgets import QHeaderView

from src.ui.widgets.themed_table import ThemedTable


class AdminUserRow:
    def __init__(
        self,
        id,
        username,
        name,
        email,
        role,
        is_active,
        last_login,
    ):
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


class AdminUsersTable(ThemedTable):

    # ID conservé dans les données mais masqué à l'affichage.
    COLUMNS = [
        "ID",
        "Nom d'utilisateur",
        "Nom complet",
        "Email",
        "Role",
        "Statut",
        "Derniere connexion",
    ]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="adminTable",
            row_height=40,
        )

        self._users = []

        # Même comportement que les tables Sales :
        # toutes les colonnes visibles occupent l'espace disponible.
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # ID caché car inutile à afficher.
        self.setColumnHidden(0, True)

    def set_users(self, users: list):
        """users = liste d'AdminUserRow."""

        self._users = list(users or [])

        if not self._users:
            self.set_empty_message("Aucun utilisateur")
            return

        rows = []

        for u in self._users:
            rows.append({
                "ID": str(u.id),
                "Nom d'utilisateur": u.username,
                "Nom complet": u.name,
                "Email": u.email,
                "Role": u.role,
                "Statut": "Actif" if u.is_active else "Inactif",
                "Derniere connexion": u.last_login or "Jamais",
            })

        self.set_rows(rows)

    def get_user(self, row: int) -> AdminUserRow | None:
        if 0 <= row < len(self._users):
            return self._users[row]

        return None

    def get_selected_user(self) -> AdminUserRow | None:
        return self.get_user(self.currentRow())