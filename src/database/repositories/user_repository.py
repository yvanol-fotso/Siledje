"""Accès aux données utilisateurs / rôles / audit."""

import sqlite3
from datetime import datetime
from src.database.connection import get_db_connection


class UserRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                can_manage_stock INTEGER DEFAULT 0,
                can_manage_users INTEGER DEFAULT 0,
                can_view_reports INTEGER DEFAULT 0,
                can_manage_cameras INTEGER DEFAULT 0,
                can_process_returns INTEGER DEFAULT 0,
                can_manage_suppliers INTEGER DEFAULT 0,
                can_configure_system INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role_id INTEGER REFERENCES roles(id),
                full_name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                pin_code TEXT,
                is_active INTEGER DEFAULT 1,
                last_login_at TIMESTAMP,
                avatar_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db.commit()
        self._seed_default_roles()
        self._seed_default_admin()

    def _seed_default_roles(self):
        cursor = self.db.get_cursor()
        roles = [
            ("admin", "Accès total", 1, 1, 1, 1, 1, 1, 1),
            ("gérant", "Gestion sans configuration système", 1, 0, 1, 1, 1, 1, 0),
            ("employé", "Caisse uniquement", 0, 0, 0, 0, 0, 0, 0),
        ]
        for r in roles:
            cursor.execute("SELECT id FROM roles WHERE name = ?", (r[0],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO roles (name, description, can_manage_stock,
                        can_manage_users, can_view_reports, can_manage_cameras,
                        can_process_returns, can_manage_suppliers, can_configure_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, r)
        self.db.commit()

    def _seed_default_admin(self):
        """Crée un compte admin par défaut si aucun utilisateur n'existe."""
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM users")
        if cursor.fetchone()["c"] > 0:
            return

        import bcrypt
        default_password = "admin123"
        hashed = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()

        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        admin_role_id = cursor.fetchone()["id"]

        cursor.execute("""
            INSERT INTO users (username, password_hash, role_id, full_name, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, ("admin", hashed, admin_role_id, "Administrateur"))
        self.db.commit()

        print("=" * 50)
        print(" Compte admin par défaut créé : admin / admin123")
        print(" À CHANGER immédiatement après la première connexion.")
        print("=" * 50)

    def get_by_username(self, username: str):
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT u.*, r.id as role_id, r.name as role_name,
                   r.can_manage_stock, r.can_manage_users, r.can_view_reports,
                   r.can_manage_cameras, r.can_process_returns,
                   r.can_manage_suppliers, r.can_configure_system
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.username = ?
        """, (username,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_pin(self, pin_code: str):
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT u.*, r.id as role_id, r.name as role_name,
                   r.can_manage_stock, r.can_manage_users, r.can_view_reports,
                   r.can_manage_cameras, r.can_process_returns,
                   r.can_manage_suppliers, r.can_configure_system
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.pin_code = ? AND u.is_active = 1
        """, (pin_code,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_last_login(self, user_id: int):
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id)
        )
        self.db.commit()

    def log_audit(self, user_id, action, table_name, record_id=None, description=""):
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action, table_name, record_id, description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, table_name, record_id, description))
        self.db.commit()

    def create_user(self, username, password_hash, role_id, full_name,
                     email=None, phone=None, pin_code=None) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role_id, full_name, email, phone, pin_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password_hash, role_id, full_name, email, phone, pin_code))
        self.db.commit()
        return cursor.lastrowid


    def get_all_users(self):
        """Retourne tous les utilisateurs avec le nom de leur rôle."""
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT u.*, r.id as role_id, r.name as role_name
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.username
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_all_roles(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM roles ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def get_role_by_name(self, name: str):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM roles WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def username_exists(self, username: str, exclude_id: int = None) -> bool:
        cursor = self.db.get_cursor()
        if exclude_id:
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND id != ?",
                (username, exclude_id)
            )
        else:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def update_user(self, user_id: int, **fields) -> bool:
        """Met à jour dynamiquement les champs fournis."""
        allowed = {'username', 'full_name', 'email', 'phone', 'role_id',
                   'is_active', 'password_hash'}
        updates, values = [], []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                values.append(value)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        cursor = self.db.get_cursor()
        cursor.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values
        )
        self.db.commit()
        return True

    def set_active(self, user_id: int, is_active: bool):
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if is_active else 0, user_id)
        )
        self.db.commit()