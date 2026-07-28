"""À lancer une seule fois : complète les produits déjà créés qui n'ont pas
encore de SKU ni de code-barres, avec le même générateur que StockManager."""
from src.database.repositories.catalog_repository import CatalogRepository

catalog = CatalogRepository()
products = catalog.get_all_products(active_only=False)

fixed = 0
for p in products:
    changed = False
    if not p.get("sku"):
        sku = catalog.generate_sku(p["id"], p.get("category_name"))
        catalog.update_product(p["id"], sku=sku)
        print(f"  SKU  #{p['id']} {p['name']!r} -> {sku}")
        changed = True

    if not catalog.get_barcodes_for_product(p["id"]):
        barcode_val = catalog.generate_internal_barcode(p["id"])
        catalog.add_barcode(barcode_val, p["id"], "internal", is_primary=True)
        print(f"  CODE #{p['id']} {p['name']!r} -> {barcode_val}")
        changed = True

    if changed:
        fixed += 1

print(f"\n{fixed} produit(s) complété(s) sur {len(products)}.")