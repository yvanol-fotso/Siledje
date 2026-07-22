"""Accès aux données de licence (table licenses)."""

import sqlite3
from datetime import datetime
from src.database.connection import get_db_connection


class LicenseRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL UNIQUE,
                plan TEXT NOT NULL,
                client_name TEXT,
                client_email TEXT,
                max_users INTEGER DEFAULT 1,
                features_json TEXT,
                is_active INTEGER DEFAULT 1,
                valid_from DATE NOT NULL,
                valid_until DATE,
                last_verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()

    def get_active_license(self):
        """Retourne la dernière licence active enregistrée (il ne devrait y en avoir qu'une)."""
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM licenses WHERE is_active = 1
            ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    def store_license(self, license_key: str, plan: str, client_name: str,
                       max_users: int, valid_from, valid_until) -> int:
        cursor = self.db.get_cursor()
        # Désactive les anciennes licences avant d'enregistrer la nouvelle
        cursor.execute("UPDATE licenses SET is_active = 0")
        cursor.execute("""
            INSERT INTO licenses (license_key, plan, client_name, max_users,
                                   valid_from, valid_until, is_active, last_verified_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
        """, (license_key, plan, client_name, max_users,
              valid_from.isoformat(), valid_until.isoformat() if valid_until else None,
              datetime.now().isoformat()))
        self.db.commit()
        return cursor.lastrowid

    def touch_last_verified(self, license_id: int):
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE licenses SET last_verified_at = ? WHERE id = ?",
            (datetime.now().isoformat(), license_id)
        )
        self.db.commit()