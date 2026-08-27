"""
Tableau roles — ThemedTable + liste des permissions.
"""

from PySide6.QtWidgets import QHeaderView

from src.ui.widgets.themed_table import ThemedTable


AVAILABLE_PERMISSIONS = [
    ("can_manage_stock", "Gestion du stock"),
    ("can_manage_users", "Gestion des utilisateurs"),
    ("can_view_reports", "Rapports et statistiques"),
    ("can_manage_cameras", "Videosurveillance"),
    ("can_process_returns", "Traitement des retours"),
    ("can_manage_suppliers", "Gestion des fournisseurs"),
    ("can_configure_system", "Configuration systeme"),
]


class SecurityRolesTable(ThemedTable):

    # ID conservé dans les données mais masqué à l'affichage.
    COLUMNS = [
        "ID",
        "Nom du role",
        "Description",
        "Permissions actives",
    ]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="securityTable",
            row_height=40,
        )

        self._roles: list = []

        # Toutes les colonnes visibles occupent l'espace disponible.
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # Colonne ID masquée : utilisée en interne uniquement.
        self.setColumnHidden(0, True)

    def set_roles(self, roles: list):
        self._roles = list(roles or [])

        if not self._roles:
            self.set_empty_message("Aucun role")
            return

        rows = []
        n = len(AVAILABLE_PERMISSIONS)

        for r in self._roles:
            active = sum(
                1
                for key, _ in AVAILABLE_PERMISSIONS
                if r.get(key, 0)
            )

            rows.append({
                "ID": str(r.get("id", "")),
                "Nom du role": r.get("name", ""),
                "Description": r.get("description") or "-",
                "Permissions actives": f"{active}/{n} permission(s)",
            })

        self.set_rows(rows)

    def get_role(self, row: int) -> dict | None:
        if 0 <= row < len(self._roles):
            return self._roles[row]

        return None

    def get_selected_role(self) -> dict | None:
        return self.get_role(self.currentRow())