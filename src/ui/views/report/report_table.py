"""
Tableau des rapports — basé sur ThemedTable (style unifié).
"""

from PySide6.QtWidgets import QHeaderView
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
        self.set_column_resize_modes({
            0: QHeaderView.ResizeToContents,
            1: QHeaderView.ResizeToContents,
            2: QHeaderView.Interactive,
            3: QHeaderView.Stretch,
            4: QHeaderView.ResizeToContents,
            5: QHeaderView.ResizeToContents,
            6: QHeaderView.ResizeToContents,
        })

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