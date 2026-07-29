"""
Modele de tableau pour les rapports et statistiques.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


class ReportTableModel(QAbstractTableModel):
    """Modele de tableau pour les rapports de ventes."""
    
    HEADERS = ["N° Facture", "Date/Heure", "Client", "Produits", "Quantite", "Total", "Paiement"]
    
    def __init__(self, sales: list = None):
        super().__init__()
        self._sales = sales or []
    
    def rowCount(self, parent=None):
        return len(self._sales)
    
    def columnCount(self, parent=None):
        return len(self.HEADERS)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        sale = self._sales[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            values = [
                sale.get("invoice_id", ""),
                sale.get("date_str", ""),
                sale.get("client", ""),
                sale.get("products_str", ""),
                str(sale.get("quantities", 0)),
                f"{sale.get('total', 0):.0f} FCFA",
                sale.get("payment_method", ""),
            ]
            return values[col]
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        if role == Qt.UserRole:
            return sale
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None
    
    def get_sale(self, row: int) -> dict:
        if 0 <= row < len(self._sales):
            return self._sales[row]
        return None
    
    def set_sales(self, sales: list):
        self.beginResetModel()
        self._sales = sales
        self.endResetModel()
    
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()