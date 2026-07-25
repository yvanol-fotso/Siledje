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
from datetime import datetime

LWW_TABLES = ["categories", "suppliers", "products", "barcodes", "product_components"]
APPEND_ONLY_TABLES = ["stock_movements"]
ALL_SYNCED_TABLES = LWW_TABLES + APPEND_ONLY_TABLES


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())  # row[1] = 'name' sur curseur brut


def upgrade(conn: sqlite3.Connection):
    """Appelée par MigrationManager.apply_migration()."""
    cursor = conn.cursor()

    # 1. Ajouter sync_uuid à toutes les tables
    for table in ALL_SYNCED_TABLES:
        if not _column_exists(cursor, table, "sync_uuid"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN sync_uuid TEXT")
            print(f"[Migration cloud_sync] Colonne sync_uuid ajoutée à {table}")

    # 2. Ajouter updated_at aux tables LWW (SANS DEFAULT)
    for table in LWW_TABLES:
        if not _column_exists(cursor, table, "updated_at"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN updated_at TIMESTAMP")
            print(f"[Migration cloud_sync] Colonne updated_at ajoutée à {table}")

    # 3. Backfill des sync_uuid manquants
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

    # 4. Mettre à jour les dates updated_at (TIMESTAMP CURRENT_TIMESTAMP)
    for table in LWW_TABLES:
        cursor.execute(f"SELECT id FROM {table} WHERE updated_at IS NULL")
        rows = cursor.fetchall()
        for row in rows:
            # Utiliser datetime.now() pour avoir une date cohérente
            now = datetime.now().isoformat()
            cursor.execute(
                f"UPDATE {table} SET updated_at = ? WHERE id = ?",
                (now, row[0])
            )
        if rows:
            print(f"[Migration cloud_sync] {len(rows)} dates updated_at définies pour {table}")

    # 5. Créer les index
    for table in ALL_SYNCED_TABLES:
        cursor.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_sync_uuid ON {table}(sync_uuid)"
        )

    # 6. Créer la table sync_state
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_state (
            table_name TEXT PRIMARY KEY,
            last_pushed_at TIMESTAMP,
            last_pulled_at TIMESTAMP
        )
    """)

    # 7. Optionnel : créer un trigger pour maintenir updated_at automatiquement
    for table in LWW_TABLES:
        cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS trg_{table}_update_updated_at 
            AFTER UPDATE ON {table} 
            FOR EACH ROW 
            BEGIN 
                UPDATE {table} SET updated_at = datetime('now') 
                WHERE id = NEW.id AND updated_at IS NULL;
            END
        """)
        print(f"[Migration cloud_sync] Trigger de mise à jour créé pour {table}")

    conn.commit()
    print("[Migration cloud_sync] Support de la synchronisation cloud prêt.")


def downgrade(conn: sqlite3.Connection):
    """
    Best-effort : supprime la table sync_state et les triggers.
    Les colonnes sync_uuid / updated_at ajoutées aux tables existantes ne sont 
    PAS retirées (SQLite gère mal DROP COLUMN sur les anciennes versions, 
    et les retirer ferait perdre des données de production sans bénéfice réel) 
    — les laisser en place est inoffensif si la fonctionnalité cloud est simplement désactivée.
    """
    cursor = conn.cursor()
    
    # Supprimer les triggers
    for table in LWW_TABLES:
        cursor.execute(f"DROP TRIGGER IF EXISTS trg_{table}_update_updated_at")
    
    cursor.execute("DROP TABLE IF EXISTS sync_state")
    
    # Supprimer les index
    for table in ALL_SYNCED_TABLES:
        cursor.execute(f"DROP INDEX IF EXISTS idx_{table}_sync_uuid")
    
    conn.commit()
    print("[Migration cloud_sync] sync_state supprimée, triggers supprimés.")