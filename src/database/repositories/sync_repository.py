"""
Accès aux données de synchronisation cloud.
Trace chaque tentative de synchro (réussie, échouée, en attente) pour permettre
de rejouer automatiquement les échecs dès que la connexion revient.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SyncRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL DEFAULT 'backup_upload',
                file_path TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_operations(status)"
        )
        self.db.commit()

    # ── Création ────────────────────────────────────────────────────

    def enqueue(self, file_path: str, operation_type: str = "backup_upload") -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO sync_operations (operation_type, file_path, status)
            VALUES (?, ?, 'pending')
        """, (operation_type, file_path))
        self.db.commit()
        return cursor.lastrowid

    # ── Lecture ─────────────────────────────────────────────────────

    def get_pending(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM sync_operations WHERE status = 'pending'
            ORDER BY created_at ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_pending_count(self) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM sync_operations WHERE status = 'pending'")
        return cursor.fetchone()["c"]

    def get_recent(self, limit: int = 30) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM sync_operations ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_last_success(self) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM sync_operations WHERE status = 'success'
            ORDER BY completed_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── Mise à jour ─────────────────────────────────────────────────

    def mark_attempt(self, op_id: int, success: bool, error: str = None):
        cursor = self.db.get_cursor()
        now = datetime.now().isoformat()
        if success:
            cursor.execute("""
                UPDATE sync_operations
                SET status = 'success', attempts = attempts + 1,
                    last_attempt_at = ?, completed_at = ?, last_error = NULL
                WHERE id = ?
            """, (now, now, op_id))
        else:
            cursor.execute("""
                UPDATE sync_operations
                SET status = 'pending', attempts = attempts + 1,
                    last_attempt_at = ?, last_error = ?
                WHERE id = ?
            """, (now, error, op_id))
        self.db.commit()

    def mark_failed_permanently(self, op_id: int, error: str):
        """Après un nombre d'essais trop élevé, on arrête de retenter automatiquement."""
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE sync_operations
            SET status = 'failed', last_attempt_at = ?, last_error = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), error, op_id))
        self.db.commit()