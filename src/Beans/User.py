"""Bean représentant un utilisateur authentifié (table users + roles)."""

from src.Beans.Role import Role


class User:
    def __init__(self, id, username, full_name, role: Role,
                 email=None, phone=None, is_active=True, last_login_at=None):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.email = email
        self.phone = phone
        self.is_active = bool(is_active)
        self.last_login_at = last_login_at

    @classmethod
    def from_row(cls, row: dict) -> "User":
        return cls(
            id=row["id"],
            username=row["username"],
            full_name=row.get("full_name") or row["username"],
            role=Role.from_row(row),
            email=row.get("email"),
            phone=row.get("phone"),
            is_active=row.get("is_active", 1),
            last_login_at=row.get("last_login_at"),
        )

    def is_admin(self) -> bool:
        return self.role.name.lower() == "admin"

    def has_permission(self, permission_name: str) -> bool:
        """permission_name ex: 'can_manage_stock'"""
        return getattr(self.role, permission_name, False)

    def __repr__(self):
        return f"<User {self.username} ({self.role.name})>"