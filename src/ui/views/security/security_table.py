"""
Modele de tableau pour la gestion des roles et permissions.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


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


class RoleTableModel(QAbstractTableModel):
    """Modele de tableau pour les roles."""

    HEADERS = ["ID", "Nom du role", "Description", "Permissions actives"]

    def __init__(self, roles: list = None):
        super().__init__()
        self._roles = roles or []

    def rowCount(self, parent=None):
        return len(self._roles)

    def columnCount(self, parent=None):
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
                return r.get("description") or "-"
            elif col == 3:
                active_count = sum(1 for key, _ in AVAILABLE_PERMISSIONS if r.get(key, 0))
                return f"{active_count}/{len(AVAILABLE_PERMISSIONS)} permission(s)"
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        if role == Qt.UserRole:
            return r

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_role(self, row: int) -> dict:
        if 0 <= row < len(self._roles):
            return self._roles[row]
        return None

    def set_roles(self, roles: list):
        self.beginResetModel()
        self._roles = roles
        self.endResetModel()

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()