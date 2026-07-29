"""
Formulaires de creation/modification de produits.
Support complet des modes Light et Dark.
Version simplifiee avec case a cocher "Ceci est un livre".
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QLabel, QTextEdit,
    QCheckBox, QGroupBox, QVBoxLayout
)
from PySide6.QtCore import Qt


class ProductForm(QWidget):
    """
    Formulaire de creation/modification de produit.
    Une case a cocher permet d'activer les champs "livre".
    """
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_edit = product is not None
        self._is_book = bool(product.get("is_book", False)) if product else False
        self._init_ui()
        self._update_book_fields_visibility()
    
    def _init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        input_style = """
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                min-height: 36px;
                background: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #567ba1;
            }
            QTextEdit {
                min-height: 70px;
                max-height: 70px;
            }
        """
        
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        
        def lbl(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # ── CASE À COCHER "Ceci est un livre" ──
        self.is_book_check = QCheckBox("Ceci est un livre (manuel scolaire)")
        self.is_book_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: #567ba1;
                spacing: 8px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #567ba1;
                border-color: #567ba1;
            }
        """)
        self.is_book_check.setChecked(self._is_book)
        self.is_book_check.toggled.connect(self._update_book_fields_visibility)
        
        layout.addRow(QLabel(""), self.is_book_check)
        
        # ── Séparateur ──
        sep = QLabel("")
        sep.setStyleSheet("border-bottom: 1px solid #bdc3c7; margin: 5px 0;")
        layout.addRow(sep)
        
        # ── Champs communs ──
        
        # Nom
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        self.name_input.setPlaceholderText("Nom du produit")
        if self.product:
            self.name_input.setText(self.product.get("name", ""))
        layout.addRow(lbl("Nom *:"), self.name_input)
        
        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setStyleSheet(input_style)
        if self.product:
            self.desc_input.setText(self.product.get("description", ""))
        layout.addRow(lbl("Description:"), self.desc_input)
        
        # Categorie
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(input_style)
        self.category_combo.addItem("- Aucune -", None)
        layout.addRow(lbl("Categorie:"), self.category_combo)
        
        # Fournisseur
        self.supplier_combo = QComboBox()
        self.supplier_combo.setStyleSheet(input_style)
        self.supplier_combo.addItem("- Aucun -", None)
        layout.addRow(lbl("Fournisseur:"), self.supplier_combo)
        
        # Prix
        self.buy_price = QDoubleSpinBox()
        self.buy_price.setStyleSheet(input_style)
        self.buy_price.setRange(0, 9999999)
        self.buy_price.setDecimals(2)
        if self.product:
            self.buy_price.setValue(self.product.get("buy_price", 0))
        layout.addRow(lbl("Prix d'achat *:"), self.buy_price)
        
        self.sell_price = QDoubleSpinBox()
        self.sell_price.setStyleSheet(input_style)
        self.sell_price.setRange(0, 9999999)
        self.sell_price.setDecimals(2)
        if self.product:
            self.sell_price.setValue(self.product.get("sell_price", 0))
        layout.addRow(lbl("Prix de vente *:"), self.sell_price)
        
        # Stock
        self.stock_input = QSpinBox()
        self.stock_input.setStyleSheet(input_style)
        self.stock_input.setRange(0, 999999)
        if self.product:
            self.stock_input.setValue(self.product.get("stock_quantity", 0))
            self.stock_input.setEnabled(False)
            self.stock_input.setToolTip("Utilisez 'Ajuster le stock' pour modifier la quantite")
        layout.addRow(lbl("Stock:"), self.stock_input)
        
        # Seuil
        self.threshold_input = QSpinBox()
        self.threshold_input.setStyleSheet(input_style)
        self.threshold_input.setRange(0, 999999)
        if self.product:
            self.threshold_input.setValue(self.product.get("min_stock_threshold", 10))
        else:
            self.threshold_input.setValue(10)
        layout.addRow(lbl("Seuil d'alerte:"), self.threshold_input)
        
        # Emballage
        self.packaging_combo = QComboBox()
        self.packaging_combo.setStyleSheet(input_style)
        self.packaging_combo.addItems(["unitaire", "paquet", "carton", "lot"])
        if self.product:
            self.packaging_combo.setCurrentText(self.product.get("packaging_type", "unitaire"))
        layout.addRow(lbl("Emballage:"), self.packaging_combo)
        
        # SKU
        self.sku_input = QLineEdit()
        self.sku_input.setStyleSheet(input_style)
        self.sku_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.sku_input.setText(self.product.get("sku", ""))
        layout.addRow(lbl("SKU:"), self.sku_input)
        
        # Code-barres
        self.barcode_input = QLineEdit()
        self.barcode_input.setStyleSheet(input_style)
        self.barcode_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.barcode_input.setText(self.product.get("barcode", ""))
        layout.addRow(lbl("Code-barres:"), self.barcode_input)
        
        # Emplacement
        self.location_input = QLineEdit()
        self.location_input.setStyleSheet(input_style)
        self.location_input.setPlaceholderText("Ex: Etagere A1")
        if self.product:
            self.location_input.setText(self.product.get("location", ""))
        layout.addRow(lbl("Emplacement:"), self.location_input)
        
        # ── CHAMPS LIVRE (caches par defaut) ──
        self.book_group = QGroupBox("Informations du livre")
        self.book_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 16px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 10px;
                color: #9b59b6;
            }
        """)
        
        book_layout = QFormLayout()
        book_layout.setSpacing(12)
        
        book_input_style = """
            QLineEdit, QComboBox {
                font-size: 14px;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                min-height: 36px;
                background: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #9b59b6;
            }
        """
        
        # Matiere
        self.subject_input = QLineEdit()
        self.subject_input.setStyleSheet(book_input_style)
        self.subject_input.setPlaceholderText("Ex: Mathematiques, Francais...")
        if self.product and self._is_book:
            self.subject_input.setText(self.product.get("subject", ""))
        book_layout.addRow(QLabel("Matiere *:"), self.subject_input)
        
        # Editeur
        self.publisher_input = QLineEdit()
        self.publisher_input.setStyleSheet(book_input_style)
        self.publisher_input.setPlaceholderText("Editeur")
        if self.product and self._is_book:
            self.publisher_input.setText(self.product.get("publisher", ""))
        book_layout.addRow(QLabel("Editeur:"), self.publisher_input)
        
        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setStyleSheet(book_input_style)
        self.isbn_input.setPlaceholderText("ISBN")
        if self.product and self._is_book:
            self.isbn_input.setText(self.product.get("isbn", ""))
        book_layout.addRow(QLabel("ISBN:"), self.isbn_input)
        
        # Niveau
        self.level_combo = QComboBox()
        self.level_combo.setStyleSheet(book_input_style)
        book_layout.addRow(QLabel("Niveau *:"), self.level_combo)
        
        # Systeme
        self.system_combo = QComboBox()
        self.system_combo.setStyleSheet(book_input_style)
        book_layout.addRow(QLabel("Systeme *:"), self.system_combo)
        
        # Classe
        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet(book_input_style)
        book_layout.addRow(QLabel("Classe *:"), self.class_combo)
        
        self.book_group.setLayout(book_layout)
        layout.addRow(self.book_group)
        
        # ── Actif ──
        self.active_chk = QCheckBox("Produit actif")
        self.active_chk.setChecked(bool(self.product.get("is_active", 1)) if self.product else True)
        self.active_chk.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #567ba1;
                border-color: #567ba1;
            }
        """)
        layout.addRow(QLabel(""), self.active_chk)
        
        self.setLayout(layout)
    
    def _update_book_fields_visibility(self):
        """Affiche ou cache les champs livre selon la case a cocher."""
        is_book = self.is_book_check.isChecked()
        self.book_group.setVisible(is_book)
        
        # Marquer les champs comme obligatoires
        self.subject_input.setEnabled(is_book)
        self.level_combo.setEnabled(is_book)
        self.system_combo.setEnabled(is_book)
        self.class_combo.setEnabled(is_book)
    
    def set_school_data(self, levels: list, systems: list, classes_data: dict):
        """Definit les donnees scolaires disponibles."""
        self._classes_data = classes_data
        
        # Niveaux
        self.level_combo.clear()
        for level in levels:
            self.level_combo.addItem(level["name"], level["id"])
        
        # Systemes
        self.system_combo.clear()
        for system in systems:
            self.system_combo.addItem(system["name"], system["id"])
        
        # Connecter les signaux
        self.level_combo.currentTextChanged.connect(self._update_classes)
        self.system_combo.currentTextChanged.connect(self._update_classes)
        
        # Remplir les classes si on est en edition
        if self.product and self._is_book:
            self._update_classes()
            # Selectionner la classe du produit
            if self.product.get("class_name"):
                idx = self.class_combo.findText(self.product.get("class_name"))
                if idx >= 0:
                    self.class_combo.setCurrentIndex(idx)
    
    def _update_classes(self):
        """Met a jour la liste des classes selon niveau et systeme."""
        self.class_combo.clear()
        
        level_name = self.level_combo.currentText()
        system_name = self.system_combo.currentText()
        
        if not level_name or not system_name:
            return
        
        for class_item in self._classes_data.get("classes", []):
            if (class_item.get("level_name") == level_name and
                class_item.get("system_name") == system_name):
                self.class_combo.addItem(class_item["name"], class_item["id"])
    
    def get_data(self) -> dict:
        """Recupere les donnees du formulaire."""
        is_book = self.is_book_check.isChecked()
        
        data = {
            'name': self.name_input.text().strip(),
            'description': self.desc_input.toPlainText().strip() or None,
            'category_id': self.category_combo.currentData(),
            'supplier_id': self.supplier_combo.currentData(),
            'buy_price': self.buy_price.value(),
            'sell_price': self.sell_price.value(),
            'stock_quantity': self.stock_input.value(),
            'min_stock_threshold': self.threshold_input.value(),
            'packaging_type': self.packaging_combo.currentText(),
            'sku': self.sku_input.text().strip() or None,
            'barcode': self.barcode_input.text().strip() or None,
            'location': self.location_input.text().strip() or None,
            'is_active': self.active_chk.isChecked(),
            'is_book': is_book,
        }
        
        if is_book:
            data.update({
                'subject': self.subject_input.text().strip(),
                'publisher': self.publisher_input.text().strip() or None,
                'isbn': self.isbn_input.text().strip() or None,
                'level_id': self.level_combo.currentData(),
                'system_id': self.system_combo.currentData(),
                'class_id': self.class_combo.currentData(),
            })
        
        return data
    
    def validate(self) -> tuple:
        """Valide les donnees du formulaire."""
        if not self.name_input.text().strip():
            return False, "Le nom est obligatoire."
        
        if self.buy_price.value() <= 0:
            return False, "Le prix d'achat doit etre superieur a 0."
        
        if self.sell_price.value() <= 0:
            return False, "Le prix de vente doit etre superieur a 0."
        
        # Validation des champs livre si la case est cochee
        if self.is_book_check.isChecked():
            if not self.subject_input.text().strip():
                return False, "La matiere est obligatoire pour un livre."
            if self.class_combo.currentData() is None:
                return False, "Veuillez selectionner une classe valide."
        
        return True, ""