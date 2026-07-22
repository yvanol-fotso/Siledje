"""Bean représentant un rôle et ses permissions."""

class Role:
    def __init__(self, id, name, description="",
                 can_manage_stock=False, can_manage_users=False,
                 can_view_reports=False, can_manage_cameras=False,
                 can_process_returns=False, can_manage_suppliers=False,
                 can_configure_system=False):
        self.id = id
        self.name = name
        self.description = description
        self.can_manage_stock = bool(can_manage_stock)
        self.can_manage_users = bool(can_manage_users)
        self.can_view_reports = bool(can_view_reports)
        self.can_manage_cameras = bool(can_manage_cameras)
        self.can_process_returns = bool(can_process_returns)
        self.can_manage_suppliers = bool(can_manage_suppliers)
        self.can_configure_system = bool(can_configure_system)

    @classmethod
    def from_row(cls, row: dict) -> "Role":
        """Construit un Role à partir d'une ligne jointe users+roles."""
        return cls(
            id=row.get("role_id"),
            name=row.get("role_name") or "inconnu",
            can_manage_stock=row.get("can_manage_stock", 0),
            can_manage_users=row.get("can_manage_users", 0),
            can_view_reports=row.get("can_view_reports", 0),
            can_manage_cameras=row.get("can_manage_cameras", 0),
            can_process_returns=row.get("can_process_returns", 0),
            can_manage_suppliers=row.get("can_manage_suppliers", 0),
            can_configure_system=row.get("can_configure_system", 0),
        )

    def __repr__(self):
        return f"<Role {self.name}>"