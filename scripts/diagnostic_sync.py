"""Diagnostic : compare l'état local (SQLite) et distant (Supabase) pour products."""
from dotenv import load_dotenv
load_dotenv()

from src.database.connection import get_db_connection
from src.database.repositories.cloud_sync_repository import CloudSyncRepository
from src.managers.sync.supabase_rest_client import SupabaseRestClient

db = get_db_connection()
cur = db.get_cursor()

print("=== sync_state (curseurs) ===")
cur.execute("SELECT * FROM sync_state")
for row in cur.fetchall():
    print(dict(row))

print("\n=== Produits LOCAUX (SQLite) ===")
cur.execute("SELECT id, name, sync_uuid, updated_at FROM products")
for row in cur.fetchall():
    print(dict(row))

print("\n=== Produits DISTANTS (Supabase) ===")
client = SupabaseRestClient()
print("Configuré :", client.is_configured())
remote_rows = client.fetch_updated_since("products", None)
for r in remote_rows:
    print({"sync_uuid": r.get("sync_uuid"), "name": r.get("name"), "updated_at": r.get("updated_at")})