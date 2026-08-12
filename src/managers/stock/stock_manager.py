"""
Manager stock v9.2 — ThemedTable + InfoDialog (plus de QMessageBox).
La gestion du theme (dark/light) n'est plus dupliquee ici : elle est
entierement deleguee a ModalForm / theme_manager, qui sont la seule
source de verite. StockManager ne fait plus que construire les vues
et les donnees.
"""

from PySide6.QtCore import QObject, Slot, Signal

from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.school_repository import SchoolRepository
from src.ui.views.stock.stock_view import StockView
from src.ui.views.stock.stock_form import ProductForm
from src.ui.widgets.modal_form import ModalForm
from src.ui.widgets.InfoDialog import InfoDialog


class StockManager(QObject):
    version = "9.2"

    data_changed = Signal()
    error_occurred = Signal(str)
    success_occurred = Signal(str)

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent = parent
        self.current_user = current_user
        self.catalog = CatalogRepository()
        self.school_repo = SchoolRepository()
        self._view = None
        self._products = []
        self.current_search = ""
        self.current_filters = {}
        print(f"[StockManager v{self.version}] Initialise")

    def get_ui(self) -> StockView:
        if self._view is None:
            self._view = StockView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
        return self._view

    def _connect_view_signals(self):
        self._view.search_requested.connect(self.on_search)
        self._view.clear_search_requested.connect(self.on_clear_search)
        self._view.filter_changed.connect(self.on_filter_changed)
        self._view.add_product_requested.connect(self.add_product)
        self._view.edit_product_requested.connect(self.edit_product)
        self._view.delete_product_requested.connect(self.delete_product)
        self._view.import_csv_requested.connect(self.import_csv)
        self._view.export_csv_requested.connect(self.export_csv)
        self._view.refresh_requested.connect(self.refresh)

    def _initialize_view(self):
        products = self.catalog.get_all_products()
        self._products = products
        self._view.update_products(products)
        self._view.update_categories(
            [c["name"] for c in self.catalog.get_all_categories()]
        )
        self._view.update_suppliers(
            [s["name"] for s in self.catalog.get_all_suppliers()]
        )
        classes = self.school_repo.get_all_classes()
        self._view.update_classes(sorted({c["name"] for c in classes}))
        print(f"[StockManager] Vue initialisee avec {len(products)} produits")

    # ========== FILTRES ==========

    @Slot(str)
    def on_search(self, text: str):
        self.current_search = text.strip()
        self._apply_filters()

    @Slot()
    def on_clear_search(self):
        self.current_search = ""
        self._apply_filters()

    @Slot(dict)
    def on_filter_changed(self, filters: dict):
        self.current_filters = filters
        self._apply_filters()

    def _apply_filters(self):
        if self.current_search:
            products = self.catalog.search_products(self.current_search)
        else:
            products = self.catalog.get_all_products()

        if self.current_filters.get("category") not in (None, "", "Toutes"):
            cat = self.catalog.get_category_by_name(self.current_filters["category"])
            if cat:
                products = [p for p in products if p["category_id"] == cat["id"]]

        if self.current_filters.get("supplier") not in (None, "", "Tous"):
            supplier = self.catalog.get_supplier_by_name(self.current_filters["supplier"])
            if supplier:
                products = [p for p in products if p["supplier_id"] == supplier["id"]]

        type_filter = self.current_filters.get("type", "Tous")
        if type_filter == "Produits":
            products = [p for p in products if not p.get("is_book", False)]
        elif type_filter == "Livres":
            products = [p for p in products if p.get("is_book", False)]

        if self.current_filters.get("class") not in (None, "", "Toutes"):
            class_obj = self.school_repo.get_class_by_name(self.current_filters["class"])
            if class_obj:
                ids = self.school_repo.get_product_ids_for_class(class_obj["id"])
                products = [p for p in products if p["id"] in ids]

        self._products = products
        self._view.update_products(products)

    # ========== AJOUT ==========

    @Slot()
    def add_product(self):
        try:
            form = ProductForm()
            self._populate_form_combos(form)
            self._populate_book_combos(form)

            modal = ModalForm(
                title="Ajouter un produit",
                parent=self._view,
                width=650, height=750,
                ok_text="Enregistrer", cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_ok():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self._view, "Validation", msg)
                    return

                data = form.get_data()
                if data["sku"] and self.catalog.sku_exists(data["sku"]):
                    InfoDialog.warning(
                        self._view, "Validation",
                        f"Le SKU '{data['sku']}' existe deja.",
                    )
                    return

                product_id = self.catalog.create_product(
                    name=data["name"],
                    description=data["description"],
                    category_id=data["category_id"],
                    supplier_id=data["supplier_id"],
                    buy_price=data["buy_price"],
                    sell_price=data["sell_price"],
                    stock_quantity=0,
                    min_stock_threshold=data["min_stock_threshold"],
                    packaging_type=data["packaging_type"],
                    location=data["location"],
                    sku=data["sku"],
                    is_book=data["is_book"],
                    is_active=data["is_active"],
                )

                if data["barcode"]:
                    self.catalog.add_barcode(
                        data["barcode"], product_id, "internal", is_primary=True
                    )
                else:
                    barcode = self.catalog.generate_internal_barcode(product_id)
                    self.catalog.add_barcode(
                        barcode, product_id, "internal", is_primary=True
                    )

                if not data["sku"]:
                    category_name = None
                    if data["category_id"]:
                        cat = self.catalog.get_category_by_id(data["category_id"])
                        category_name = cat["name"] if cat else None
                    sku = self.catalog.generate_sku(product_id, category_name)
                    self.catalog.update_product(product_id, sku=sku)

                if data["stock_quantity"] > 0:
                    user_id = self.current_user.id if self.current_user else None
                    self.catalog.adjust_stock(
                        product_id, data["stock_quantity"], "entry",
                        user_id=user_id, reason="Stock initial a la creation",
                    )

                if data["is_book"]:
                    self.school_repo.create_book(
                        product_id=product_id,
                        school_class_id=data["class_id"],
                        title=data["name"],
                        subject=data["subject"],
                        publisher=data["publisher"],
                        isbn=data["isbn"],
                    )

                self.refresh()
                modal.accept()
                label = "Livre" if data["is_book"] else "Produit"
                self.success_occurred.emit(f"{label} '{data['name']}' ajoute.")
                InfoDialog.success(
                    self._view, "Succes", f"{label} '{data['name']}' ajoute."
                )

            modal.ok_clicked.connect(on_ok)
            modal.exec()
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(self._view, "Erreur", f"Erreur lors de l'ajout:\n{e}")

    # ========== MODIFICATION ==========

    @Slot(int)
    def edit_product(self, row: int):
        product = self._view.get_product(row)
        if not product:
            InfoDialog.warning(self._view, "Erreur", "Produit introuvable.")
            return

        is_book = bool(product.get("is_book", False))
        try:
            form = ProductForm(product)
            self._populate_form_combos(form)
            if is_book:
                self._populate_book_combos(form)
                self._populate_book_data(form, product["id"])

            modal = ModalForm(
                title="Modifier le produit" + (" (Livre)" if is_book else ""),
                parent=self._view,
                width=650, height=750 if is_book else 700,
                ok_text="Enregistrer", cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_ok():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self._view, "Validation", msg)
                    return

                data = form.get_data()
                if data["sku"] and self.catalog.sku_exists(
                    data["sku"], exclude_id=product["id"]
                ):
                    InfoDialog.warning(
                        self._view, "Validation",
                        f"Le SKU '{data['sku']}' existe deja.",
                    )
                    return

                self.catalog.update_product(
                    product["id"],
                    name=data["name"],
                    description=data["description"],
                    category_id=data["category_id"],
                    supplier_id=data["supplier_id"],
                    buy_price=data["buy_price"],
                    sell_price=data["sell_price"],
                    min_stock_threshold=data["min_stock_threshold"],
                    packaging_type=data["packaging_type"],
                    location=data["location"],
                    sku=data["sku"],
                    is_active=data["is_active"],
                )

                if data["barcode"]:
                    barcodes = self.catalog.get_barcodes_for_product(product["id"])
                    if barcodes:
                        self.catalog.update_barcode(barcodes[0]["id"], data["barcode"])
                    else:
                        self.catalog.add_barcode(
                            data["barcode"], product["id"], "internal", is_primary=True
                        )

                if is_book:
                    self.school_repo.update_book(
                        product_id=product["id"],
                        school_class_id=data["class_id"],
                        title=data["name"],
                        subject=data["subject"],
                        publisher=data["publisher"],
                        isbn=data["isbn"],
                    )

                self.refresh()
                modal.accept()
                self.success_occurred.emit(f"Produit '{data['name']}' modifie.")
                InfoDialog.success(
                    self._view, "Succes", f"'{data['name']}' modifie."
                )

            modal.ok_clicked.connect(on_ok)
            modal.exec()
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(
                self._view, "Erreur", f"Erreur lors de la modification:\n{e}"
            )

    # ========== SUPPRESSION ==========

    @Slot(int)
    def delete_product(self, row: int):
        product = self._view.get_product(row)
        if not product:
            return

        ok = InfoDialog.question(
            self._view,
            "Confirmation",
            f"Desactiver '{product['name']}' ?\n\n"
            "Le produit ne sera plus visible en vente "
            "mais son historique sera conserve.",
            ok_text="Yes",
            cancel_text="No",
        )
        if not ok:
            return

        try:
            self.catalog.set_product_active(product["id"], False)
            self.refresh()
            self.success_occurred.emit(f"Produit '{product['name']}' desactive.")
            InfoDialog.success(
                self._view, "Succes", f"'{product['name']}' desactive."
            )
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(
                self._view, "Erreur", f"Erreur lors de la suppression:\n{e}"
            )

    # ========== IMPORT / EXPORT ==========

    @Slot(str, dict)
    def import_csv(self, file_path: str, options: dict):
        try:
            import csv

            is_book = options.get("type") == "Livres / Manuels scolaires"
            skip_header = options.get("skip_header", True)
            update_stock = options.get("update_stock", False)
            reason = options.get("reason", "Import CSV")

            with open(file_path, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            if skip_header and rows:
                rows = rows[1:]

            count, errors = 0, []
            for idx, row in enumerate(rows):
                if len(row) < 6:
                    continue
                name = row[0].strip()
                if not name:
                    continue
                try:
                    buy_price = float(row[1]) if row[1] else 0
                    sell_price = float(row[2]) if row[2] else 0
                    stock = int(row[3]) if row[3] else 0
                    category_name = row[4].strip() if len(row) > 4 else None
                    supplier_name = row[5].strip() if len(row) > 5 else None

                    category_id = None
                    if category_name:
                        cat = self.catalog.get_category_by_name(category_name)
                        category_id = (
                            cat["id"] if cat
                            else self.catalog.create_category(category_name)
                        )

                    supplier_id = None
                    if supplier_name:
                        sup = self.catalog.get_supplier_by_name(supplier_name)
                        supplier_id = (
                            sup["id"] if sup
                            else self.catalog.create_supplier(supplier_name)
                        )

                    existing = None
                    if update_stock:
                        for p in self.catalog.get_all_products():
                            if p["name"].lower() == name.lower():
                                existing = p
                                break

                    if existing:
                        self.catalog.adjust_stock(
                            existing["id"], stock, "entry",
                            reason=f"{reason} - Mise a jour stock",
                        )
                        count += 1
                    else:
                        product_id = self.catalog.create_product(
                            name=name,
                            category_id=category_id,
                            supplier_id=supplier_id,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            stock_quantity=0,
                            min_stock_threshold=10,
                            packaging_type="unitaire",
                            is_book=is_book,
                            is_active=True,
                        )
                        if stock > 0:
                            self.catalog.adjust_stock(
                                product_id, stock, "entry", reason=reason
                            )
                        sku = self.catalog.generate_sku(
                            product_id, category_name or "GEN"
                        )
                        self.catalog.update_product(product_id, sku=sku)
                        if is_book:
                            self.school_repo.create_book(
                                product_id=product_id,
                                school_class_id=1,
                                title=name,
                                subject="General",
                                publisher=None,
                                isbn=None,
                            )
                        count += 1
                except Exception as e:
                    errors.append(f"Ligne {idx + 1}: {e}")

            self.refresh()
            if errors:
                msg = (
                    f"Import termine: {count} produits.\n\nErreurs:\n"
                    + "\n".join(errors[:5])
                )
                if len(errors) > 5:
                    msg += f"\n... et {len(errors) - 5} autres"
                InfoDialog.warning(self._view, "Import termine", msg)
            else:
                self.success_occurred.emit(f"Import: {count} produits.")
                InfoDialog.success(
                    self._view, "Succes",
                    f"Import termine: {count} produits.\nRaison: {reason}",
                )
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(self._view, "Erreur", f"Erreur lors de l'import:\n{e}")

    @Slot(str)
    def export_csv(self, file_path: str):
        try:
            import csv

            products = self._products
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Nom", "Prix Achat", "Prix Vente", "Stock", "Categorie", "Fournisseur"]
                )
                for p in products:
                    writer.writerow([
                        p["name"], p["buy_price"], p["sell_price"],
                        p["stock_quantity"],
                        p.get("category_name", ""),
                        p.get("supplier_name", ""),
                    ])
            self.success_occurred.emit(f"Export: {len(products)} produits.")
            InfoDialog.success(
                self._view, "Succes",
                f"Export termine: {len(products)} produits.",
            )
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(self._view, "Erreur", f"Erreur lors de l'export:\n{e}")

    # ========== HELPERS ==========

    def _populate_form_combos(self, form):
        for cat in self.catalog.get_all_categories():
            form.category_combo.addItem(cat["name"], cat["id"])
        for sup in self.catalog.get_all_suppliers():
            form.supplier_combo.addItem(sup["name"], sup["id"])
        if form.product:
            if form.product.get("category_id"):
                idx = form.category_combo.findData(form.product["category_id"])
                if idx >= 0:
                    form.category_combo.setCurrentIndex(idx)
            if form.product.get("supplier_id"):
                idx = form.supplier_combo.findData(form.product["supplier_id"])
                if idx >= 0:
                    form.supplier_combo.setCurrentIndex(idx)

    def _populate_book_combos(self, form):
        form.set_school_data(
            self.school_repo.get_levels(),
            self.school_repo.get_systems(),
            {"classes": self.school_repo.get_all_classes()},
        )

    def _populate_book_data(self, form, product_id: int):
        cursor = self.catalog.db.get_cursor()
        cursor.execute("""
            SELECT b.*, sc.name as class_name, sl.name as level_name, ss.name as system_name
            FROM books b
            JOIN school_classes sc ON b.school_class_id = sc.id
            JOIN school_levels sl ON sc.level_id = sl.id
            JOIN school_systems ss ON sc.system_id = ss.id
            WHERE b.product_id = ?
        """, (product_id,))
        book = cursor.fetchone()
        if not book:
            return
        form.subject_input.setText(book["subject"] or "")
        form.publisher_input.setText(book["publisher"] or "")
        form.isbn_input.setText(book["isbn"] or "")
        idx = form.level_combo.findText(book["level_name"])
        if idx >= 0:
            form.level_combo.setCurrentIndex(idx)
        idx = form.system_combo.findText(book["system_name"])
        if idx >= 0:
            form.system_combo.setCurrentIndex(idx)
        form._update_classes()
        idx = form.class_combo.findText(book["class_name"])
        if idx >= 0:
            form.class_combo.setCurrentIndex(idx)

    @Slot()
    def refresh(self):
        self._apply_filters()
        self.data_changed.emit()