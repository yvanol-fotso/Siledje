"""
Migration : ajoute le support de la synchronisation cloud bidirectionnelle
(desktop <-> mobile via Supabase) au schéma existant.

Compatible avec MigrationManager (src/database/migrations/migration_manager.py) :
expose upgrade(conn) / downgrade(conn), reçoit la connexion sqlite3 brute
(pas le wrapper DatabaseManager), et est entièrement idempotente — elle peut
être découverte et exécutée automatiquement par run_migrations() sans risque.

Tables concernées :
  LWW (dernière écriture gagne)     : categories, suppliers, products,
                                        barcodes, product_components
  Append-only (fusion additive)      : stock_movements
"""

import uuid
import sqlite3

LWW_TABLES = ["categories", "suppliers", "products", "barcodes", "product_components"]
APPEND_ONLY_TABLES = ["stock_movements"]
ALL_SYNCED_TABLES = LWW_TABLES + APPEND_ONLY_TABLES


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())  # row[1] = 'name' sur curseur brut


def upgrade(conn: sqlite3.Connection):
    """Appelée par MigrationManager.apply_migration()."""
    cursor = conn.cursor()

    for table in ALL_SYNCED_TABLES:
        if not _column_exists(cursor, table, "sync_uuid"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN sync_uuid TEXT")
            print(f"[Migration cloud_sync] Colonne sync_uuid ajoutée à {table}")

        if table in LWW_TABLES and not _column_exists(cursor, table, "updated_at"):
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            )
            print(f"[Migration cloud_sync] Colonne updated_at ajoutée à {table}")

    conn.commit()

    # Backfill des sync_uuid manquants (lignes créées avant la migration)
    for table in ALL_SYNCED_TABLES:
        cursor.execute(f"SELECT id FROM {table} WHERE sync_uuid IS NULL")
        rows = cursor.fetchall()
        for row in rows:
            cursor.execute(
                f"UPDATE {table} SET sync_uuid = ? WHERE id = ?",
                (str(uuid.uuid4()), row[0])
            )
        if rows:
            print(f"[Migration cloud_sync] {len(rows)} sync_uuid générés pour {table}")

    conn.commit()

    for table in ALL_SYNCED_TABLES:
        cursor.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_sync_uuid ON {table}(sync_uuid)"
        )
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_state (
            table_name TEXT PRIMARY KEY,
            last_pushed_at TIMESTAMP,
            last_pulled_at TIMESTAMP
        )
    """)
    conn.commit()

    print("[Migration cloud_sync] Support de la synchronisation cloud prêt.")


def downgrade(conn: sqlite3.Connection):
    """
    Best-effort : supprime la table sync_state. Les colonnes sync_uuid /
    updated_at ajoutées aux tables existantes ne sont PAS retirées (SQLite
    gère mal DROP COLUMN sur les anciennes versions, et les retirer ferait
    perdre des données de production sans bénéfice réel) — les laisser en
    place est inoffensif si la fonctionnalité cloud est simplement désactivée.
    """
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS sync_state")
    conn.commit()
    print("[Migration cloud_sync] sync_state supprimée (colonnes sync_uuid/updated_at conservées).")