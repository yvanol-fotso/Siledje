"""product_form_dialog.py - Dialogue de formulaire pour produits."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import QDate

class ProductFormDialog(QDialog):
    """Dialogue pour ajouter/modifier un produit."""
    
    def __init__(self, product_data=None, headers=None, parent=None, all_stock_data=None):
        super().__init__(parent)
        self.headers = headers or []
        self.all_stock_data = all_stock_data or []
        self.product_data = product_data or []
        
        self.setWindowTitle("Ajouter un produit" if not product_data else "Modifier un produit")
        self.setMinimumWidth(500)
        
        self.init_ui()
        self.init_data()
    
    def init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Champs dynamiques basés sur les en-têtes
        self.fields = {}
        
        for i, header in enumerate(self.headers):
            if header == "ID":
                continue
                
            if header in ["Quantité", "Seuil d'alerte"]:
                field = QSpinBox()
                field.setRange(0, 10000)
            elif header in ["Prix unitaire", "Total"]:
                field = QDoubleSpinBox()
                field.setRange(0, 1000000)
                field.setDecimals(2)
            elif header == "Date d'ajout":
                field = QDateEdit()
                field.setDate(QDate.currentDate())
                field.setCalendarPopup(True)
            elif header in ["Catégorie", "Fournisseur", "Type d'emballage", "Classe"]:
                field = QComboBox()
                # Remplir avec les valeurs existantes
                self.populate_combo(field, header)
            else:
                field = QLineEdit()
            
            form_layout.addRow(header + ":", field)
            self.fields[header] = field
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def populate_combo(self, combo, header_name):
        """Remplit un QComboBox avec les valeurs existantes."""
        index = self.headers.index(header_name)
        values = set()
        
        for item in self.all_stock_data:
            if item[index]:
                values.add(str(item[index]))
        
        combo.addItem("")
        for value in sorted(values):
            combo.addItem(str(value))
    
    def init_data(self):
        """Initialise les champs avec les données existantes."""
        if not self.product_data:
            return
            
        for i, header in enumerate(self.headers):
            if header in self.fields and i < len(self.product_data):
                field = self.fields[header]
                value = self.product_data[i]
                
                if isinstance(field, QLineEdit):
                    field.setText(str(value))
                elif isinstance(field, QSpinBox):
                    field.setValue(int(value) if value else 0)
                elif isinstance(field, QDoubleSpinBox):
                    field.setValue(float(value) if value else 0.0)
                elif isinstance(field, QDateEdit) and value:
                    date = QDate.fromString(str(value), "yyyy-MM-dd")
                    if date.isValid():
                        field.setDate(date)
                elif isinstance(field, QComboBox):
                    idx = field.findText(str(value))
                    if idx >= 0:
                        field.setCurrentIndex(idx)
    
    def get_product_data(self):
        """Récupère les données du formulaire."""
        result = []
        
        for header in self.headers:
            if header == "ID":
                # Garder l'ID existant ou None pour nouveau produit
                result.append(self.product_data[self.headers.index("ID")] 
                            if self.product_data and "ID" in self.headers else None)
                continue
                
            if header in self.fields:
                field = self.fields[header]
                
                if isinstance(field, QLineEdit):
                    value = field.text()
                elif isinstance(field, QSpinBox):
                    value = field.value()
                elif isinstance(field, QDoubleSpinBox):
                    value = field.value()
                elif isinstance(field, QDateEdit):
                    value = field.date().toString("yyyy-MM-dd")
                elif isinstance(field, QComboBox):
                    value = field.currentText()
                else:
                    value = ""
                
                result.append(value)
        
        return result