"""
Tableau des rapports — basé sur ThemedTable (style unifié).
"""

from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from src.ui.widgets.themed_table import ThemedTable


class ReportResultsTable(ThemedTable):
    COLUMNS = [
        "N° Facture", "Date/Heure", "Client", "Produits",
        "Quantite", "Total", "Paiement",
    ]

    def __init__(self, parent=None):
        super().__init__(
            self.COLUMNS,
            parent=parent,
            object_name="reportTable",
            row_height=38,
        )
        self.setWordWrap(True)

        self.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,
            1: QHeaderView.ResizeToContents,
            2: QHeaderView.ResizeToContents,
            3: QHeaderView.Stretch,
            4: QHeaderView.ResizeToContents,
            5: QHeaderView.ResizeToContents,
            6: QHeaderView.ResizeToContents,
        })

    def showEvent(self, event):
        # Se declenche quand la table devient reellement visible avec sa
        # geometrie DEFINITIVE (apres que la fenetre ait fini son layout).
        # C'est plus fiable que sectionResized ou un QTimer devine : ici
        # on est certain que la largeur de "Produits" (Stretch) est enfin
        # correcte, donc le wrap du texte se calcule sur la bonne largeur
        # au lieu d'une largeur provisoire trop etroite (source de l'espace
        # vertical enorme au demarrage).
        super().showEvent(event)
        self.resizeRowsToContents()

    def resizeEvent(self, event):
        # Couvre aussi les redimensionnements ulterieurs (fenetre
        # maximisee/restauree, etc.) qui changent la largeur de
        # "Produits" et donc le nombre de lignes necessaires au wrap.
        super().resizeEvent(event)
        self.resizeRowsToContents()

    def set_sales(self, sales: list):
        """
        sales = liste de dicts avec clés :
        invoice_id, date_str, client, products_str, quantities, total, payment_method
        """
        if not sales:
            self.set_empty_message("Aucune vente pour cette periode")
            return

        rows = []
        for s in sales:
            total = s.get("total", 0)
            rows.append({
                "N° Facture": s.get("invoice_id", ""),
                "Date/Heure": s.get("date_str", ""),
                "Client": s.get("client", ""),
                "Produits": s.get("products_str", ""),
                "Quantite": str(s.get("quantities", 0)),
                "Total": f"{total:.0f} FCFA",
                "Paiement": s.get("payment_method", ""),
            })
        self.set_rows(rows)
        self._fix_products_column_display()

        # Appel immediat en plus : couvre le cas ou la table est deja
        # visible avec sa largeur definitive (ex: changement de periode).
        # showEvent/resizeEvent prennent le relais pour tous les autres cas
        # (demarrage, redimensionnement de fenetre).
        self.resizeRowsToContents()

    def _fix_products_column_display(self):
        products_col = self.COLUMNS.index("Produits")
        for row in range(self.rowCount()):
            item = self.item(row, products_col)
            if item is not None:
                item.setToolTip("")
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)