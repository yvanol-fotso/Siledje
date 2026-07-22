"""
Manager de la gestion du stock — connecté au vrai schéma products/categories/suppliers.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import (
    QMessageBox, QWidget, QFormLayout, QLineEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QLabel, QTextEdit, QCheckBox
)

from src.database.repositories.catalog_repository import CatalogRepository


class ProductTableModel(QAbstractTableModel):

    HEADERS = ["ID", "Nom", "Catégorie", "Fournisseur", "Prix Achat", "Prix Vente",
               "Stock", "Seuil Min", "Emballage", "SKU", "Actif"]

    def __init__(self, products: list):
        super().__init__()
        self._products = products

    def rowCount(self, parent=None):
        return len(self._products)

    def columnCount(self, parent=None):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        p = self._products[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            values = [
                str(p["id"]), p["name"], p.get("category_name") or "—",
                p.get("supplier_name") or "—", f"{p['buy_price']:.2f}",
                f"{p['sell_price']:.2f}", str(p["stock_quantity"]),
                str(p["min_stock_threshold"]), p["packaging_type"],
                p.get("sku") or "—", "Oui" if p["is_active"] else "Non",
            ]
            return values[col]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_product(self, row):
        return self._products[row] if 0 <= row < len(self._products) else None

    def set_products(self, products):
        self.beginResetModel()
        self._products = products
        self.endResetModel()


class StockManager(QObject):
    """Manager de gestion du stock — vrai schéma, plus de dummy data."""

    version = "5.0"

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.current_user = current_user

        self.catalog = CatalogRepository()
        self.current_search = ""
        self.current_category_id = None

        self.rows = self.catalog.get_all_products()
        self.model = ProductTableModel(self.rows)

        print(f"[StockManager v{self.version}] Initialisé avec {len(self.rows)} produits")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.stock_view import StockView
            self.view = StockView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            print("[StockManager] Vue créée et initialisée")
        return self.view

    def _initialize_view(self):
        self.view.set_table_model(self.model)
        categories = [c["name"] for c in self.catalog.get_all_categories()]
        self.view.update_categories(["Toutes"] + categories)
        suppliers = [s["name"] for s in self.catalog.get_all_suppliers()]
        self.view.update_suppliers(["Tous"] + suppliers)

    def _connect_view_signals(self):
        self.view.search_requested.connect(self.on_search_requested)
        self.view.category_filter_changed.connect(self.on_category_changed)
        self.view.add_product_requested.connect(self.add_product)
        self.view.edit_product_requested.connect(self.edit_product)
        self.view.delete_product_requested.connect(self.delete_product)
        self.view.refresh_requested.connect(self.refresh)

    # ========== FILTRES ==========

    @Slot(str)
    def on_search_requested(self, text: str):
        self.current_search = text.strip()
        self._apply_filters()

    @Slot(str)
    def on_category_changed(self, category: str):
        if category == "Toutes":
            self.current_category_id = None
        else:
            cat = self.catalog.get_category_by_name(category)
            self.current_category_id = cat["id"] if cat else None
        self._apply_filters()

    def _apply_filters(self):
        if self.current_search:
            products = self.catalog.search_products(self.current_search)
        else:
            products = self.catalog.get_all_products()

        if self.current_category_id:
            products = [p for p in products if p["category_id"] == self.current_category_id]

        self.rows = products
        self.model.set_products(self.rows)
        print(f"[StockManager] {len(self.rows)} produits affichés")

    # ========== FORMULAIRE PRODUIT ==========

    def _create_product_form(self, product=None):
        from src.ui.widgets.ModalView import ModalView

        is_edit = product is not None
        modal = ModalView(
            title="Modifier le Produit" if is_edit else "Ajouter un Produit",
            parent=self.view, width=750, height=750,
            ok_text="Enregistrer", cancel_text="Annuler"
        )

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)

        label_style = "font-weight: bold; font-size: 14px;"
        input_style = """
            font-size: 14px; padding: 8px; border: 2px solid #bdc3c7;
            border-radius: 8px; min-height: 36px;
        """

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(label_style)
            return l

        name_input = QLineEdit(product["name"] if is_edit else "")
        name_input.setStyleSheet(input_style)

        description_input = QTextEdit(product.get("description", "") if is_edit else "")
        description_input.setStyleSheet(input_style)
        description_input.setMaximumHeight(70)

        categories = self.catalog.get_all_categories()
        category_combo = QComboBox()
        category_combo.setStyleSheet(input_style)
        category_combo.addItem("— Aucune —", None)
        for c in categories:
            category_combo.addItem(c["name"], c["id"])
        if is_edit and product.get("category_id"):
            idx = category_combo.findData(product["category_id"])
            if idx >= 0:
                category_combo.setCurrentIndex(idx)

        suppliers = self.catalog.get_all_suppliers()
        supplier_combo = QComboBox()
        supplier_combo.setStyleSheet(input_style)
        supplier_combo.addItem("— Aucun —", None)
        for s in suppliers:
            supplier_combo.addItem(s["name"], s["id"])
        if is_edit and product.get("supplier_id"):
            idx = supplier_combo.findData(product["supplier_id"])
            if idx >= 0:
                supplier_combo.setCurrentIndex(idx)

        buy_price_input = QDoubleSpinBox()
        buy_price_input.setStyleSheet(input_style)
        buy_price_input.setRange(0, 9999999)
        buy_price_input.setDecimals(2)
        if is_edit:
            buy_price_input.setValue(product["buy_price"])

        sell_price_input = QDoubleSpinBox()
        sell_price_input.setStyleSheet(input_style)
        sell_price_input.setRange(0, 9999999)
        sell_price_input.setDecimals(2)
        if is_edit:
            sell_price_input.setValue(product["sell_price"])

        stock_input = QSpinBox()
        stock_input.setStyleSheet(input_style)
        stock_input.setRange(0, 999999)
        if is_edit:
            stock_input.setValue(product["stock_quantity"])
            stock_input.setEnabled(False)  # édition via "Ajuster le stock" uniquement
            stock_input.setToolTip("Utilisez 'Ajuster le stock' pour modifier la quantité")

        threshold_input = QSpinBox()
        threshold_input.setStyleSheet(input_style)
        threshold_input.setRange(0, 999999)
        threshold_input.setValue(product["min_stock_threshold"] if is_edit else 10)

        packaging_combo = QComboBox()
        packaging_combo.setStyleSheet(input_style)
        packaging_combo.addItems(["unitaire", "paquet", "carton"])
        if is_edit:
            packaging_combo.setCurrentText(product["packaging_type"])

        sku_input = QLineEdit(product.get("sku", "") if is_edit else "")
        sku_input.setStyleSheet(input_style)
        sku_input.setPlaceholderText("Optionnel — auto si vide")

        location_input = QLineEdit(product.get("location", "") if is_edit else "")
        location_input.setStyleSheet(input_style)
        location_input.setPlaceholderText("Ex: Étagère 1A")

        barcode_input = QLineEdit()
        barcode_input.setStyleSheet(input_style)
        barcode_input.setPlaceholderText("Optionnel — laissez vide si généré plus tard")
        if is_edit:
            barcodes = self.catalog.get_barcodes_for_product(product["id"])
            primary = next((b["barcode_text"] for b in barcodes if b["is_primary"]),
                           barcodes[0]["barcode_text"] if barcodes else "")
            barcode_input.setText(primary)

        is_book_chk = QCheckBox("Ceci est un manuel scolaire")
        is_book_chk.setChecked(bool(product.get("is_book")) if is_edit else False)

        active_chk = QCheckBox("Produit actif")
        active_chk.setChecked(bool(product.get("is_active", 1)) if is_edit else True)

        form_layout.addRow(lbl("Nom *:"), name_input)
        form_layout.addRow(lbl("Description:"), description_input)
        form_layout.addRow(lbl("Catégorie:"), category_combo)
        form_layout.addRow(lbl("Fournisseur:"), supplier_combo)
        form_layout.addRow(lbl("Prix d'achat *:"), buy_price_input)
        form_layout.addRow(lbl("Prix de vente *:"), sell_price_input)
        form_layout.addRow(lbl("Stock initial:" if not is_edit else "Stock actuel:"), stock_input)
        form_layout.addRow(lbl("Seuil alerte:"), threshold_input)
        form_layout.addRow(lbl("Emballage:"), packaging_combo)
        form_layout.addRow(lbl("SKU:"), sku_input)
        form_layout.addRow(lbl("Code-barres:"), barcode_input)
        form_layout.addRow(lbl("Emplacement:"), location_input)
        form_layout.addRow(QLabel(""), is_book_chk)
        form_layout.addRow(QLabel(""), active_chk)

        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)

        modal.name_input = name_input
        modal.description_input = description_input
        modal.category_combo = category_combo
        modal.supplier_combo = supplier_combo
        modal.buy_price_input = buy_price_input
        modal.sell_price_input = sell_price_input
        modal.stock_input = stock_input
        modal.threshold_input = threshold_input
        modal.packaging_combo = packaging_combo
        modal.sku_input = sku_input
        modal.location_input = location_input
        modal.barcode_input = barcode_input
        modal.is_book_chk = is_book_chk
        modal.active_chk = active_chk

        return modal

    # ========== SLOTS ==========

    @Slot()
    def add_product(self):
        try:
            modal = self._create_product_form()

            def on_save():
                name = modal.name_input.text().strip()
                if not name:
                    QMessageBox.warning(self.view, "Validation", "Le nom est obligatoire.")
                    return

                sku = modal.sku_input.text().strip() or None
                if sku and self.catalog.sku_exists(sku):
                    QMessageBox.warning(self.view, "Validation", f"Le SKU '{sku}' existe déjà.")
                    return

                new_id = self.catalog.create_product(
                    name=name,
                    description=modal.description_input.toPlainText().strip() or None,
                    category_id=modal.category_combo.currentData(),
                    supplier_id=modal.supplier_combo.currentData(),
                    buy_price=modal.buy_price_input.value(),
                    sell_price=modal.sell_price_input.value(),
                    stock_quantity=0,
                    min_stock_threshold=modal.threshold_input.value(),
                    packaging_type=modal.packaging_combo.currentText(),
                    location=modal.location_input.text().strip() or None,
                    sku=sku,
                    is_book=modal.is_book_chk.isChecked(),
                )

                barcode_val = modal.barcode_input.text().strip()
                if barcode_val and not self.catalog.barcode_exists(barcode_val):
                    self.catalog.add_barcode(barcode_val, new_id, "internal", is_primary=True)

                initial_stock = modal.stock_input.value()
                if initial_stock > 0:
                    user_id = self.current_user.id if self.current_user else None
                    self.catalog.adjust_stock(
                        new_id, initial_stock, "entry", user_id=user_id,
                        reason="Stock initial à la création"
                    )

                if not modal.active_chk.isChecked():
                    self.catalog.set_product_active(new_id, False)

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès", f"Produit '{name}' ajouté.")
                print(f"[StockManager] Produit créé: ID {new_id}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de l'ajout:\n{e}")
            print(f"[StockManager] ERREUR ajout: {e}")

    @Slot(int)
    def edit_product(self, row: int):
        product = self.model.get_product(row)
        if not product:
            QMessageBox.warning(self.view, "Sélection requise", "Sélectionnez un produit.")
            return

        try:
            modal = self._create_product_form(product)

            def on_save():
                name = modal.name_input.text().strip()
                if not name:
                    QMessageBox.warning(self.view, "Validation", "Le nom est obligatoire.")
                    return

                sku = modal.sku_input.text().strip() or None
                if sku and self.catalog.sku_exists(sku, exclude_id=product["id"]):
                    QMessageBox.warning(self.view, "Validation", f"Le SKU '{sku}' existe déjà.")
                    return

                self.catalog.update_product(
                    product["id"],
                    name=name,
                    description=modal.description_input.toPlainText().strip() or None,
                    category_id=modal.category_combo.currentData(),
                    supplier_id=modal.supplier_combo.currentData(),
                    buy_price=modal.buy_price_input.value(),
                    sell_price=modal.sell_price_input.value(),
                    min_stock_threshold=modal.threshold_input.value(),
                    packaging_type=modal.packaging_combo.currentText(),
                    location=modal.location_input.text().strip() or None,
                    sku=sku,
                    is_book=modal.is_book_chk.isChecked(),
                    is_active=1 if modal.active_chk.isChecked() else 0,
                )

                barcode_val = modal.barcode_input.text().strip()
                if barcode_val:
                    existing_barcodes = self.catalog.get_barcodes_for_product(product["id"])
                    if not any(b["barcode_text"] == barcode_val for b in existing_barcodes):
                        self.catalog.add_barcode(barcode_val, product["id"], "internal", is_primary=True)

                self.refresh()
                modal.accept()
                QMessageBox.information(self.view, "Succès", f"Produit '{name}' modifié.")
                print(f"[StockManager] Produit modifié: ID {product['id']}")

            modal.ok_clicked.connect(on_save)
            modal.exec()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la modification:\n{e}")

    @Slot(int)
    def delete_product(self, row: int):
        """Désactivation logique (les FK RESTRICT empêchent la suppression physique)."""
        product = self.model.get_product(row)
        if not product:
            QMessageBox.warning(self.view, "Sélection requise", "Sélectionnez un produit.")
            return

        reply = QMessageBox.question(
            self.view, "Confirmation",
            f"Désactiver '{product['name']}' ?\n\nLe produit ne sera plus visible en vente "
            "mais son historique sera conservé.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.catalog.set_product_active(product["id"], False)
            self.refresh()
            QMessageBox.information(self.view, "Succès", f"'{product['name']}' désactivé.")

    @Slot()
    def refresh(self):
        self._apply_filters()
        print("[StockManager] Vue rafraîchie depuis la BDD")