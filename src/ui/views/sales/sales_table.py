"""
Modele de tableau pour le point de vente.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class SalesTableModel(QAbstractTableModel):
    """Modele de tableau pour les produits en vente"""
    
    HEADERS = ["SKU", "Code-barres", "Nom", "Type", "Prix", "Stock"]
    
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
            type_display = {
                "unitaire": "UNT", "paquet": "PQT", "carton": "CRT",
            }.get(product.get("packaging_type", ""), product.get("packaging_type", ""))
            
            values = [
                product.get("sku", f"#{product['id']}"),
                product.get("barcode_test", ""),
                product["name"],
                type_display,
                f"{product['sell_price']:.0f} FCFA",
                str(product["stock_quantity"]),
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
        """Recupere le produit a la ligne donnee"""
        if 0 <= row < len(self._products):
            return self._products[row]
        return None
    
    def set_products(self, products: list):
        """Met a jour la liste des produits"""
        self.beginResetModel()
        self._products = products
        self.endResetModel()
    
    def refresh(self):
        """Rafraichit le modele"""
        self.beginResetModel()
        self.endResetModel()