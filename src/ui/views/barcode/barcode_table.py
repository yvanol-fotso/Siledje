"""
Tableau codes-barres — basé sur ThemedTable.
"""

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from src.ui.widgets.themed_table import ThemedTable


class BarcodeProductsTable(ThemedTable):
    # La colonne ID reste dans les donnees (COLUMNS) mais elle est masquee
    # a l'affichage juste apres l'init (voir __init__ ci-dessous) : elle
    # ne sert a rien pour l'utilisateur, la selection se fait deja par ligne.
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
        # Stretch global sur toutes les colonnes visibles : l'espace est
        # reparti equitablement entre elles au lieu de coller certaines
        # colonnes (Prix, Stock, Interne...) a la largeur exacte de leur
        # contenu pendant qu'une seule (Nom) engloutit tout le reste.
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Colonne ID masquee : non utilisee pour le moment.
        self.setColumnHidden(0, True)

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

        # "Nom" occupe la meme part que les autres colonnes en Stretch ;
        # le centrage herite de ThemedTable ferait flotter le texte au
        # milieu de cet espace. On aligne a gauche pour un rendu plus
        # naturel et compact.
        self._align_column_left("Nom")

    def _align_column_left(self, column_name: str):
        col = self.COLUMNS.index(column_name)
        for row in range(self.rowCount()):
            item = self.item(row, col)
            if item is not None:
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

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