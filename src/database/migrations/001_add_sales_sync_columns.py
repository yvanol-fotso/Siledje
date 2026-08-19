"""
Migration : ajoute le support de la synchronisation cloud aux tables de
ventes (sales, sale_items, sale_payments), qui n'étaient pas couvertes
par cloud_sync_migration.py (celle-ci ne traitait que categories,
suppliers, products, barcodes, product_components, stock_movements).

Compatible avec MigrationManager (src/database/migrations/migration_manager.py) :
expose upgrade(conn) / downgrade(conn), reçoit la connexion sqlite3 brute,
et est entièrement idempotente.

Particularité SQLite : ALTER TABLE ... ADD COLUMN ne supporte pas la
contrainte UNIQUE directement (sqlite3.OperationalError: Cannot add a
UNIQUE column). On ajoute donc la colonne sans contrainte, puis on crée
un index UNIQUE séparé — effet identique, syntaxe compatible.

Tables concernées :
  sales          : ajoute sync_uuid
  sale_items     : ajoute sync_uuid ET created_at (absent à l'origine,
                   nécessaire comme curseur de push incrémental) —
                   backfillé depuis la date de la vente parente.
  sale_payments  : ajoute sync_uuid
"""

import uuid
import sqlite3

TABLES_SYNC_UUID_ONLY = ["sales", "sale_payments"]
TABLES_WITH_EXTRA_COLUMNS = {
    "sale_items": ["created_at TIMESTAMP"],
}
ALL_TABLES = TABLES_SYNC_UUID_ONLY + list(TABLES_WITH_EXTRA_COLUMNS.keys())


def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())  # row[1] = 'name'


def upgrade(conn: sqlite3.Connection):
    """Appelée par MigrationManager.apply_migration()."""
    cursor = conn.cursor()

    # 1. Ajouter sync_uuid (sans UNIQUE, contrainte via index séparé ensuite)
    for table in ALL_TABLES:
        if not _column_exists(cursor, table, "sync_uuid"):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN sync_uuid TEXT")
            print(f"[Migration sales_sync] Colonne sync_uuid ajoutée à {table}")

    # 2. Colonnes supplémentaires spécifiques (created_at sur sale_items)
    for table, extra_cols in TABLES_WITH_EXTRA_COLUMNS.items():
        for col_def in extra_cols:
            col_name = col_def.split()[0]
            if not _column_exists(cursor, table, col_name):
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
                print(f"[Migration sales_sync] Colonne {col_name} ajoutée à {table}")

    # 3. Backfill de sale_items.created_at depuis la vente parente
    #    (approximation correcte pour un curseur de tri, cf. cloud_data_sync_manager.py)
    cursor.execute("""
        UPDATE sale_items SET created_at = (
            SELECT s.created_at FROM sales s WHERE s.id = sale_items.sale_id
        ) WHERE created_at IS NULL
    """)

    # 4. Backfill des sync_uuid manquants sur les 3 tables
    for table in ALL_TABLES:
        cursor.execute(f"SELECT id FROM {table} WHERE sync_uuid IS NULL")
        rows = cursor.fetchall()
        for row in rows:
            cursor.execute(
                f"UPDATE {table} SET sync_uuid = ? WHERE id = ?",
                (str(uuid.uuid4()), row[0])
            )
        if rows:
            print(f"[Migration sales_sync] {len(rows)} sync_uuid générés pour {table}")

    # 5. Index UNIQUE (remplace la contrainte UNIQUE refusée par ALTER TABLE)
    for table in ALL_TABLES:
        cursor.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{table}_sync_uuid ON {table}(sync_uuid)"
        )

    conn.commit()
    print("[Migration sales_sync] Support de la synchronisation cloud prêt pour les ventes.")


def downgrade(conn: sqlite3.Connection):
    """
    Best-effort : supprime uniquement les index. Les colonnes sync_uuid /
    created_at ajoutées ne sont PAS retirées (SQLite gère mal DROP COLUMN,
    et ça ferait perdre des données sans bénéfice réel) — les laisser en
    place est inoffensif si la fonctionnalité cloud est désactivée.
    """
    cursor = conn.cursor()
    for table in ALL_TABLES:
        cursor.execute(f"DROP INDEX IF EXISTS idx_{table}_sync_uuid")
    conn.commit()
    print("[Migration sales_sync] Index de synchronisation des ventes supprimés.")