"""
Modele de tableau pour la gestion des fournisseurs.
"""

from PySide6.QtCore import QAbstractTableModel, Qt


class SupplierTableModel(QAbstractTableModel):
    """Modele de tableau pour les fournisseurs."""

    HEADERS = ["ID", "Nom", "Contact", "Telephone", "Email", "Ville", "Actif"]

    def __init__(self, suppliers: list = None):
        super().__init__()
        self._suppliers = suppliers or []

    def rowCount(self, parent=None):
        return len(self._suppliers)

    def columnCount(self, parent=None):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        s = self._suppliers[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            values = [
                str(s.get("id", "")),
                s.get("name", ""),
                s.get("contact_name") or "-",
                s.get("phone") or "-",
                s.get("email") or "-",
                s.get("city") or "-",
                "Oui" if s.get("is_active", 1) else "Non",
            ]
            return values[col]
        
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignLeft
        
        if role == Qt.UserRole:
            return s

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_supplier(self, row: int) -> dict:
        if 0 <= row < len(self._suppliers):
            return self._suppliers[row]
        return None

    def set_suppliers(self, suppliers: list):
        self.beginResetModel()
        self._suppliers = suppliers
        self.endResetModel()

    def refresh(self):
        self.beginResetModel()
        self.endResetModel()