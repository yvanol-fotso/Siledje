"""
Tableau fournisseurs — ThemedTable.
"""

from PySide6.QtWidgets import QHeaderView
from src.ui.widgets.themed_table import ThemedTable


class SupplierTable(ThemedTable):
    COLUMNS = ["ID", "Nom", "Contact", "Telephone", "Email", "Ville", "Actif"]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="supplierTable",
            row_height=40,
        )
        self._suppliers: list = []
        self.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,
            1: QHeaderView.Stretch,
            2: QHeaderView.Interactive,
            3: QHeaderView.ResizeToContents,
            4: QHeaderView.Stretch,
            5: QHeaderView.ResizeToContents,
            6: QHeaderView.ResizeToContents,
        })

    def set_suppliers(self, suppliers: list):
        self._suppliers = list(suppliers or [])
        if not self._suppliers:
            self.set_empty_message("Aucun fournisseur")
            return
        rows = []
        for s in self._suppliers:
            rows.append({
                "ID": str(s.get("id", "")),
                "Nom": s.get("name", ""),
                "Contact": s.get("contact_name") or "-",
                "Telephone": s.get("phone") or "-",
                "Email": s.get("email") or "-",
                "Ville": s.get("city") or "-",
                "Actif": "Oui" if s.get("is_active", 1) else "Non",
            })
        self.set_rows(rows)

    def get_supplier(self, row: int) -> dict | None:
        if 0 <= row < len(self._suppliers):
            return self._suppliers[row]
        return None

    def get_selected_supplier(self) -> dict | None:
        return self.get_supplier(self.currentRow())