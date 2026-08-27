"""Tableaux point de vente — ThemedTable + viewport forcé."""

from PySide6.QtWidgets import QHeaderView
from PySide6.QtGui import QPalette, QColor

from src.ui.widgets.themed_table import ThemedTable
from src.ui.views.base.base_view import Palette


class SalesProductsTable(ThemedTable):
    # La colonne Code-barres reste dans les donnees (COLUMNS) mais elle est
    # masquee a l'affichage juste apres l'init (voir __init__ ci-dessous) :
    # le code-barres n'est pas encore utilise, la selection se fait par ligne.
    COLUMNS = ["SKU", "Code-barres", "Nom", "Type", "Prix", "Stock"]
    TYPE_LABELS = {"unitaire": "UNT", "paquet": "PQT", "carton": "CRT"}

    def __init__(self, parent=None):
        super().__init__(self.COLUMNS, parent=parent, object_name="salesProductsTable")
        self._products_data = []
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Colonne Code-barres masquee : non utilisee pour le moment.
        self.setColumnHidden(1, True)

    def update_products(self, products: list):
        self._products_data = products or []
        if not self._products_data:
            self.set_empty_message("Aucun produit trouve")
            return
        rows = [
            {
                "SKU": p.get("sku", ""),
                "Code-barres": p.get("barcode_test", ""),
                "Nom": p.get("name", ""),
                "Type": self.TYPE_LABELS.get(p.get("type", ""), p.get("type", "")),
                "Prix": f"{p.get('price', 0):.0f} FCFA",
                "Stock": str(p.get("stock", 0)),
            }
            for p in self._products_data
        ]
        self.set_rows(rows)

    def get_selected_product_id(self):
        row = self.currentRow()
        if 0 <= row < len(self._products_data):
            return self._products_data[row].get("id")
        return None


class SalesCartTable(ThemedTable):
    # Meme principe : colonne Code gardee en donnees, masquee a l'affichage.
    COLUMNS = ["SKU", "Code", "Nom", "Type", "Qte", "Sous-total"]

    def __init__(self, parent=None):
        super().__init__(self.COLUMNS, parent=parent, object_name="salesCartTable")
        self._cart_data = []
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Colonne Code masquee : non utilisee pour le moment.
        self.setColumnHidden(1, True)

    def update_cart(self, cart_items: list):
        self._cart_data = cart_items or []
        if not self._cart_data:
            self.set_empty_message("Panier vide")
            return
        rows = []
        for item in self._cart_data:
            product = item["product"]
            subtotal = product["price"] * item["quantity"]
            rows.append({
                "SKU": product.get("sku", ""),
                "Code": product.get("barcode_test", ""),
                "Nom": product.get("name", ""),
                "Type": item.get("type_display", ""),
                "Qte": str(item["quantity"]),
                "Sous-total": f"{subtotal:.0f} FCFA",
            })
        self.set_rows(rows)

    def get_selected_product_id(self):
        row = self.currentRow()
        if 0 <= row < len(self._cart_data):
            return self._cart_data[row]["product"].get("id")
        return None