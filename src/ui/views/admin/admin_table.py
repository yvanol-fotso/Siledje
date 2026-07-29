"""
Modèle de tableau pour l'administration des utilisateurs.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


class AdminUserRow:
    """Ligne d'affichage pour le tableau admin."""
    
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


class AdminTableModel(QAbstractTableModel):
    """Modèle de table pour les utilisateurs."""

    HEADERS = ["ID", "Nom d'utilisateur", "Nom complet", "Email",
               "Rôle", "Statut", "Dernière connexion"]

    def __init__(self, users: list = None):
        super().__init__()
        self._users = users or []

    def rowCount(self, parent=None):
        return len(self._users)

    def columnCount(self, parent=None):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        user = self._users[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            values = [
                str(user.id),
                user.username,
                user.name,
                user.email,
                user.role,
                "Actif" if user.is_active else "Inactif",
                user.last_login or "Jamais",
            ]
            return values[col]
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        if role == Qt.UserRole:
            return user

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_user(self, row) -> AdminUserRow:
        if 0 <= row < len(self._users):
            return self._users[row]
        return None

    def set_users(self, users: list):
        """Remplace toutes les données et rafraîchit le tableau."""
        self.beginResetModel()
        self._users = users
        self.endResetModel()

    def refresh(self):
        """Rafraîchit le modèle."""
        self.beginResetModel()
        self.endResetModel()