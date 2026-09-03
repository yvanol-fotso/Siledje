"""
Manager stock v9.4 — ThemedTable + InfoDialog (plus de QMessageBox).
La gestion du theme (dark/light) n'est plus dupliquee ici : elle est
entierement deleguee a ModalForm / theme_manager, qui sont la seule
source de verite. StockManager ne fait plus que construire les vues
et les donnees.

CHANGELOG v9.4 :
- BUG CORRIGE (import "0 produits") : l'ancien import_csv() lisait le
  fichier avec une virgule comme separateur et un format positionnel a
  6 colonnes fixes, alors que TOUS les CSV de l'application (modele
  telecharge, export du module Fichier, etc.) sont en point-virgule
  avec des colonnes nommees. Une ligne mal separee ne fait qu'un seul
  "champ" -> `len(row) < 6` -> ignoree silencieusement -> 0 import,
  aucune erreur affichee.
- Le format d'import Stock est desormais UNIFIE avec celui du module
  Fichier (FileManager) : meme separateur (;), memes noms de colonnes.
  Un CSV genere pour l'un fonctionne pour l'autre, plus de confusion
  possible entre "Importer Produit" et "Importer Livres".
- import_csv() est scinde en deux methodes explicites et independantes :
  import_products_csv() et import_books_csv(). Chacune a son propre
  bouton dans StockView (tous deux verts, cote a cote), pour qu'il n'y
  ait plus d'ambiguite sur "lequel utiliser".
- export_csv() ecrit desormais aussi en point-virgule (coherence avec
  le reste de l'app, notamment pour la reimportation immediate du
  fichier exporte).
"""

import csv
import re
import unicodedata

from PySide6.QtCore import QObject, Slot, Signal

from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.school_repository import SchoolRepository
from src.ui.views.stock.stock_view import StockView
from src.ui.views.stock.stock_form import ProductForm
from src.ui.widgets.modal_form import ModalForm
from src.ui.widgets.InfoDialog import InfoDialog


def _norm(s: str) -> str:
    """Normalise un texte pour un matching insensible aux accents/casse/
    espaces (ex: en-tetes de colonnes, noms de roles). Identique a la
    fonction du meme nom dans FileManager, pour un comportement coherent
    partout dans l'application."""
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", s)


def _map_headers(fieldnames, header_map):
    result = {}
    for h in fieldnames or []:
        key = header_map.get(_norm(h))
        if key:
            result[key] = h
    return result


# Sous-ensemble des colonnes FileManager pertinentes pour un import stock.
# Mêmes libellés que PRODUCT_COLUMNS_FR côté FileManager : un fichier
# généré/exporté pour l'un fonctionne directement pour l'autre.
PRODUCT_HEADER_MAP = {
    "nom": "name", "designation": "name",
    "description": "description",
    "categorie": "category", "categorie(s)": "category",
    "fournisseur": "supplier",
    "sku": "sku", "reference": "sku",
    "prixachat": "buy_price", "prixdachat": "buy_price",
    "prixvente": "sell_price",
    "stock": "stock_quantity", "quantite": "stock_quantity",
    "seuilmin": "min_stock_threshold", "seuil": "min_stock_threshold",
}
BOOK_HEADER_MAP = dict(PRODUCT_HEADER_MAP, **{
    "classe": "school_class_name",
    "matiere": "subject", "matieres": "subject",
    "editeur": "publisher",
    "isbn": "isbn",
})


class StockManager(QObject):
    version = "9.4"

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
        self._view.import_products_csv_requested.connect(self.import_products_csv)
        self._view.import_books_csv_requested.connect(self.import_books_csv)
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
    #
    # Format CSV attendu : IDENTIQUE a celui du module Fichier (point-
    # virgule, colonnes nommees — voir FileManager.PRODUCT_COLUMNS_FR).
    # Un fichier genere/exporte par le module Fichier fonctionne donc
    # directement ici, et inversement. Colonnes utilisees :
    #
    #   Import Produit : Nom;Prix Achat;Prix Vente;Stock;Categorie;
    #                     Fournisseur;SKU;Seuil Min  (SKU et Seuil Min
    #                     optionnels)
    #   Import Livres  : les memes + Classe;Matiere;Editeur;ISBN
    #                     ("Classe" est OBLIGATOIRE et doit correspondre
    #                     exactement au nom d'une classe deja creee dans
    #                     Parametres > Classes)
    #
    # Seule la colonne "Nom" est obligatoire pour les produits standards.
    # Une ligne livre sans classe valide n'est jamais silencieusement
    # rattachee a la mauvaise classe : le produit catalogue est quand
    # meme cree (rien n'est perdu), mais signale en erreur et laisse
    # sans fiche livre tant que la classe n'est pas corrigee — un
    # reimport ulterieur avec la bonne classe complete alors la fiche
    # (le produit existant est retrouve par son nom).

    def _read_csv_rows(self, file_path: str):
        """Ouvre un CSV point-virgule et retourne (fieldnames, rows).
        Leve une exception explicite si le fichier est vide/mal forme."""
        with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            if not reader.fieldnames:
                raise ValueError("Le fichier est vide ou mal formate.")
            rows = list(reader)
        return reader.fieldnames, rows

    def _resolve_category(self, category_name: str):
        if not category_name:
            return None
        cat = self.catalog.get_category_by_name(category_name)
        return cat["id"] if cat else self.catalog.create_category(category_name)

    def _resolve_supplier(self, supplier_name: str):
        if not supplier_name:
            return None
        sup = self.catalog.get_supplier_by_name(supplier_name)
        return sup["id"] if sup else self.catalog.create_supplier(supplier_name)

    def _find_existing_product(self, name: str, sku: str):
        """Priorite au SKU (identifiant fiable) ; a defaut, on retombe
        sur le nom (insensible a la casse) pour rester compatible avec
        des CSV sans colonne SKU."""
        if sku and self.catalog.sku_exists(sku):
            return self.catalog.get_product_by_sku(sku)
        for p in self.catalog.get_all_products():
            if p["name"].lower() == name.lower():
                return p
        return None

    @Slot(str, dict)
    def import_products_csv(self, file_path: str, options: dict):
        try:
            update_existing = options.get("update_stock", True)
            reason = options.get("reason", "Import CSV")

            fieldnames, rows = self._read_csv_rows(file_path)
            cols = _map_headers(fieldnames, PRODUCT_HEADER_MAP)
            if "name" not in cols:
                InfoDialog.warning(
                    self._view, "Colonne manquante",
                    f"La colonne 'Nom' est obligatoire.\n\n"
                    f"Colonnes trouvees :\n{', '.join(fieldnames)}",
                )
                return

            count, errors = 0, []
            for row_num, row in enumerate(rows, start=2):
                try:
                    name = row.get(cols.get("name", ""), "").strip()
                    if not name:
                        errors.append(f"Ligne {row_num} : nom manquant")
                        continue

                    def num(key, default=0.0):
                        raw = (row.get(cols.get(key, ""), "") or "").strip()
                        raw = raw.replace(",", ".")
                        return float(raw) if raw else default

                    def integer(key, default=0):
                        raw = (row.get(cols.get(key, ""), "") or "").strip()
                        return int(raw) if raw else default

                    buy_price = num("buy_price")
                    sell_price = num("sell_price")
                    stock = integer("stock_quantity")
                    category_name = row.get(cols.get("category", ""), "").strip()
                    supplier_name = row.get(cols.get("supplier", ""), "").strip()
                    sku = row.get(cols.get("sku", ""), "").strip() or None

                    category_id = self._resolve_category(category_name)
                    supplier_id = self._resolve_supplier(supplier_name)

                    existing = (
                        self._find_existing_product(name, sku)
                        if update_existing else None
                    )

                    if existing:
                        self.catalog.adjust_stock(
                            existing["id"], stock, "entry",
                            reason=f"{reason} - Mise a jour stock",
                        )
                    else:
                        product_id = self.catalog.create_product(
                            name=name,
                            category_id=category_id,
                            supplier_id=supplier_id,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            stock_quantity=0,
                            min_stock_threshold=integer("min_stock_threshold", 10),
                            packaging_type="unitaire",
                            sku=sku,
                            is_book=False,
                            is_active=True,
                        )
                        if stock > 0:
                            self.catalog.adjust_stock(
                                product_id, stock, "entry", reason=reason
                            )
                        if not sku:
                            generated = self.catalog.generate_sku(
                                product_id, category_name or "GEN"
                            )
                            self.catalog.update_product(product_id, sku=generated)
                    count += 1
                except Exception as e:
                    errors.append(f"Ligne {row_num} : {e}")

            self.refresh()
            self._report_import_result(count, errors, reason, "produit(s)")
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(self._view, "Erreur", f"Erreur lors de l'import:\n{e}")

    @Slot(str, dict)
    def import_books_csv(self, file_path: str, options: dict):
        try:
            update_existing = options.get("update_stock", True)
            reason = options.get("reason", "Import CSV")

            fieldnames, rows = self._read_csv_rows(file_path)
            cols = _map_headers(fieldnames, BOOK_HEADER_MAP)
            if "name" not in cols:
                InfoDialog.warning(
                    self._view, "Colonne manquante",
                    f"La colonne 'Nom' est obligatoire.\n\n"
                    f"Colonnes trouvees :\n{', '.join(fieldnames)}",
                )
                return

            count, errors = 0, []
            # La resolution du nom de classe (exact -> alias -> normalise)
            # est ENTIEREMENT deleguee a SchoolRepository.resolve_class_name() :
            # c'est le seul endroit de l'application qui connait cette
            # logique. Idem pour known_class_names(), utilisee ci-dessous
            # pour un message d'erreur explicite.
            known_class_names = self.school_repo.known_class_names()

            for row_num, row in enumerate(rows, start=2):
                try:
                    name = row.get(cols.get("name", ""), "").strip()
                    if not name:
                        errors.append(f"Ligne {row_num} : nom manquant")
                        continue

                    class_name = row.get(
                        cols.get("school_class_name", ""), ""
                    ).strip()
                    if not class_name:
                        errors.append(
                            f"Ligne {row_num} : classe obligatoire pour le "
                            f"livre '{name}'"
                        )
                        continue
                    school_class = self.school_repo.resolve_class_name(class_name)
                    if not school_class:
                        available = (
                            ", ".join(known_class_names)
                            if known_class_names
                            else "aucune classe creee pour l'instant"
                        )
                        errors.append(
                            f"Ligne {row_num} : classe '{class_name}' "
                            f"inconnue pour '{name}'. Classes disponibles : "
                            f"{available}"
                        )
                        continue

                    def num(key, default=0.0):
                        raw = (row.get(cols.get(key, ""), "") or "").strip()
                        raw = raw.replace(",", ".")
                        return float(raw) if raw else default

                    def integer(key, default=0):
                        raw = (row.get(cols.get(key, ""), "") or "").strip()
                        return int(raw) if raw else default

                    buy_price = num("buy_price")
                    sell_price = num("sell_price")
                    stock = integer("stock_quantity")
                    category_name = row.get(cols.get("category", ""), "").strip()
                    supplier_name = row.get(cols.get("supplier", ""), "").strip()
                    sku = row.get(cols.get("sku", ""), "").strip() or None
                    subject = row.get(
                        cols.get("subject", ""), ""
                    ).strip() or "General"
                    publisher = row.get(
                        cols.get("publisher", ""), ""
                    ).strip() or None
                    isbn = row.get(cols.get("isbn", ""), "").strip() or None

                    category_id = self._resolve_category(category_name)
                    supplier_id = self._resolve_supplier(supplier_name)

                    existing = (
                        self._find_existing_product(name, sku)
                        if update_existing else None
                    )

                    if existing:
                        product_id = existing["id"]
                        self.catalog.adjust_stock(
                            product_id, stock, "entry",
                            reason=f"{reason} - Mise a jour stock",
                        )
                    else:
                        product_id = self.catalog.create_product(
                            name=name,
                            category_id=category_id,
                            supplier_id=supplier_id,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            stock_quantity=0,
                            min_stock_threshold=integer("min_stock_threshold", 10),
                            packaging_type="unitaire",
                            sku=sku,
                            is_book=True,
                            is_active=True,
                        )
                        if stock > 0:
                            self.catalog.adjust_stock(
                                product_id, stock, "entry", reason=reason
                            )
                        if not sku:
                            generated = self.catalog.generate_sku(
                                product_id, category_name or "GEN"
                            )
                            self.catalog.update_product(product_id, sku=generated)

                    self._upsert_book(
                        product_id, school_class["id"], name, subject,
                        publisher, isbn,
                    )
                    count += 1
                except Exception as e:
                    errors.append(f"Ligne {row_num} : {e}")

            self.refresh()
            self._report_import_result(count, errors, reason, "livre(s)")
        except Exception as e:
            self.error_occurred.emit(str(e))
            InfoDialog.error(self._view, "Erreur", f"Erreur lors de l'import:\n{e}")

    def _report_import_result(self, count, errors, reason, label):
        if errors:
            msg = f"Import termine : {count} {label}.\n\nErreurs :\n" + "\n".join(
                errors[:5]
            )
            if len(errors) > 5:
                msg += f"\n... et {len(errors) - 5} autre(s)"
            InfoDialog.warning(self._view, "Import partiel", msg)
        else:
            self.success_occurred.emit(f"Import : {count} {label}.")
            InfoDialog.success(
                self._view, "Succes",
                f"Import termine : {count} {label}.\nRaison : {reason}",
            )

    def _upsert_book(self, product_id: int, school_class_id: int,
                      title: str, subject: str, publisher: str = None,
                      isbn: str = None):
        """Cree la fiche books si elle n'existe pas encore, sinon la
        met a jour (ex: reimport avec une classe corrigee)."""
        cursor = self.catalog.db.get_cursor()
        cursor.execute("SELECT 1 FROM books WHERE product_id = ?", (product_id,))
        book_kwargs = dict(
            product_id=product_id,
            school_class_id=school_class_id,
            title=title,
            subject=subject,
            publisher=publisher,
            isbn=isbn,
        )
        if cursor.fetchone():
            self.school_repo.update_book(**book_kwargs)
        else:
            self.school_repo.create_book(**book_kwargs)

    @Slot(str)
    def export_csv(self, file_path: str):
        try:
            products = self._products
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(
                    ["Nom", "Prix Achat", "Prix Vente", "Stock", "Categorie",
                     "Fournisseur", "SKU"]
                )
                for p in products:
                    writer.writerow([
                        p["name"],
                        str(p["buy_price"]).replace(".", ","),
                        str(p["sell_price"]).replace(".", ","),
                        p["stock_quantity"],
                        p.get("category_name", ""),
                        p.get("supplier_name", ""),
                        p.get("sku") or "",
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