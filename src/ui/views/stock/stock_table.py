"""
Modele de tableau pour la gestion du stock.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


class StockTableModel(QAbstractTableModel):
    """Modele de tableau pour les produits"""
    
    HEADERS = [
        "ID", "Nom", "Categorie", "Fournisseur",
        "Prix Achat", "Prix Vente", "Stock",
        "Seuil", "SKU", "Actif"
    ]
    
    def __init__(self, products: list = None):
        super().__init__()
        self._products = products or []
    
    def rowCount(self, parent=None):
        return len(self._products)
    
    def columnCount(self, parent=None):
        return len(self.HEADERS)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        product = self._products[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            values = [
                str(product["id"]),
                product["name"],
                product.get("category_name") or "-",
                product.get("supplier_name") or "-",
                f"{product['buy_price']:.2f}",
                f"{product['sell_price']:.2f}",
                str(product["stock_quantity"]),
                str(product["min_stock_threshold"]),
                product.get("sku") or "-",
                "Oui" if product["is_active"] else "Non",
            ]
            return values[col]
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        if role == Qt.UserRole:
            return product
        
        return None
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None
    
    def get_product(self, row: int) -> dict:
        if 0 <= row < len(self._products):
            return self._products[row]
        return None
    
    def set_products(self, products: list):
        self.beginResetModel()
        self._products = products
        self.endResetModel()
    
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()