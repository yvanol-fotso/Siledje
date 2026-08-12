"""
Accès aux données de la file d'attente des rapports de bug.

Suit le même patron que SyncRepository (table sync_operations) : chaque
rapport soumis est mis en file localement (une ligne SQLite, jamais un
fichier JSON à part), avec un compteur de tentatives, puis une purge
automatique des rapports jamais envoyés au-delà d'un certain âge — pas
la peine de les garder indéfiniment si on n'arrive jamais à les envoyer.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from src.database.connection import get_db_connection


class BugReportRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_attempt_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_bug_reports_status ON bug_reports(status)"
        )
        self.db.commit()

    # ── Création ────────────────────────────────────────────────────

    def enqueue(self, data: dict) -> int:
        """Met un rapport en file. `data` est sérialisé tel quel en JSON
        dans la colonne `payload` — c'est la seule trace du rapport,
        rien n'est écrit sur disque en dehors de la base."""
        cursor = self.db.get_cursor()
        cursor.execute(
            "INSERT INTO bug_reports (payload, status) VALUES (?, 'pending')",
            (json.dumps(data, ensure_ascii=False),)
        )
        self.db.commit()
        return cursor.lastrowid

    # ── Lecture ─────────────────────────────────────────────────────

    def get_pending(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT * FROM bug_reports WHERE status = 'pending' ORDER BY created_at ASC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_pending_count(self) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM bug_reports WHERE status = 'pending'")
        return cursor.fetchone()["c"]

    def get_recent(self, limit: int = 30) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT * FROM bug_reports ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # ── Mise à jour ─────────────────────────────────────────────────

    def mark_attempt(self, report_id: int, success: bool, error: str = None):
        cursor = self.db.get_cursor()
        now = datetime.now().isoformat()
        if success:
            cursor.execute("""
                UPDATE bug_reports
                SET status = 'success', attempts = attempts + 1,
                    last_attempt_at = ?, completed_at = ?, last_error = NULL
                WHERE id = ?
            """, (now, now, report_id))
        else:
            cursor.execute("""
                UPDATE bug_reports
                SET status = 'pending', attempts = attempts + 1,
                    last_attempt_at = ?, last_error = ?
                WHERE id = ?
            """, (now, error, report_id))
        self.db.commit()

    # ── Purge ───────────────────────────────────────────────────────

    def purge_expired(self, max_pending_age_days: int = 7,
                       max_success_age_days: int = 30) -> int:
        """
        Supprime :
          - les rapports encore 'pending' plus vieux que `max_pending_age_days`
            (jamais envoyés, on abandonne — pas la peine d'accumuler) ;
          - les rapports 'success' plus vieux que `max_success_age_days`
            (juste pour ne pas faire grossir la table indéfiniment).
        Retourne le nombre de rapports 'pending' abandonnés.
        """
        cursor = self.db.get_cursor()

        pending_cutoff = (datetime.now() - timedelta(days=max_pending_age_days)).isoformat()
        cursor.execute(
            "DELETE FROM bug_reports WHERE status = 'pending' AND created_at < ?",
            (pending_cutoff,)
        )
        removed = cursor.rowcount

        success_cutoff = (datetime.now() - timedelta(days=max_success_age_days)).isoformat()
        cursor.execute(
            "DELETE FROM bug_reports WHERE status = 'success' AND completed_at < ?",
            (success_cutoff,)
        )

        self.db.commit()
        return removed