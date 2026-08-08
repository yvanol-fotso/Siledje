"""
Formulaire produit / livre — Palette unifiée.
"""

from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QLabel, QTextEdit,
    QCheckBox, QGroupBox,
)
from src.ui.views.base.base_view import Palette


class ProductForm(QWidget):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_edit = product is not None
        self._is_book = bool(product.get("is_book", False)) if product else False
        self._classes_data = {}
        self._init_ui()
        self._update_book_fields_visibility()  # OK : méthode définie plus bas

    def _input_css(self) -> str:
        return f"""
            QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox {{
                font-size: 14px; padding: 8px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 8px; min-height: 36px;
                background: {Palette.LIGHT_BG}; color: {Palette.LIGHT_TEXT};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {Palette.ACCENT};
            }}
            QTextEdit {{ min-height: 70px; max-height: 70px; }}
        """

    def _init_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(0, 0, 0, 0)

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(
                f"font-weight: bold; font-size: 14px; color: {Palette.LIGHT_TEXT};"
            )
            return l

        css = self._input_css()

        # ── Case à cocher livre ──
        self.is_book_check = QCheckBox("Ceci est un livre (manuel scolaire)")
        self.is_book_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px; font-weight: bold;
                color: {Palette.ACCENT}; spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px; height: 20px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 4px; background: white;
            }}
            QCheckBox::indicator:checked {{
                background: {Palette.ACCENT}; border-color: {Palette.ACCENT};
            }}
        """)
        self.is_book_check.setChecked(self._is_book)
        self.is_book_check.toggled.connect(self._update_book_fields_visibility)
        layout.addRow("", self.is_book_check)

        # ── Champs communs ──
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(css)
        self.name_input.setPlaceholderText("Nom du produit")
        if self.product:
            self.name_input.setText(self.product.get("name", ""))
        layout.addRow(lbl("Nom *:"), self.name_input)

        self.desc_input = QTextEdit()
        self.desc_input.setStyleSheet(css)
        if self.product:
            self.desc_input.setText(self.product.get("description", "") or "")
        layout.addRow(lbl("Description:"), self.desc_input)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(css)
        self.category_combo.addItem("- Aucune -", None)
        layout.addRow(lbl("Categorie:"), self.category_combo)

        self.supplier_combo = QComboBox()
        self.supplier_combo.setStyleSheet(css)
        self.supplier_combo.addItem("- Aucun -", None)
        layout.addRow(lbl("Fournisseur:"), self.supplier_combo)

        self.buy_price = QDoubleSpinBox()
        self.buy_price.setStyleSheet(css)
        self.buy_price.setRange(0, 9999999)
        self.buy_price.setDecimals(2)
        if self.product:
            self.buy_price.setValue(self.product.get("buy_price", 0) or 0)
        layout.addRow(lbl("Prix d'achat *:"), self.buy_price)

        self.sell_price = QDoubleSpinBox()
        self.sell_price.setStyleSheet(css)
        self.sell_price.setRange(0, 9999999)
        self.sell_price.setDecimals(2)
        if self.product:
            self.sell_price.setValue(self.product.get("sell_price", 0) or 0)
        layout.addRow(lbl("Prix de vente *:"), self.sell_price)

        self.stock_input = QSpinBox()
        self.stock_input.setStyleSheet(css)
        self.stock_input.setRange(0, 999999)
        if self.product:
            self.stock_input.setValue(self.product.get("stock_quantity", 0) or 0)
            self.stock_input.setEnabled(False)
            self.stock_input.setToolTip("Utilisez 'Ajuster le stock' pour modifier la quantite")
        layout.addRow(lbl("Stock:"), self.stock_input)

        self.threshold_input = QSpinBox()
        self.threshold_input.setStyleSheet(css)
        self.threshold_input.setRange(0, 999999)
        self.threshold_input.setValue(
            self.product.get("min_stock_threshold", 10) if self.product else 10
        )
        layout.addRow(lbl("Seuil d'alerte:"), self.threshold_input)

        self.packaging_combo = QComboBox()
        self.packaging_combo.setStyleSheet(css)
        self.packaging_combo.addItems(["unitaire", "paquet", "carton", "lot"])
        if self.product:
            self.packaging_combo.setCurrentText(
                self.product.get("packaging_type", "unitaire") or "unitaire"
            )
        layout.addRow(lbl("Emballage:"), self.packaging_combo)

        self.sku_input = QLineEdit()
        self.sku_input.setStyleSheet(css)
        self.sku_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.sku_input.setText(self.product.get("sku", "") or "")
        layout.addRow(lbl("SKU:"), self.sku_input)

        self.barcode_input = QLineEdit()
        self.barcode_input.setStyleSheet(css)
        self.barcode_input.setPlaceholderText("Laissez vide pour auto-generation")
        if self.product:
            self.barcode_input.setText(self.product.get("barcode", "") or "")
        layout.addRow(lbl("Code-barres:"), self.barcode_input)

        self.location_input = QLineEdit()
        self.location_input.setStyleSheet(css)
        self.location_input.setPlaceholderText("Ex: Etagere A1")
        if self.product:
            self.location_input.setText(self.product.get("location", "") or "")
        layout.addRow(lbl("Emplacement:"), self.location_input)

        # ── Groupe livre ──
        self.book_group = QGroupBox("Informations du livre")
        self.book_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px; font-weight: bold;
                border: 2px solid {Palette.ACCENT};
                border-radius: 8px; margin-top: 10px; padding-top: 16px;
                color: {Palette.LIGHT_TEXT};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 4px 10px; color: {Palette.ACCENT};
            }}
        """)
        book_layout = QFormLayout(self.book_group)
        book_layout.setSpacing(12)

        self.subject_input = QLineEdit()
        self.subject_input.setStyleSheet(css)
        self.subject_input.setPlaceholderText("Ex: Mathematiques, Francais...")
        if self.product and self._is_book:
            self.subject_input.setText(self.product.get("subject", "") or "")
        book_layout.addRow(lbl("Matiere *:"), self.subject_input)

        self.publisher_input = QLineEdit()
        self.publisher_input.setStyleSheet(css)
        if self.product and self._is_book:
            self.publisher_input.setText(self.product.get("publisher", "") or "")
        book_layout.addRow(lbl("Editeur:"), self.publisher_input)

        self.isbn_input = QLineEdit()
        self.isbn_input.setStyleSheet(css)
        if self.product and self._is_book:
            self.isbn_input.setText(self.product.get("isbn", "") or "")
        book_layout.addRow(lbl("ISBN:"), self.isbn_input)

        self.level_combo = QComboBox()
        self.level_combo.setStyleSheet(css)
        book_layout.addRow(lbl("Niveau *:"), self.level_combo)

        self.system_combo = QComboBox()
        self.system_combo.setStyleSheet(css)
        book_layout.addRow(lbl("Systeme *:"), self.system_combo)

        self.class_combo = QComboBox()
        self.class_combo.setStyleSheet(css)
        book_layout.addRow(lbl("Classe *:"), self.class_combo)

        layout.addRow(self.book_group)

        # ── Actif ──
        self.active_chk = QCheckBox("Produit actif")
        self.active_chk.setChecked(
            bool(self.product.get("is_active", 1)) if self.product else True
        )
        self.active_chk.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px; font-weight: bold;
                color: {Palette.LIGHT_TEXT}; spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px; height: 20px;
                border: 2px solid {Palette.BORDER_GRAY};
                border-radius: 4px; background: white;
            }}
            QCheckBox::indicator:checked {{
                background: {Palette.ACCENT}; border-color: {Palette.ACCENT};
            }}
        """)
        layout.addRow("", self.active_chk)

    # ══════════════════════════════════════════════
    # ✅ Méthode manquante (cause de ton erreur)
    # ══════════════════════════════════════════════

    def _update_book_fields_visibility(self, checked=None):
        """Affiche / cache le bloc livre selon la case à cocher."""
        is_book = self.is_book_check.isChecked()
        self.book_group.setVisible(is_book)
        for w in (
            self.subject_input,
            self.publisher_input,
            self.isbn_input,
            self.level_combo,
            self.system_combo,
            self.class_combo,
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

        # Connecter une seule fois — évite RuntimeWarning
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