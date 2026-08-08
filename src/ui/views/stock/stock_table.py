"""Tableau stock — ThemedTable (comme Accueil / File / Sales)."""

from PySide6.QtWidgets import QHeaderView
from src.ui.widgets.themed_table import ThemedTable


class StockProductsTable(ThemedTable):
    COLUMNS = [
        "ID", "Nom", "Categorie", "Fournisseur",
        "Prix Achat", "Prix Vente", "Stock",
        "Seuil", "SKU", "Actif",
    ]

    def __init__(self, parent=None):
        super().__init__(self.COLUMNS, parent=parent, object_name="stockTable")
        self._products = []
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def set_products(self, products: list):
        self._products = products or []
        if not self._products:
            self.set_empty_message("Aucun produit")
            return
        rows = []
        for p in self._products:
            rows.append({
                "ID": str(p["id"]),
                "Nom": p.get("name", ""),
                "Categorie": p.get("category_name") or "-",
                "Fournisseur": p.get("supplier_name") or "-",
                "Prix Achat": f"{p.get('buy_price', 0):.2f}",
                "Prix Vente": f"{p.get('sell_price', 0):.2f}",
                "Stock": str(p.get("stock_quantity", 0)),
                "Seuil": str(p.get("min_stock_threshold", 0)),
                "SKU": p.get("sku") or "-",
                "Actif": "Oui" if p.get("is_active") else "Non",
            })
        self.set_rows(rows)

    def get_product(self, row: int):
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def get_selected_product(self):
        return self.get_product(self.currentRow())