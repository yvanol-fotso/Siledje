"""
Formulaire produit / livre — 100% dependant du theme de ModalFOrm.

Aucun setStyleSheet() local ici : tous les widgets (QLineEdit, QComboBox,
QSpinBox, QDoubleSpinBox, QTextEdit, QCheckBox, QCheckBox::indicator,
QGroupBox, QLabel) sont deja stylees par ModalFOrm via les regles
QSS "QWidget#modalContent ...", qui s'appliquent a tous les descendants
de #modalContent - y compris ceux de ce formulaire, quelle que soit
la profondeur. ProductForm ne fait donc que construire la structure ;
le theme (dark/light) est gere une seule fois, au meme endroit :
ModalFOrm._apply_theme().
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QLabel, QTextEdit,
    QCheckBox, QGroupBox,
)


class ProductForm(QWidget):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_edit = product is not None
        self._is_book = bool(product.get("is_book", False)) if product else False
        self._classes_data = {}

        self._init_ui()
        self._update_book_fields_visibility()

    def _init_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        def lbl(text):
            # Pas de couleur ici : elle vient de "QWidget#modalContent QLabel"
            # dans ModalForm. On ne fixe QUE le poids de la police, une
            # propriete que l'ancetre ne definit pas -> pas de conflit.
            l = QLabel(text)
            l.setStyleSheet("font-weight: bold; font-size: 14px;")
            return l

        # ── Case a cocher livre : aucun style -> QSS de ModalForm ──
        self.is_book_check = QCheckBox("Ceci est un livre (manuel scolaire)")
        self.is_book_check.setChecked(self._is_book)
        self.is_book_check.toggled.connect(self._update_book_fields_visibility)
        layout.addRow("", self.is_book_check)

        # ── Champs communs ──
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nom du produit")
        if self.product:
            self.name_input.setText(self.product.get("name", ""))
        layout.addRow(lbl("Nom *:"), self.name_input)

        self.desc_input = QTextEdit()
        if self.product:
            self.desc_input.setText(self.product.get("description", "") or "")
        layout.addRow(lbl("Description:"), self.desc_input)

        self.category_combo = QComboBox()
        self.category_combo.addItem("- Aucune -", None)
        layout.addRow(lbl("Categorie:"), self.category_combo)

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("- Aucun -", None)
        layout.addRow(lbl("Fournisseur:"), self.supplier_combo)

        self.buy_price = QDoubleSpinBox()
        self.buy_price.setRange(0, 9999999)
        self.buy_price.setDecimals(2)
        if self.product:
            self.buy_price.setValue(self.product.get("buy_price", 0) or 0)
        layout.addRow(lbl("Prix d'achat *:"), self.buy_price)

        self.sell_price = QDoubleSpinBox()
        self.sell_price.setRange(0, 9999999)
        self.sell_price.setDecimals(2)
        if self.product:
            self.sell_price.setValue(self.product.get("sell_price", 0) or 0)
        layout.addRow(lbl("Prix de vente *:"), self.sell_price)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        if self.product:
            self.stock_input.setValue(self.product.get("stock_quantity", 0) or 0)
            self.stock_input.setEnabled(False)
            self.stock_input.setToolTip("Utilisez 'Ajuster le stock' pour modifier la quantite")
        layout.addRow(lbl("Stock:"), self.stock_input)

        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(0, 999999)
        self.threshold_input.setValue(
            self.product.get("min_stock_threshold", 10) if self.product else 10
        )
        layout.addRow(lbl("Seuil d'alerte:"), self.threshold_input)

        self.packaging_combo = QComboBox()
        self.packaging_combo.addItems(["unitaire", "paquet", "carton", "lot"])
        if self.product:
            self.packaging_combo.setCurrentText(
                self.product.get("packaging_type", "unitaire") or "unitaire"
            )
        layout.addRow(lbl("Emballage:"), self.packaging_combo)

        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.sku_input.setText(self.product.get("sku", "") or "")
        layout.addRow(lbl("SKU:"), self.sku_input)

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.barcode_input.setText(self.product.get("barcode", "") or "")
        layout.addRow(lbl("Code-barres:"), self.barcode_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ex: Etagere A1")
        if self.product:
            self.location_input.setText(self.product.get("location", "") or "")
        layout.addRow(lbl("Emplacement:"), self.location_input)

        # ── Groupe livre : aucun style -> QSS de ModalForm (QGroupBox) ──
        self.book_group = QGroupBox("Informations du livre")
        book_layout = QFormLayout(self.book_group)
        book_layout.setSpacing(12)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Ex: Mathematiques, Francais...")
        if self.product and self._is_book:
            self.subject_input.setText(self.product.get("subject", "") or "")
        book_layout.addRow(lbl("Matiere *:"), self.subject_input)

        self.publisher_input = QLineEdit()
        if self.product and self._is_book:
            self.publisher_input.setText(self.product.get("publisher", "") or "")
        book_layout.addRow(lbl("Editeur:"), self.publisher_input)

        self.isbn_input = QLineEdit()
        if self.product and self._is_book:
            self.isbn_input.setText(self.product.get("isbn", "") or "")
        book_layout.addRow(lbl("ISBN:"), self.isbn_input)

        self.level_combo = QComboBox()
        book_layout.addRow(lbl("Niveau *:"), self.level_combo)

        self.system_combo = QComboBox()
        book_layout.addRow(lbl("Systeme *:"), self.system_combo)

        self.class_combo = QComboBox()
        book_layout.addRow(lbl("Classe *:"), self.class_combo)

        layout.addRow(self.book_group)

        # ── Actif : aucun style -> QSS de ModalForm ──
        self.active_chk = QCheckBox("Produit actif")
        self.active_chk.setChecked(
            bool(self.product.get("is_active", 1)) if self.product else True
        )
        layout.addRow("", self.active_chk)

    def _update_book_fields_visibility(self, checked=None):
        is_book = self.is_book_check.isChecked()
        self.book_group.setVisible(is_book)
        for w in (
            self.subject_input, self.publisher_input, self.isbn_input,
            self.level_combo, self.system_combo, self.class_combo,
        ):
            w.setEnabled(is_book)

    def set_school_data(self, levels: list, systems: list, classes_data: dict):
        self._classes_data = classes_data or {}
        self.level_combo.blockSignals(True)
        self.level_combo.clear()
        for level in levels:
            self.level_combo.addItem(level["name"], level["id"])
        self.level_combo.blockSignals(False)

        self.system_combo.blockSignals(True)
        self.system_combo.clear()
        for system in systems:
            self.system_combo.addItem(system["name"], system["id"])
        self.system_combo.blockSignals(False)

        if not getattr(self, "_school_signals_connected", False):
            self.level_combo.currentTextChanged.connect(self._update_classes)
            self.system_combo.currentTextChanged.connect(self._update_classes)
            self._school_signals_connected = True

        if self.product and self._is_book:
            self._update_classes()
            if self.product.get("class_name"):
                idx = self.class_combo.findText(self.product.get("class_name"))
                if idx >= 0:
                    self.class_combo.setCurrentIndex(idx)

    def _update_classes(self, *_args):
        self.class_combo.clear()
        level_name = self.level_combo.currentText()
        system_name = self.system_combo.currentText()
        if not level_name or not system_name:
            return
        for class_item in self._classes_data.get("classes", []):
            if (
                class_item.get("level_name") == level_name
                and class_item.get("system_name") == system_name
            ):
                self.class_combo.addItem(class_item["name"], class_item["id"])

    def get_data(self) -> dict:
        is_book = self.is_book_check.isChecked()
        data = {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.toPlainText().strip() or None,
            "category_id": self.category_combo.currentData(),
            "supplier_id": self.supplier_combo.currentData(),
            "buy_price": self.buy_price.value(),
            "sell_price": self.sell_price.value(),
            "stock_quantity": self.stock_input.value(),
            "min_stock_threshold": self.threshold_input.value(),
            "packaging_type": self.packaging_combo.currentText(),
            "sku": self.sku_input.text().strip() or None,
            "barcode": self.barcode_input.text().strip() or None,
            "location": self.location_input.text().strip() or None,
            "is_active": self.active_chk.isChecked(),
            "is_book": is_book,
        }
        if is_book:
            data.update({
                "subject": self.subject_input.text().strip(),
                "publisher": self.publisher_input.text().strip() or None,
                "isbn": self.isbn_input.text().strip() or None,
                "level_id": self.level_combo.currentData(),
                "system_id": self.system_combo.currentData(),
                "class_id": self.class_combo.currentData(),
            })
        return data

    def validate(self) -> tuple:
        if not self.name_input.text().strip():
            return False, "Le nom est obligatoire."
        if self.buy_price.value() <= 0:
            return False, "Le prix d'achat doit etre superieur a 0."
        if self.sell_price.value() <= 0:
            return False, "Le prix de vente doit etre superieur a 0."
        if self.is_book_check.isChecked():
            if not self.subject_input.text().strip():
                return False, "La matiere est obligatoire pour un livre."
            if self.class_combo.currentData() is None:
                return False, "Veuillez selectionner une classe valide."
        return True, ""