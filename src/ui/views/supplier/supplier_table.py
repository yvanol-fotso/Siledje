"""
Tableau fournisseurs — ThemedTable.
"""

from PySide6.QtWidgets import QHeaderView
from src.ui.widgets.themed_table import ThemedTable


class SupplierTable(ThemedTable):
    # La colonne ID reste dans les données (COLUMNS) mais elle est masquée
    # a l'affichage juste apres l'init (voir _init_ui ci-dessous) : elle
    # ne sert a rien pour l'utilisateur, la selection se fait deja par ligne.
    COLUMNS = ["ID", "Nom", "Contact", "Telephone", "Email", "Ville", "Actif"]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="supplierTable",
            row_height=40,
        )
        self._suppliers: list = []

        # Colonne ID masquee : plus besoin de largeur pour elle, on peut
        # redistribuer l'espace sur les colonnes utiles.
        self.setColumnHidden(0, True)

        self.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,  # ID (masquee)
            1: QHeaderView.Stretch,           # Nom
            2: QHeaderView.Stretch,           # Contact
            3: QHeaderView.ResizeToContents,  # Telephone
            4: QHeaderView.Stretch,           # Email
            5: QHeaderView.ResizeToContents,  # Ville
            6: QHeaderView.ResizeToContents,  # Actif
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