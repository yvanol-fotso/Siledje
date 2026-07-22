"""
Accès aux données système — conforme au schéma SILEDJE.
Couvre : sync_logs, settings.
"""

from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SystemRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT NOT NULL,
                direction TEXT NOT NULL,
                status TEXT NOT NULL,
                records_synced INTEGER DEFAULT 0,
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT,
                value_type TEXT DEFAULT 'string',
                description TEXT,
                category TEXT,
                is_editable INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db.commit()
        self._seed_settings()

    def _seed_settings(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM settings")
        if cursor.fetchone()["c"] > 0:
            return

        defaults = [
            ("shop_name", "SILEDJE Librairie", "string", "Nom de la boutique", "general"),
            ("currency", "FCFA", "string", "Devise principale", "general"),
            ("tax_rate", "0", "float", "Taux TVA par défaut", "general"),
            ("default_low_stock", "10", "integer", "Seuil stock bas par défaut", "general"),
            ("receipt_footer", "Merci de votre visite !", "string", "Pied de ticket", "general"),
            ("cloud_sync_enabled", "0", "boolean", "Sync cloud activée", "sync"),
            ("sync_interval_hours", "24", "integer", "Intervalle de synchro", "sync"),
            ("video_retention_days", "7", "integer", "Durée conservation vidéos", "security"),
            ("ai_detection_enabled", "0", "boolean", "IA surveillance activée", "security"),
            ("ai_confidence_threshold", "0.75", "float", "Seuil de confiance IA", "security"),
            ("barcode_prefix_internal", "LIB", "string", "Préfixe codes-barres internes", "general"),
        ]
        for key, value, vtype, desc, category in defaults:
            cursor.execute("""
                INSERT INTO settings (key, value, value_type, description, category)
                VALUES (?, ?, ?, ?, ?)
            """, (key, value, vtype, desc, category))
        self.db.commit()

    def get(self, key: str, default=None):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT value, value_type FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return default
        value, vtype = row["value"], row["value_type"]
        if vtype == "integer":
            return int(value)
        if vtype == "float":
            return float(value)
        if vtype == "boolean":
            return value == "1"
        return value

    def set(self, key: str, value):
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?
        """, (str(value), key))
        self.db.commit()

    def get_all_settings(self, category: str = None) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        if category:
            cursor.execute("SELECT * FROM settings WHERE category = ? ORDER BY key", (category,))
        else:
            cursor.execute("SELECT * FROM settings ORDER BY category, key")
        return [dict(row) for row in cursor.fetchall()]

    # ── SYNC LOGS ────────────────────────────────────────────────────

    def log_sync_start(self, sync_type: str, direction: str) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO sync_logs (sync_type, direction, status)
            VALUES (?, ?, 'in_progress')
        """, (sync_type, direction))
        self.db.commit()
        return cursor.lastrowid

    def log_sync_finish(self, sync_id: int, status: str, records_synced: int = 0,
                         error_message: str = None):
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE sync_logs SET status = ?, records_synced = ?, error_message = ?,
                                  finished_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, records_synced, error_message, sync_id))
        self.db.commit()