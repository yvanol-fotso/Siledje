"""
Manager des ventes — connecté à SalesRepository + CatalogRepository.
Panier en mémoire, checkout réel avec sale_items/sale_payments et
déduction de stock tracée dans stock_movements.

v2.2 — ThemedTable (via SalesView) + InfoDialog (plus de QMessageBox),
modals via ModalForm + SalesPaymentForm / InvoiceViewer (sales_forms.py),
meme pattern que StockManager.
"""

from PySide6.QtCore import QObject, Slot

from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.sales_repository import SalesRepository

from src.ui.views.sales.sales_view import SalesView
from src.ui.views.sales.sales_form import SalesPaymentForm, InvoiceViewer, build_invoice_html
from src.ui.widgets.modal_form import ModalForm
from src.ui.widgets.InfoDialog import InfoDialog


class SalesManager(QObject):
    """Manager des ventes — vrai schéma, plus de dummy data."""

    version = "2.2"

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user
        self._is_dark = False

        self.catalog = CatalogRepository()
        self.sales_repo = SalesRepository()

        self.current_cart = []
        self.current_search = ""
        self.current_type_filter = None
        self.all_products = []

        print(f"[SalesManager v{self.version}] Initialisé")

    def get_ui(self):
        if self.view is None:
            self.view = SalesView(self.parent)
            self._connect_view_signals()
            self.load_products()
            self.view.set_theme(self._is_dark)
        return self.view

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.load_products)
        self.view.type_filter_changed.connect(self.on_type_filter_changed)
        self.view.add_to_cart_requested.connect(self.add_to_cart)
        self.view.remove_from_cart_requested.connect(self.remove_from_cart)
        self.view.clear_cart_requested.connect(self.clear_cart)
        self.view.checkout_requested.connect(self.process_sale)

    # ──────────────────────────────────────────────────────────────
    # CHARGEMENT & FILTRAGE
    # ──────────────────────────────────────────────────────────────

    @Slot()
    def load_products(self):
        """Charge les produits depuis CatalogRepository et applique les filtres."""
        search_term = self.view.get_search_term() if self.view else ""

        if search_term:
            products = self.catalog.search_products(search_term)
        else:
            products = self.catalog.get_all_products()

        type_filter = self.view.get_type_filter() if self.view else None
        if type_filter:
            products = [p for p in products if p.get("packaging_type") == type_filter]

        adapted = []
        for p in products:
            barcodes = self.catalog.get_barcodes_for_product(p["id"])
            primary = next((b["barcode_text"] for b in barcodes if b["is_primary"]),
                           barcodes[0]["barcode_text"] if barcodes else "")
            adapted.append({
                "id": p["id"],
                "sku": p.get("sku") or f"—#{p['id']}",
                "name": p["name"],
                "price": p["sell_price"],
                "stock": p["stock_quantity"],
                "type": p.get("packaging_type", "unitaire"),
                "barcode_test": primary,
            })

        self.all_products = adapted
        self.view.update_products_table(adapted)
        print(f"[SalesManager] {len(adapted)} produits affichés")

    @Slot(str)
    def on_type_filter_changed(self, product_type):
        """Filtre par type de produit changé"""
        self.load_products()

    # ──────────────────────────────────────────────────────────────
    # GESTION DU PANIER
    # ──────────────────────────────────────────────────────────────

    @Slot(int)
    def add_to_cart(self, product_id: int):
        product = next((p for p in self.all_products if p["id"] == product_id), None)
        if not product:
            return

        if product["stock"] <= 0:
            InfoDialog.warning(
                self.view, "Stock épuisé", f"{product['name']} n'est plus en stock."
            )
            return

        existing = next(
            (item for item in self.current_cart if item["product"]["id"] == product_id), None
        )
        if existing:
            if existing["quantity"] + 1 > product["stock"]:
                InfoDialog.warning(
                    self.view, "Stock insuffisant",
                    f"Stock disponible : {product['stock']}",
                )
                return
            existing["quantity"] += 1
        else:
            self.current_cart.append({
                "product": product, "quantity": 1, "type_display": product["type"],
            })

        self.update_cart_display()

    @Slot(int)
    def remove_from_cart(self, product_id: int):
        for item in self.current_cart[:]:
            if item["product"]["id"] == product_id:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                else:
                    self.current_cart.remove(item)
                break
        self.update_cart_display()

    @Slot()
    def clear_cart(self):
        self.current_cart = []
        self.update_cart_display()

    def update_cart_display(self):
        total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        self.view.update_cart_table(self.current_cart, total)

    # ──────────────────────────────────────────────────────────────
    # PROCESSUS DE VENTE COMPLET
    # ──────────────────────────────────────────────────────────────

    @Slot()
    def process_sale(self):
        if not self.current_cart:
            InfoDialog.warning(self.view, "Panier vide", "Aucun article dans le panier.")
            return

        for item in self.current_cart:
            fresh = self.catalog.get_product_by_id(item["product"]["id"])
            if not fresh or item["quantity"] > fresh["stock_quantity"]:
                InfoDialog.error(
                    self.view, "Stock insuffisant",
                    f"Stock insuffisant pour {item['product']['name']}\n"
                    f"Disponible : {fresh['stock_quantity'] if fresh else 0}",
                )
                return

        total = sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        payment_methods = self.sales_repo.get_payment_methods()

        form = SalesPaymentForm(total=total, payment_methods=payment_methods)

        modal = ModalForm(
            title="Finaliser le Paiement",
            parent=self.view,
            width=520, height=480,
            ok_text="Valider le paiement", cancel_text="Annuler",
        )
        modal.set_content(form)

        def on_validate():
            data = form.get_data()
            client_name = data["client_name"]
            client_phone = data["client_phone"]
            payment_label = data["payment_method_name"]
            payment_method_id = data["payment_method_id"]

            client_id = None
            if client_phone:
                client_id = self.sales_repo.get_or_create_client(
                    client_name or "Client", client_phone
                )

            items = [{
                "product_id": item["product"]["id"],
                "quantity": item["quantity"],
                "unit_price": item["product"]["price"],
                "discount": 0,
                "total_price": item["product"]["price"] * item["quantity"],
                "product_name_snap": item["product"]["name"],
            } for item in self.current_cart]

            user_id = self.current_user.id if self.current_user else None

            result = self.sales_repo.create_sale(
                user_id=user_id, items=items, payment_method_id=payment_method_id,
                client_id=client_id, subtotal=total, total_amount=total,
            )

            if not result:
                InfoDialog.error(modal, "Erreur", "Impossible d'enregistrer la vente.")
                return

            for item in self.current_cart:
                self.catalog.adjust_stock(
                    item["product"]["id"], -item["quantity"], "sale",
                    user_id=user_id, reference_id=result["sale_id"],
                    reference_type="sale",
                    reason=f"Vente {result['invoice_number']}",
                )

            cart_snapshot = [
                {"product": dict(item["product"]), "quantity": item["quantity"],
                 "type_display": item["type_display"]}
                for item in self.current_cart
            ]

            modal.accept()
            print(f"[SalesManager] Vente finalisée — {result['invoice_number']} | {total:.0f} FCFA")

            self.clear_cart()
            self.load_products()

            self._show_invoice(
                result["invoice_number"], client_name, client_phone,
                payment_label, total, cart_snapshot,
            )

        modal.ok_clicked.connect(on_validate)
        modal.exec()

    # ──────────────────────────────────────────────────────────────
    # FACTURE
    # ──────────────────────────────────────────────────────────────

    def _show_invoice(self, invoice_number, client_name, client_phone,
                       payment_label, total, cart_snapshot):
        html = build_invoice_html(
            invoice_number, client_name, client_phone,
            payment_label, total, cart_snapshot,
        )
        viewer = InvoiceViewer(invoice_number, html, parent=self.view)
        viewer.exec()

    # ──────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ──────────────────────────────────────────────────────────────

    def refresh(self):
        if self.view:
            self.load_products()
            self.update_cart_display()

    def get_current_state(self) -> dict:
        return {
            "cart": self.current_cart,
            "cart_count": len(self.current_cart),
            "total": sum(item["product"]["price"] * item["quantity"] for item in self.current_cart),
        }

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        self._is_dark = is_dark
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[SalesManager] Theme appliqué: {'dark' if is_dark else 'light'}")