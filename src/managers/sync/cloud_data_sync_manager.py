"""
Synchronisation bidirectionnelle des données métier (desktop <-> mobile,
via Supabase) — distincte du SyncManager de sauvegarde cloud (celui-là
envoie un instantané complet de la base pour la reprise après sinistre ;
celui-ci synchronise chaque enregistrement individuellement, dans les
deux sens, pour que desktop et mobile restent cohérents en continu).

RÈGLES DE FUSION :
  - categories / suppliers / products / barcodes / product_components :
    "dernière écriture gagne" (LWW) via la colonne updated_at.

  - stock_movements : JAMAIS de LWW. Journal d'événements (append-only) :
    chaque mouvement créé sur un appareil est rejoué sur l'autre, en
    s'AJOUTANT au stock existant — jamais en l'écrasant.

IMPORTANT — colonnes envoyées à Supabase :
  Seules les colonnes qui existent réellement côté Supabase sont envoyées.
  `created_at`, `id`, `stock_quantity` et les colonnes purement locales
  (user_id, quantity_before, quantity_after, reference_id, reference_type
  sur stock_movements) ne partent JAMAIS vers le cloud.

PRÉ-REQUIS :
  - Migration exécutée : src.database.migrations.cloud_sync_migration
  - Tables miroir Supabase créées avec les mêmes noms de colonnes que ceux
    utilisés ici (voir to_remote() de chaque adaptateur pour la liste exacte).
  - Horloges des appareils synchronisées (NTP).

Pour ajouter barcodes / product_components, dupliquer le patron de
ProductAdapter avec leurs propres champs et FK.
"""

from datetime import timezone
from dateutil import parser as date_parser
from PySide6.QtCore import QObject, Signal, Slot

from src.database.repositories.cloud_sync_repository import CloudSyncRepository
from src.database.repositories.catalog_repository import CatalogRepository
from src.managers.sync.supabase_rest_client import SupabaseRestClient
from src.managers.sync.network_utils import has_internet_connection


def _parse_ts(raw):
    """Parse un horodatage local (SQLite, naïf, UTC implicite) ou distant
    (Supabase, ISO8601 avec fuseau) et retourne un datetime naïf en UTC,
    comparable de manière fiable — jamais une comparaison de texte brut,
    qui donne des résultats faux dès que les formats diffèrent (ex: 'T'
    contre espace comme séparateur, présence ou non d'un fuseau)."""
    if not raw:
        return None
    dt = date_parser.parse(raw)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# ────────────────────────────────────────────────────────────────────
# ADAPTATEURS — un par table LWW : traduisent local <-> distant
# ────────────────────────────────────────────────────────────────────

class _BaseLWWAdapter:
    table = None
    fk_fields = {}  # {colonne_locale: table_parente} pour traduire id -> sync_uuid
    # Colonnes qui ne partent JAMAIS vers Supabase (id local, created_at local...)
    local_only_fields = {"id", "created_at"}
    # Colonnes envoyées telles quelles (sans FK) — LISTE EXPLICITE pour éviter
    # qu'une colonne locale non prévue côté Supabase ne fasse planter la requête.
    remote_fields = []  # à définir dans chaque sous-classe

    def __init__(self, sync_repo: CloudSyncRepository, catalog: CatalogRepository):
        self.sync_repo = sync_repo
        self.catalog = catalog

    def to_remote(self, local_row: dict) -> dict:
        remote = {"sync_uuid": local_row["sync_uuid"]}
        for field in self.remote_fields:
            if field in self.fk_fields:
                continue  # traité séparément ci-dessous
            remote[field] = local_row.get(field)

        for local_col, parent_table in self.fk_fields.items():
            local_fk_id = local_row.get(local_col)
            remote[local_col] = self.sync_repo.find_uuid_by_local_id(parent_table, local_fk_id) \
                if local_fk_id else None

        remote["updated_at"] = local_row.get("updated_at")
        return remote

    def resolve_fk_to_local(self, remote_row: dict) -> dict:
        """Traduit les FK distantes (sync_uuid) en id locaux pour create_*/update_*."""
        resolved = {}
        for local_col, parent_table in self.fk_fields.items():
            remote_uuid = remote_row.get(local_col)
            resolved[local_col] = self.sync_repo.find_local_id_by_uuid(parent_table, remote_uuid) \
                if remote_uuid else None
        return resolved

    def create_local(self, remote_row: dict) -> int:
        raise NotImplementedError

    def update_local(self, local_id: int, remote_row: dict):
        raise NotImplementedError


class CategoryAdapter(_BaseLWWAdapter):
    table = "categories"
    fk_fields = {"parent_id": "categories"}
    remote_fields = ["name", "description", "icon", "color", "sort_order", "is_active"]

    def create_local(self, remote_row: dict) -> int:
        fk = self.resolve_fk_to_local(remote_row)
        return self.catalog.create_category(
            name=remote_row["name"], parent_id=fk["parent_id"],
            description=remote_row.get("description"), icon=remote_row.get("icon"),
            color=remote_row.get("color"), sort_order=remote_row.get("sort_order", 0),
        )

    def update_local(self, local_id: int, remote_row: dict):
        fk = self.resolve_fk_to_local(remote_row)
        self.catalog.update_category(
            local_id, name=remote_row["name"], parent_id=fk["parent_id"],
            description=remote_row.get("description"), icon=remote_row.get("icon"),
            color=remote_row.get("color"), sort_order=remote_row.get("sort_order", 0),
            is_active=remote_row.get("is_active", 1),
        )


class SupplierAdapter(_BaseLWWAdapter):
    table = "suppliers"
    remote_fields = ["name", "contact_name", "email", "phone", "phone2",
                      "address", "city", "payment_terms", "notes", "is_active"]

    def create_local(self, remote_row: dict) -> int:
        return self.catalog.create_supplier(
            name=remote_row["name"], contact_name=remote_row.get("contact_name"),
            email=remote_row.get("email"), phone=remote_row.get("phone"),
            phone2=remote_row.get("phone2"), address=remote_row.get("address"),
            city=remote_row.get("city"), payment_terms=remote_row.get("payment_terms"),
            notes=remote_row.get("notes"),
        )

    def update_local(self, local_id: int, remote_row: dict):
        self.catalog.update_supplier(
            local_id, name=remote_row["name"], contact_name=remote_row.get("contact_name"),
            email=remote_row.get("email"), phone=remote_row.get("phone"),
            phone2=remote_row.get("phone2"), address=remote_row.get("address"),
            city=remote_row.get("city"), payment_terms=remote_row.get("payment_terms"),
            notes=remote_row.get("notes"), is_active=remote_row.get("is_active", 1),
        )


class ProductAdapter(_BaseLWWAdapter):
    table = "products"
    fk_fields = {"category_id": "categories", "supplier_id": "suppliers"}
    remote_fields = [
        "name", "description", "buy_price", "sell_price", "min_stock_threshold",
        "packaging_type", "units_per_pack", "location", "image_path", "sku",
        "tax_rate", "is_active", "is_book", "notes",
    ]
    # stock_quantity EXCLU volontairement — reconstruit uniquement via
    # StockMovementAdapter (fusion additive), jamais copié tel quel.

    def create_local(self, remote_row: dict) -> int:
        fk = self.resolve_fk_to_local(remote_row)
        return self.catalog.create_product(
            name=remote_row["name"], description=remote_row.get("description"),
            category_id=fk["category_id"], supplier_id=fk["supplier_id"],
            buy_price=remote_row.get("buy_price", 0), sell_price=remote_row.get("sell_price", 0),
            stock_quantity=0,  # jamais depuis le distant
            min_stock_threshold=remote_row.get("min_stock_threshold", 10),
            packaging_type=remote_row.get("packaging_type", "unitaire"),
            units_per_pack=remote_row.get("units_per_pack", 1),
            location=remote_row.get("location"), image_path=remote_row.get("image_path"),
            sku=remote_row.get("sku"), tax_rate=remote_row.get("tax_rate", 0),
            is_book=bool(remote_row.get("is_book")), notes=remote_row.get("notes"),
        )

    def update_local(self, local_id: int, remote_row: dict):
        fk = self.resolve_fk_to_local(remote_row)
        self.catalog.update_product(
            local_id, name=remote_row["name"], description=remote_row.get("description"),
            category_id=fk["category_id"], supplier_id=fk["supplier_id"],
            buy_price=remote_row.get("buy_price", 0), sell_price=remote_row.get("sell_price", 0),
            min_stock_threshold=remote_row.get("min_stock_threshold", 10),
            packaging_type=remote_row.get("packaging_type", "unitaire"),
            units_per_pack=remote_row.get("units_per_pack", 1),
            location=remote_row.get("location"), sku=remote_row.get("sku"),
            tax_rate=remote_row.get("tax_rate", 0), is_book=bool(remote_row.get("is_book")),
            notes=remote_row.get("notes"), is_active=remote_row.get("is_active", 1),
        )


# ────────────────────────────────────────────────────────────────────
# MANAGER
# ────────────────────────────────────────────────────────────────────

class CloudDataSyncManager(QObject):
    """Synchronise categories/suppliers/products (LWW) et stock_movements
    (fusion additive) entre cet appareil et Supabase."""

    version = "1.1.0"

    sync_started = Signal()
    sync_finished = Signal(bool, str)  # succès, message

    LWW_ADAPTERS_ORDER = [CategoryAdapter, SupplierAdapter, ProductAdapter]

    # Colonnes stock_movements réellement présentes côté Supabase
    STOCK_MOVEMENT_REMOTE_FIELDS = [
        "sync_uuid", "product_id", "movement_type", "quantity",
        "reason", "unit_cost", "notes", "created_at",
    ]

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.sync_repo = CloudSyncRepository()
        self.catalog = CatalogRepository()
        self.client = SupabaseRestClient()
        self._adapters = {
            cls.table: cls(self.sync_repo, self.catalog) for cls in self.LWW_ADAPTERS_ORDER
        }
        self._is_syncing = False

    def _has_permission(self) -> bool:
        return bool(self.current_user and self.current_user.has_permission("can_configure_system"))

    def get_status_summary(self) -> dict:
        """État actuel, sans lancer de synchro — pour affichage immédiat à l'ouverture."""
        if not self.client.is_configured():
            return {"configured": False, "last_sync": None}

        timestamps = []
        for table in list(self._adapters.keys()) + ["stock_movements"]:
            state = self.sync_repo.get_state(table)
            for key in ("last_pushed_at", "last_pulled_at"):
                if state.get(key):
                    timestamps.append(state[key])

        return {"configured": True, "last_sync": max(timestamps) if timestamps else None}

    @Slot()
    def sync_now(self):
        if self._is_syncing:
            return
        if not self._has_permission():
            self.sync_finished.emit(False, "Permission refusée.")
            return
        if not self.client.is_configured():
            self.sync_finished.emit(False, "SUPABASE_URL / SUPABASE_API_KEY manquants dans .env.")
            return
        if not has_internet_connection():
            self.sync_finished.emit(False, "Pas de connexion internet — nouvelle tentative au prochain cycle.")
            return

        self._is_syncing = True
        self.sync_started.emit()
        errors = []

        try:
            # Comble les sync_uuid manquants (lignes créées après la migration
            # initiale, ou via un chemin de code qui n'en génère pas encore).
            for table in list(self._adapters.keys()) + ["stock_movements"]:
                self.sync_repo.backfill_missing_uuids(table)

            for table in self._adapters:
                try:
                    self._push_lww_table(table)
                except Exception as e:
                    errors.append(f"push {table} : {e}")

            for table in self._adapters:
                try:
                    self._pull_lww_table(table)
                except Exception as e:
                    errors.append(f"pull {table} : {e}")

            try:
                self._push_stock_movements()
            except Exception as e:
                errors.append(f"push stock_movements : {e}")

            try:
                self._pull_stock_movements()
            except Exception as e:
                errors.append(f"pull stock_movements : {e}")

            if errors:
                self.sync_finished.emit(False, " | ".join(errors))
            else:
                self.sync_finished.emit(True, "Synchronisation réussie.")
        finally:
            self._is_syncing = False

    # ── LWW (categories / suppliers / products) ────────────────────

    def _push_lww_table(self, table: str):
        adapter = self._adapters[table]
        state = self.sync_repo.get_state(table)
        rows = self.sync_repo.fetch_local_updated_since(table, state.get("last_pushed_at"))
        if not rows:
            return

        remote_rows = [adapter.to_remote(r) for r in rows]
        self.client.upsert_rows(table, remote_rows)
        self.sync_repo.set_pushed(table, rows[-1]["updated_at"])

    def _pull_lww_table(self, table: str):
        adapter = self._adapters[table]
        state = self.sync_repo.get_state(table)
        remote_rows = self.client.fetch_updated_since(table, state.get("last_pulled_at"))
        if not remote_rows:
            return

        for remote_row in remote_rows:
            remote_uuid = remote_row["sync_uuid"]
            local_id = self.sync_repo.find_local_id_by_uuid(table, remote_uuid)

            if local_id is None:
                new_id = adapter.create_local(remote_row)
                self.sync_repo.stamp_sync_uuid(table, new_id, remote_uuid, remote_row.get("updated_at"))
            else:
                local_rows = self.sync_repo.fetch_local_updated_since(table, None)
                local_row = next((r for r in local_rows if r["id"] == local_id), None)
                local_updated = _parse_ts(local_row["updated_at"]) if local_row else None
                remote_updated = _parse_ts(remote_row.get("updated_at"))
                if not local_updated or (remote_updated and remote_updated > local_updated):
                    adapter.update_local(local_id, remote_row)
                    self.sync_repo.stamp_sync_uuid(table, local_id, remote_uuid, remote_row.get("updated_at"))

        self.sync_repo.set_pulled(table, remote_rows[-1]["updated_at"])

    # ── Mouvements de stock (append-only, fusion additive) ─────────

    def _push_stock_movements(self):
        table = "stock_movements"
        state = self.sync_repo.get_state(table)
        rows = self.sync_repo.fetch_local_new_since(table, state.get("last_pushed_at"))
        if not rows:
            return

        remote_rows = []
        for r in rows:
            remote_rows.append({
                "sync_uuid": r["sync_uuid"],
                "product_id": self.sync_repo.find_uuid_by_local_id("products", r["product_id"]),
                "movement_type": r["movement_type"],
                "quantity": r["quantity"],
                "reason": r.get("reason"),
                "unit_cost": r.get("unit_cost"),
                "notes": r.get("notes"),
                "created_at": r["created_at"],
            })

        self.client.upsert_rows(table, remote_rows)
        self.sync_repo.set_pushed(table, rows[-1]["created_at"])

    def _pull_stock_movements(self):
        table = "stock_movements"
        state = self.sync_repo.get_state(table)
        remote_rows = self.client.fetch_new_since(table, state.get("last_pulled_at"))
        if not remote_rows:
            return

        for remote_row in remote_rows:
            remote_uuid = remote_row["sync_uuid"]
            if self.sync_repo.find_local_id_by_uuid(table, remote_uuid) is not None:
                continue  # déjà appliqué

            local_product_id = self.sync_repo.find_local_id_by_uuid("products", remote_row["product_id"])
            if not local_product_id:
                continue  # produit pas encore synchronisé ; rattrapé au cycle suivant

            new_id = self.catalog.adjust_stock(
                product_id=local_product_id,
                quantity_change=remote_row["quantity"],
                movement_type=remote_row.get("movement_type", "adjustment"),
                user_id=None,
                reason=remote_row.get("reason"),
                unit_cost=remote_row.get("unit_cost"),
                notes=(remote_row.get("notes") or "") + " (synchronisé depuis un autre appareil)",
            )
            if new_id:
                self.sync_repo.stamp_sync_uuid(table, new_id, remote_uuid)

        self.sync_repo.set_pulled(table, remote_rows[-1]["created_at"])