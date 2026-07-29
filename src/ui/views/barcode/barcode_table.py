"""
Modèle de tableau pour la gestion des codes-barres.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


class BarcodeTableModel(QAbstractTableModel):
    """Modèle de tableau pour les codes-barres."""

    HEADERS = ["ID", "Code-Barres", "Nom", "Catégorie", "Prix", "Stock", "Interne"]

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
                str(product.get('id', '')),
                product.get('barcode', ''),
                product.get('name', ''),
                product.get('category', ''),
                f"{product.get('price', 0):.2f}",
                str(product.get('stock', 0)),
                "Oui" if product.get('is_internal_barcode', False) else "Non",
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