"""
Accès aux données propres à la synchronisation bidirectionnelle :
curseurs de synchro par table, et requêtes génériques (par sync_uuid,
par updated_at) qui s'appliquent à n'importe quelle table synchronisée.

Les écritures locales elles-mêmes (create_product, update_supplier, etc.)
restent la responsabilité de CatalogRepository / UserRepository — ce
repository ne fait que "brancher" la couche sync par-dessus.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class CloudSyncRepository:

    def __init__(self):
        self.db = get_db_connection()

    # ── Curseurs (un par table synchronisée) ───────────────────────

    def get_state(self, table: str) -> Dict[str, Any]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM sync_state WHERE table_name = ?", (table,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        cursor.execute(
            "INSERT INTO sync_state (table_name, last_pushed_at, last_pulled_at) VALUES (?, NULL, NULL)",
            (table,)
        )
        self.db.commit()
        return {"table_name": table, "last_pushed_at": None, "last_pulled_at": None}

    def set_pushed(self, table: str, when_iso: str = None):
        when_iso = when_iso or datetime.now().isoformat()
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE sync_state SET last_pushed_at = ? WHERE table_name = ?", (when_iso, table)
        )
        self.db.commit()

    def set_pulled(self, table: str, when_iso: str = None):
        when_iso = when_iso or datetime.now().isoformat()
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE sync_state SET last_pulled_at = ? WHERE table_name = ?", (when_iso, table)
        )
        self.db.commit()

    # ── Requêtes génériques (tables mutables, LWW) ─────────────────

    def fetch_local_updated_since(self, table: str, since_iso: Optional[str]) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        if since_iso:
            cursor.execute(
                f"SELECT * FROM {table} WHERE updated_at > ? ORDER BY updated_at ASC", (since_iso,)
            )
        else:
            cursor.execute(f"SELECT * FROM {table} ORDER BY updated_at ASC")
        return [dict(row) for row in cursor.fetchall()]

    # ── Requêtes génériques (tables événementielles, append-only) ─

    def fetch_local_new_since(self, table: str, since_iso: Optional[str]) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        if since_iso:
            cursor.execute(
                f"SELECT * FROM {table} WHERE created_at > ? ORDER BY created_at ASC", (since_iso,)
            )
        else:
            cursor.execute(f"SELECT * FROM {table} ORDER BY created_at ASC")
        return [dict(row) for row in cursor.fetchall()]

    # ── Résolution d'identifiants (local <-> sync_uuid) ────────────

    def find_local_id_by_uuid(self, table: str, sync_uuid: str) -> Optional[int]:
        if not sync_uuid:
            return None
        cursor = self.db.get_cursor()
        cursor.execute(f"SELECT id FROM {table} WHERE sync_uuid = ?", (sync_uuid,))
        row = cursor.fetchone()
        return row["id"] if row else None

    def find_uuid_by_local_id(self, table: str, local_id: int) -> Optional[str]:
        if local_id is None:
            return None
        cursor = self.db.get_cursor()
        cursor.execute(f"SELECT sync_uuid FROM {table} WHERE id = ?", (local_id,))
        row = cursor.fetchone()
        return row["sync_uuid"] if row else None

    def stamp_sync_uuid(self, table: str, local_id: int, sync_uuid: str, updated_at_iso: str = None):
        """Après une création locale issue d'une ligne distante : fige le sync_uuid
        et l'updated_at reçu, pour ne pas re-pousser immédiatement cette ligne."""
        cursor = self.db.get_cursor()
        if updated_at_iso:
            cursor.execute(
                f"UPDATE {table} SET sync_uuid = ?, updated_at = ? WHERE id = ?",
                (sync_uuid, updated_at_iso, local_id)
            )
        else:
            cursor.execute(f"UPDATE {table} SET sync_uuid = ? WHERE id = ?", (sync_uuid, local_id))
        self.db.commit()