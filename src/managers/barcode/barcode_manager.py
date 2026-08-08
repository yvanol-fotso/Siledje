"""
Manager des codes-barres — CatalogRepository (products + barcodes).
Messages : InfoDialog uniquement.
"""

from PySide6.QtCore import QObject, Slot

import barcode as barcode_lib
from barcode.writer import ImageWriter

from src.database.repositories.catalog_repository import CatalogRepository
from src.utils.config import get_config
from src.ui.widgets.InfoDialog import InfoDialog


class BarcodeManager(QObject):

    version = "4.1"

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user
        self.catalog = CatalogRepository()

        config = get_config()
        self.barcodes_dir = config.base_dir / "barcodes"
        self.barcodes_dir.mkdir(exist_ok=True)

        self.current_barcode_for_print = None
        self.current_product_name_for_print = None

        print(f"[BarcodeManager v{self.version}] Initialisé")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.barcode.barcode_view import BarcodeView

            self.view = BarcodeView(self.parent)
            self._connect_view_signals()
            self.load_products()
            print("[BarcodeManager] Vue créée et initialisée")
        return self.view

    def _connect_view_signals(self):
        self.view.search_barcode_requested.connect(self.on_search_barcode)
        self.view.scan_barcode_requested.connect(self.on_scan_barcode)
        self.view.save_product_requested.connect(self.on_save_product)
        self.view.generate_internal_barcode_requested.connect(
            self.on_generate_internal_barcode
        )
        self.view.print_barcode_requested.connect(self.on_print_barcode)
        self.view.refresh_products_requested.connect(self.load_products)
        self.view.edit_product_requested.connect(self.on_edit_product)
        self.view.delete_product_requested.connect(self.on_delete_product)

    # ========== SLOTS ==========

    @Slot(str)
    def on_search_barcode(self, barcode_text: str):
        if not barcode_text:
            self.view.set_status_message(
                "Veuillez entrer un code-barres.", is_error=True
            )
            return

        product = self.catalog.get_product_by_barcode(barcode_text)
        if product:
            self.view.update_product_form({
                "id": product["id"],
                "barcode": barcode_text,
                "name": product["name"],
                "category": product.get("category_name") or "Divers",
                "price": product["sell_price"],
                "stock": product["stock_quantity"],
            })
        else:
            self.view.update_product_form({
                "id": "",
                "barcode": barcode_text,
                "name": "",
                "category": "Divers",
                "price": "0",
                "stock": "0",
            })
        print(
            f"[BarcodeManager] Recherche: {barcode_text} - "
            f"{'Trouve' if product else 'Non trouve'}"
        )

    @Slot()
    def on_scan_barcode(self):
        import random

        simulated = f"{random.randint(1000000000000, 9999999999999)}"
        self.on_search_barcode(simulated)

    @Slot(dict)
    def on_save_product(self, data: dict):
        barcode_val = data.get("barcode", "").strip()
        name = data.get("name", "").strip()
        category_name = data.get("category", "Divers")

        if not barcode_val:
            InfoDialog.warning(
                self.view, "Erreur", "Le code-barres est obligatoire."
            )
            return
        if not name:
            InfoDialog.warning(
                self.view, "Erreur", "Le nom du produit est obligatoire."
            )
            return

        try:
            price = float(data.get("price", "0") or "0")
            stock = int(data.get("stock", "0") or "0")
        except ValueError:
            InfoDialog.warning(self.view, "Erreur", "Prix et stock invalides.")
            return

        category = self.catalog.get_category_by_name(category_name)
        category_id = category["id"] if category else None
        product_id = data.get("id", "").strip()
        user_id = self.current_user.id if self.current_user else None

        if product_id:
            self.catalog.update_product(
                int(product_id),
                name=name,
                category_id=category_id,
                sell_price=price,
            )
            InfoDialog.success(
                self.view, "Succes", f"Produit '{name}' mis a jour."
            )
        else:
            new_id = self.catalog.create_product(
                name=name,
                category_id=category_id,
                sell_price=price,
                stock_quantity=0,
            )
            if stock > 0:
                self.catalog.adjust_stock(
                    new_id, stock, "entry",
                    user_id=user_id, reason="Stock initial",
                )
            if not self.catalog.barcode_exists(barcode_val):
                self.catalog.add_barcode(
                    barcode_val, new_id, "internal", is_primary=True
                )

            sku = self.catalog.generate_sku(new_id, category_name)
            self.catalog.update_product(new_id, sku=sku)

            InfoDialog.success(
                self.view, "Succes", f"Produit '{name}' ajoute."
            )

        self.view.clear_product_form()
        self.load_products()

    @Slot(dict)
    def on_generate_internal_barcode(self, data: dict):
        name = data.get("name", "").strip()
        if not name:
            InfoDialog.warning(
                self.view, "Erreur", "Veuillez entrer un nom de produit."
            )
            return

        try:
            price = float(data.get("price", "0") or "0")
            stock = int(data.get("stock", "0") or "0")
        except ValueError:
            InfoDialog.warning(self.view, "Erreur", "Prix et stock invalides.")
            return

        category_name = data.get("category", "Divers")
        category = self.catalog.get_category_by_name(category_name)
        category_id = category["id"] if category else None
        user_id = self.current_user.id if self.current_user else None

        new_id = self.catalog.create_product(
            name=name,
            category_id=category_id,
            sell_price=price,
            stock_quantity=0,
        )
        if stock > 0:
            self.catalog.adjust_stock(
                new_id, stock, "entry",
                user_id=user_id, reason="Stock initial",
            )

        new_barcode = self.catalog.generate_internal_barcode(new_id)
        self.catalog.add_barcode(
            new_barcode, new_id, "internal", is_primary=True
        )

        sku = self.catalog.generate_sku(new_id, category_name)
        self.catalog.update_product(new_id, sku=sku)

        try:
            ean = barcode_lib.get(
                "code128", new_barcode, writer=ImageWriter()
            )
            filename = self.barcodes_dir / new_barcode
            ean.save(str(filename))
            image_path = str(filename) + ".png"

            self.view.update_barcode_preview(new_barcode, image_path)
            self.current_barcode_for_print = new_barcode
            self.current_product_name_for_print = name
            self.load_products()
            print(
                f"[BarcodeManager] Code genere: {new_barcode} (SKU: {sku})"
            )
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur", f"Erreur generation: {e}"
            )

    @Slot()
    def on_print_barcode(self):
        if self.current_barcode_for_print:
            InfoDialog.info(
                self.view,
                "Impression",
                f"Nom: {self.current_product_name_for_print}\n"
                f"Code: {self.current_barcode_for_print}\n"
                f"Verifiez le dossier 'barcodes'",
            )
        else:
            InfoDialog.warning(
                self.view, "Erreur", "Aucun code-barres a imprimer."
            )

    @Slot(int)
    def on_edit_product(self, product_id: int):
        product = self.catalog.get_product_by_id(product_id)
        if not product:
            InfoDialog.error(self.view, "Erreur", "Produit introuvable.")
            return
        InfoDialog.info(
            self.view,
            "Edition",
            f"Utilisez le module 'Gestion de Stock' pour modifier tous les "
            f"details de '{product['name']}'. "
            f"Cet ecran gere uniquement les codes-barres.",
        )

    @Slot(int)
    def on_delete_product(self, product_id: int):
        product = self.catalog.get_product_by_id(product_id)
        if not product:
            InfoDialog.error(self.view, "Erreur", "Produit introuvable.")
            return

        ok = InfoDialog.question(
            self.view,
            "Confirmation",
            f"Desactiver '{product['name']}' ?",
            ok_text="Yes",
            cancel_text="No",
        )
        if not ok:
            return

        self.catalog.set_product_active(product_id, False)
        InfoDialog.success(self.view, "Succes", "Produit desactive.")
        self.load_products()

    def load_products(self):
        products = self.catalog.get_all_products()
        products_list = []
        for p in products:
            barcodes = self.catalog.get_barcodes_for_product(p["id"])
            primary = next(
                (b["barcode_text"] for b in barcodes if b["is_primary"]),
                barcodes[0]["barcode_text"] if barcodes else "",
            )
            products_list.append({
                "id": p["id"],
                "barcode": primary,
                "name": p["name"],
                "category": p.get("category_name") or "",
                "price": p["sell_price"],
                "stock": p["stock_quantity"],
                "is_internal_barcode": 1 if primary.startswith("LIB") else 0,
            })
        if self.view:
            self.view.update_products_table(products_list)
        print(f"[BarcodeManager] {len(products_list)} produits charges")

    def refresh(self):
        self.load_products()

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(
                f"[BarcodeManager] Theme applique: "
                f"{'dark' if is_dark else 'light'}"
            )