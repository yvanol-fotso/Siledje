"""
Tableau codes-barres — basé sur ThemedTable.
"""

from PySide6.QtWidgets import QHeaderView
from src.ui.widgets.themed_table import ThemedTable


class BarcodeProductsTable(ThemedTable):
    COLUMNS = [
        "ID", "Code-Barres", "Nom", "Categorie", "Prix", "Stock", "Interne",
    ]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="barcodeTable",
            row_height=38,
        )
        self.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,
            1: QHeaderView.ResizeToContents,
            2: QHeaderView.Stretch,
            3: QHeaderView.Interactive,
            4: QHeaderView.ResizeToContents,
            5: QHeaderView.ResizeToContents,
            6: QHeaderView.ResizeToContents,
        })

    def set_products(self, products: list):
        if not products:
            self.set_empty_message("Aucun produit")
            return
        rows = []
        for p in products:
            rows.append({
                "ID": str(p.get("id", "")),
                "Code-Barres": p.get("barcode", ""),
                "Nom": p.get("name", ""),
                "Categorie": p.get("category", ""),
                "Prix": f"{float(p.get('price', 0)):.2f}",
                "Stock": str(p.get("stock", 0)),
                "Interne": "Oui" if p.get("is_internal_barcode") else "Non",
            })
        self.set_rows(rows)

    def get_selected_product_id(self) -> int | None:
        row = self.currentRow()
        if row < 0:
            return None
        item = self.item(row, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None