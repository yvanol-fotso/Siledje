"""
Gestionnaire des opérations sur les fichiers.
Import/Export CSV alignés sur le schéma réel (CatalogRepository / UserRepository)
+ Sauvegarde/Restauration de la base de données + Activation de licence.

Contrôle d'accès basé sur les permissions réelles du rôle de current_user
(table roles) — double protection : boutons désactivés côté vue via
apply_permissions(), et revérification systématique côté manager avant
chaque action sensible.
"""

import csv
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox

from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.user_repository import UserRepository
from src.database.connection import get_db_connection
from src.managers.license.license_manager import LicenseManager


def _norm(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", s)


def _fmt_int(n) -> str:
    try:
        return f"{int(n):,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(n)


def _fmt_money(n) -> str:
    try:
        return f"{int(round(float(n))):,}".replace(",", " ") + " FCFA"
    except (TypeError, ValueError):
        return str(n)


class FileManager(QObject):
    """Gère toutes les opérations fichier (import/export/sauvegarde/licence) de l'application."""

    version = "3.0.0"

    PRODUCT_COLUMNS_FR = [
        "Nom", "Description", "Catégorie", "Fournisseur", "SKU",
        "Prix Achat", "Prix Vente", "Stock", "Seuil Min", "Emplacement",
        "Conditionnement", "Unités par Paquet", "Taux TVA", "Livre", "Notes",
    ]
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
        "emplacement": "location",
        "conditionnement": "packaging_type",
        "unitesparpaquet": "units_per_pack", "unitespaquet": "units_per_pack",
        "tauxtva": "tax_rate", "tva": "tax_rate",
        "livre": "is_book",
        "notes": "notes", "remarques": "notes",
    }

    SUPPLIER_COLUMNS_FR = [
        "Nom", "Contact", "Email", "Téléphone", "Téléphone 2",
        "Adresse", "Ville", "Conditions Paiement", "Notes",
    ]
    SUPPLIER_HEADER_MAP = {
        "nom": "name",
        "contact": "contact_name", "contactname": "contact_name",
        "email": "email",
        "telephone": "phone", "tel": "phone",
        "telephone2": "phone2", "tel2": "phone2",
        "adresse": "address",
        "ville": "city",
        "conditionspaiement": "payment_terms", "paiement": "payment_terms",
        "notes": "notes",
    }

    CATEGORY_COLUMNS_FR = ["Nom", "Catégorie Parent", "Description", "Icône", "Couleur", "Ordre"]
    CATEGORY_HEADER_MAP = {
        "nom": "name",
        "categorieparent": "parent_name", "parent": "parent_name",
        "description": "description",
        "icone": "icon",
        "couleur": "color",
        "ordre": "sort_order",
    }

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None
        self.current_user = current_user

        self.catalog_repo = CatalogRepository()
        self.user_repo = UserRepository()
        self.license_manager = LicenseManager()

        conn = get_db_connection()
        self.db_path = Path(
            getattr(conn, "db_path", None)
            or getattr(conn, "db_name", None)
            or "librairie.db"
        )

        self.backup_dir = Path("data/backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"[FileManager v{self.version}] Initialisé — BDD : {self.db_path}")

    # ────────────────────────────────────────────────────────────────
    # PERMISSIONS
    # ────────────────────────────────────────────────────────────────

    def _has_permission(self, permission_name: str) -> bool:
        """Vérifie une permission réelle du rôle. Aucun utilisateur -> tout refusé."""
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission_name)

    def _require_permission(self, permission_name: str, action_label: str) -> bool:
        """Revérification côté manager avant une action sensible. Affiche un
        message et retourne False si refusé — filet de sécurité même si un
        bouton restait cliquable côté vue."""
        if self._has_permission(permission_name):
            return True
        QMessageBox.warning(
            self.view, "Permission refusée",
            f"Vous n'avez pas la permission d'effectuer cette action : {action_label}.\n"
            "Contactez un administrateur si vous pensez que c'est une erreur."
        )
        return False

    def get_ui(self):
        if self.view is None:
            from src.ui.views.file_view import FileView
            self.view = FileView(self.parent_window)
            self._connect_signals()
            self._apply_permissions()
            self._refresh_backups_list()
            self._refresh_all_panels()
        return self.view

    def _apply_permissions(self):
        if not self.view:
            return
        self.view.apply_permissions(
            can_manage_stock=self._has_permission("can_manage_stock"),
            can_manage_users=self._has_permission("can_manage_users"),
            can_configure_system=self._has_permission("can_configure_system"),
        )

    def _connect_signals(self):
        v = self.view
        v.import_products_requested.connect(self.import_products_csv)
        v.export_products_requested.connect(self.export_products_csv)
        v.template_products_requested.connect(self.generate_products_template)

        v.import_suppliers_requested.connect(self.import_suppliers_csv)
        v.export_suppliers_requested.connect(self.export_suppliers_csv)
        v.template_suppliers_requested.connect(self.generate_suppliers_template)

        v.import_categories_requested.connect(self.import_categories_csv)
        v.export_categories_requested.connect(self.export_categories_csv)
        v.template_categories_requested.connect(self.generate_categories_template)

        v.export_users_requested.connect(self.export_users_csv)

        v.activate_license_requested.connect(self.activate_license)

        v.create_backup_requested.connect(self.create_backup)
        v.restore_backup_requested.connect(self.restore_backup)
        v.delete_backup_requested.connect(self.delete_backup)
        v.refresh_backups_requested.connect(self._refresh_backups_list)

    def _refresh_backups_list(self):
        if self.view:
            self.view.update_backups_list(self._get_backups_list())

    def _get_backups_list(self) -> list:
        backups = []
        for f in sorted(self.backup_dir.glob("*.db"), reverse=True):
            size_kb = f.stat().st_size / 1024
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            backups.append({
                "name": f.name, "path": str(f),
                "size": f"{size_kb:.1f} KB",
                "date": mtime.strftime("%d/%m/%Y %H:%M:%S"),
            })
        return backups

    def _map_headers(self, fieldnames, header_map):
        result = {}
        for h in fieldnames:
            key = header_map.get(_norm(h))
            if key:
                result[key] = h
        return result

    # ────────────────────────────────────────────────────────────────
    # RÉSUMÉS
    # ────────────────────────────────────────────────────────────────

    def _refresh_all_panels(self):
        if not self.view:
            return
        try:
            products = self.catalog_repo.get_all_products(active_only=False)
            low_stock = self.catalog_repo.get_low_stock_products()
            suppliers = self.catalog_repo.get_all_suppliers(active_only=False)
            categories = self.catalog_repo.get_all_categories(active_only=False)
            users = self.user_repo.get_all_users()

            stock_value = sum(
                float(p.get("buy_price") or 0) * float(p.get("stock_quantity") or 0)
                for p in products
            )
            self.view.products_panel.set_stats([
                (_fmt_int(len(products)), "Produit(s)"),
                (_fmt_int(len(low_stock)), "En stock bas"),
                (_fmt_money(stock_value), "Valeur du stock"),
            ])

            with_email = sum(1 for s in suppliers if s.get("email"))
            with_phone = sum(1 for s in suppliers if s.get("phone"))
            self.view.suppliers_panel.set_stats([
                (_fmt_int(len(suppliers)), "Fournisseur(s)"),
                (_fmt_int(with_email), "Avec email"),
                (_fmt_int(with_phone), "Avec téléphone"),
            ])

            main_cats = sum(1 for c in categories if not c.get("parent_id"))
            sub_cats = len(categories) - main_cats
            self.view.categories_panel.set_stats([
                (_fmt_int(len(categories)), "Catégorie(s)"),
                (_fmt_int(main_cats), "Principales"),
                (_fmt_int(sub_cats), "Sous-catégories"),
            ])

            if self._has_permission("can_manage_users"):
                active_users = sum(1 for u in users if u.get("is_active"))
                self.view.users_panel.set_stats([
                    (_fmt_int(len(users)), "Utilisateur(s)"),
                    (_fmt_int(active_users), "Actif(s)"),
                    (_fmt_int(len(users) - active_users), "Inactif(s)"),
                ])
        except Exception as e:
            print(f"[FileManager] Erreur rafraîchissement résumés : {e}")

        self._refresh_license_panel()

    def _refresh_license_panel(self):
        if not self.view or not self._has_permission("can_configure_system"):
            return
        try:
            status = self.license_manager.check_current_license()
            info = self.license_manager.current_license
            days = self.license_manager.days_remaining()
            self.view.license_panel.set_status(status, info, days)
        except Exception as e:
            print(f"[FileManager] Erreur rafraîchissement licence : {e}")

    # ────────────────────────────────────────────────────────────────
    # LICENCE — réservé aux profils can_configure_system
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def activate_license(self, key_text: str):
        if not self._require_permission("can_configure_system", "activer une licence"):
            return

        key = (key_text or "").strip()
        if not key:
            QMessageBox.warning(self.view, "Clé requise", "Veuillez saisir ou charger une clé de licence.")
            return
        try:
            ok = self.license_manager.activate_license(key)
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de l'activation :\n{e}")
            return

        if ok:
            QMessageBox.information(self.view, "Licence activée", "La nouvelle licence a été activée avec succès.")
        else:
            QMessageBox.critical(
                self.view, "Licence invalide",
                "Cette clé est invalide, corrompue, ou déjà expirée."
            )
        self._refresh_license_panel()

    # ────────────────────────────────────────────────────────────────
    # PRODUITS — import réservé à can_manage_stock, export libre
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_products_csv(self, file_path: str):
        if not self._require_permission("can_manage_stock", "importer des produits"):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"{file_path}")
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    QMessageBox.warning(self.view, "CSV vide", "Le fichier est vide ou mal formaté.")
                    return

                cols = self._map_headers(reader.fieldnames, self.PRODUCT_HEADER_MAP)
                if "name" not in cols:
                    QMessageBox.warning(
                        self.view, "Colonne manquante",
                        f"La colonne 'Nom' est obligatoire.\n\nColonnes trouvées :\n{', '.join(reader.fieldnames)}"
                    )
                    return

                category_cache, supplier_cache = {}, {}

                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get(cols.get("name", ""), "").strip()
                        if not name:
                            errors.append(f"Ligne {row_num} : nom manquant")
                            continue

                        def num(key, default=0.0):
                            raw = row.get(cols.get(key, ""), "")
                            raw = (raw or "").strip().replace(",", ".")
                            if raw == "":
                                return default
                            return float(raw)

                        def integer(key, default=0):
                            raw = row.get(cols.get(key, ""), "")
                            raw = (raw or "").strip()
                            return int(raw) if raw else default

                        category_name = row.get(cols.get("category", ""), "").strip()
                        supplier_name = row.get(cols.get("supplier", ""), "").strip()

                        category_id = None
                        if category_name:
                            category_id = category_cache.get(category_name.lower())
                            if category_id is None:
                                existing = self.catalog_repo.get_category_by_name(category_name)
                                category_id = existing["id"] if existing else \
                                    self.catalog_repo.create_category(category_name)
                                category_cache[category_name.lower()] = category_id

                        supplier_id = None
                        if supplier_name:
                            supplier_id = supplier_cache.get(supplier_name.lower())
                            if supplier_id is None:
                                match = next(
                                    (s for s in self.catalog_repo.get_all_suppliers(active_only=False)
                                     if s["name"].lower() == supplier_name.lower()), None
                                )
                                supplier_id = match["id"] if match else \
                                    self.catalog_repo.create_supplier(supplier_name)
                                supplier_cache[supplier_name.lower()] = supplier_id

                        is_book_raw = row.get(cols.get("is_book", ""), "").strip().lower()
                        is_book = is_book_raw in ("1", "oui", "true", "vrai", "yes")

                        sku = row.get(cols.get("sku", ""), "").strip() or None
                        if sku and self.catalog_repo.sku_exists(sku):
                            existing_product = self.catalog_repo.get_product_by_sku(sku)
                            self.catalog_repo.update_product(
                                existing_product["id"],
                                name=name,
                                description=row.get(cols.get("description", ""), "").strip(),
                                category_id=category_id, supplier_id=supplier_id,
                                buy_price=num("buy_price"), sell_price=num("sell_price"),
                                stock_quantity=integer("stock_quantity"),
                                min_stock_threshold=integer("min_stock_threshold", 10),
                                packaging_type=row.get(cols.get("packaging_type", ""), "unitaire").strip() or "unitaire",
                                units_per_pack=integer("units_per_pack", 1),
                                location=row.get(cols.get("location", ""), "").strip(),
                                tax_rate=num("tax_rate"), is_book=is_book,
                                notes=row.get(cols.get("notes", ""), "").strip(),
                            )
                        else:
                            self.catalog_repo.create_product(
                                name=name,
                                description=row.get(cols.get("description", ""), "").strip(),
                                category_id=category_id, supplier_id=supplier_id,
                                buy_price=num("buy_price"), sell_price=num("sell_price"),
                                stock_quantity=integer("stock_quantity"),
                                min_stock_threshold=integer("min_stock_threshold", 10),
                                packaging_type=row.get(cols.get("packaging_type", ""), "unitaire").strip() or "unitaire",
                                units_per_pack=integer("units_per_pack", 1),
                                location=row.get(cols.get("location", ""), "").strip(),
                                sku=sku, tax_rate=num("tax_rate"), is_book=is_book,
                                notes=row.get(cols.get("notes", ""), "").strip(),
                            )
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("produit(s)", imported, errors)
            self._refresh_all_panels()

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_products_csv(self, file_path: str):
        try:
            products = self.catalog_repo.get_all_products(active_only=False)
            if not products:
                QMessageBox.information(self.view, "Aucune donnée", "Il n'y a aucun produit à exporter.")
                return

            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(".csv")

            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(self.PRODUCT_COLUMNS_FR)
                for p in products:
                    writer.writerow([
                        p["name"], p.get("description") or "",
                        p.get("category_name") or "", p.get("supplier_name") or "",
                        p.get("sku") or "",
                        str(p["buy_price"]).replace(".", ","),
                        str(p["sell_price"]).replace(".", ","),
                        p["stock_quantity"], p["min_stock_threshold"],
                        p.get("location") or "", p.get("packaging_type") or "unitaire",
                        p.get("units_per_pack") or 1,
                        str(p.get("tax_rate") or 0).replace(".", ","),
                        "Oui" if p.get("is_book") else "Non",
                        p.get("notes") or "",
                    ])

            self._report_export(path, len(products), "produit(s)")
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", str(e))

    def generate_products_template(self, file_path: str):
        if not self._require_permission("can_manage_stock", "télécharger un modèle d'import"):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.PRODUCT_COLUMNS_FR)
            writer.writerow(["Stylo Bic", "Stylo à bille bleu", "Papeterie", "Fournisseur ABC",
                              "STY-001", "150", "250", "100", "10", "Rayon A2",
                              "unitaire", "1", "19,25", "Non", ""])
            writer.writerow(["Dictionnaire Larousse", "Édition 2024", "Manuels Scolaires", "",
                              "DIC-002", "3000", "5000", "20", "5", "Rayon B1",
                              "unitaire", "1", "0", "Oui", ""])
        QMessageBox.information(self.view, "Modèle créé", f"Modèle produits créé :\n{path.absolute()}")

    # ────────────────────────────────────────────────────────────────
    # FOURNISSEURS
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_suppliers_csv(self, file_path: str):
        if not self._require_permission("can_manage_stock", "importer des fournisseurs"):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"{file_path}")
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    QMessageBox.warning(self.view, "CSV vide", "Le fichier est vide ou mal formaté.")
                    return
                cols = self._map_headers(reader.fieldnames, self.SUPPLIER_HEADER_MAP)
                if "name" not in cols:
                    QMessageBox.warning(self.view, "Colonne manquante", "La colonne 'Nom' est obligatoire.")
                    return

                existing_suppliers = {
                    s["name"].lower(): s for s in self.catalog_repo.get_all_suppliers(active_only=False)
                }

                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get(cols.get("name", ""), "").strip()
                        if not name:
                            errors.append(f"Ligne {row_num} : nom manquant")
                            continue

                        fields = dict(
                            contact_name=row.get(cols.get("contact_name", ""), "").strip(),
                            email=row.get(cols.get("email", ""), "").strip(),
                            phone=row.get(cols.get("phone", ""), "").strip(),
                            phone2=row.get(cols.get("phone2", ""), "").strip(),
                            address=row.get(cols.get("address", ""), "").strip(),
                            city=row.get(cols.get("city", ""), "").strip(),
                            payment_terms=row.get(cols.get("payment_terms", ""), "").strip(),
                            notes=row.get(cols.get("notes", ""), "").strip(),
                        )

                        existing = existing_suppliers.get(name.lower())
                        if existing:
                            self.catalog_repo.update_supplier(existing["id"], **fields)
                        else:
                            self.catalog_repo.create_supplier(name=name, **fields)
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("fournisseur(s)", imported, errors)
            self._refresh_all_panels()
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_suppliers_csv(self, file_path: str):
        try:
            suppliers = self.catalog_repo.get_all_suppliers(active_only=False)
            if not suppliers:
                QMessageBox.information(self.view, "Aucune donnée", "Il n'y a aucun fournisseur à exporter.")
                return
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(".csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(self.SUPPLIER_COLUMNS_FR)
                for s in suppliers:
                    writer.writerow([
                        s["name"], s.get("contact_name") or "", s.get("email") or "",
                        s.get("phone") or "", s.get("phone2") or "", s.get("address") or "",
                        s.get("city") or "", s.get("payment_terms") or "", s.get("notes") or "",
                    ])
            self._report_export(path, len(suppliers), "fournisseur(s)")
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", str(e))

    def generate_suppliers_template(self, file_path: str):
        if not self._require_permission("can_manage_stock", "télécharger un modèle d'import"):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.SUPPLIER_COLUMNS_FR)
            writer.writerow(["Fournisseur ABC", "Jean Dupont", "contact@abc.cm", "699000000",
                              "", "Rue du Marché", "Bafoussam", "30 jours", ""])
        QMessageBox.information(self.view, "Modèle créé", f"Modèle fournisseurs créé :\n{path.absolute()}")

    # ────────────────────────────────────────────────────────────────
    # CATÉGORIES
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_categories_csv(self, file_path: str):
        if not self._require_permission("can_manage_stock", "importer des catégories"):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"{file_path}")
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    QMessageBox.warning(self.view, "CSV vide", "Le fichier est vide ou mal formaté.")
                    return
                cols = self._map_headers(reader.fieldnames, self.CATEGORY_HEADER_MAP)
                if "name" not in cols:
                    QMessageBox.warning(self.view, "Colonne manquante", "La colonne 'Nom' est obligatoire.")
                    return

                name_to_id = {c["name"].lower(): c["id"]
                              for c in self.catalog_repo.get_all_categories(active_only=False)}

                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get(cols.get("name", ""), "").strip()
                        if not name:
                            errors.append(f"Ligne {row_num} : nom manquant")
                            continue
                        parent_name = row.get(cols.get("parent_name", ""), "").strip()
                        parent_id = name_to_id.get(parent_name.lower()) if parent_name else None

                        sort_order_raw = row.get(cols.get("sort_order", ""), "0").strip()
                        sort_order = int(sort_order_raw) if sort_order_raw else 0

                        if name.lower() in name_to_id:
                            self.catalog_repo.update_category(
                                name_to_id[name.lower()], parent_id=parent_id,
                                description=row.get(cols.get("description", ""), "").strip(),
                                icon=row.get(cols.get("icon", ""), "").strip(),
                                color=row.get(cols.get("color", ""), "").strip(),
                                sort_order=sort_order,
                            )
                        else:
                            new_id = self.catalog_repo.create_category(
                                name=name, parent_id=parent_id,
                                description=row.get(cols.get("description", ""), "").strip(),
                                icon=row.get(cols.get("icon", ""), "").strip(),
                                color=row.get(cols.get("color", ""), "").strip(),
                                sort_order=sort_order,
                            )
                            name_to_id[name.lower()] = new_id
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("catégorie(s)", imported, errors)
            self._refresh_all_panels()
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_categories_csv(self, file_path: str):
        try:
            categories = self.catalog_repo.get_all_categories(active_only=False)
            if not categories:
                QMessageBox.information(self.view, "Aucune donnée", "Il n'y a aucune catégorie à exporter.")
                return
            id_to_name = {c["id"]: c["name"] for c in categories}
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(".csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(self.CATEGORY_COLUMNS_FR)
                for c in categories:
                    writer.writerow([
                        c["name"], id_to_name.get(c.get("parent_id"), ""),
                        c.get("description") or "", c.get("icon") or "",
                        c.get("color") or "", c.get("sort_order") or 0,
                    ])
            self._report_export(path, len(categories), "catégorie(s)")
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", str(e))

    def generate_categories_template(self, file_path: str):
        if not self._require_permission("can_manage_stock", "télécharger un modèle d'import"):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.CATEGORY_COLUMNS_FR)
            writer.writerow(["Cahiers", "Papeterie", "Tous formats de cahiers", "", "", "1"])
        QMessageBox.information(self.view, "Modèle créé", f"Modèle catégories créé :\n{path.absolute()}")

    # ────────────────────────────────────────────────────────────────
    # UTILISATEURS — export réservé à can_manage_users
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def export_users_csv(self, file_path: str):
        if not self._require_permission("can_manage_users", "exporter la liste des utilisateurs"):
            return
        try:
            users = self.user_repo.get_all_users()
            if not users:
                QMessageBox.information(self.view, "Aucune donnée", "Il n'y a aucun utilisateur à exporter.")
                return
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(".csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Nom d'utilisateur", "Nom complet", "Email", "Téléphone",
                                  "Rôle", "Actif", "Dernière connexion"])
                for u in users:
                    writer.writerow([
                        u["username"], u.get("full_name") or "", u.get("email") or "",
                        u.get("phone") or "", u.get("role_name") or "",
                        "Oui" if u.get("is_active") else "Non",
                        u.get("last_login_at") or "",
                    ])
            self._report_export(path, len(users), "utilisateur(s)")
            QMessageBox.information(
                self.view, "Rappel sécurité",
                "Cet export ne contient jamais les mots de passe (hachés ou non)."
            )
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", str(e))

    # ────────────────────────────────────────────────────────────────
    # SAUVEGARDE / RESTAURATION — restaurer/supprimer réservé à can_configure_system
    # ────────────────────────────────────────────────────────────────

    @Slot()
    def create_backup(self):
        try:
            if not self.db_path.exists():
                QMessageBox.warning(self.view, "Base introuvable", f"{self.db_path}")
                return
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"sauvegarde_{timestamp}.db"
            shutil.copy2(str(self.db_path), str(backup_path))
            self._refresh_backups_list()
            size_kb = backup_path.stat().st_size / 1024
            QMessageBox.information(
                self.view, "Sauvegarde créée",
                f"Fichier : {backup_path.name}\nTaille : {size_kb:.1f} KB"
            )
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", str(e))

    @Slot(str)
    def restore_backup(self, backup_path: str):
        if not self._require_permission("can_configure_system", "restaurer une sauvegarde"):
            return
        try:
            path = Path(backup_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"{backup_path}")
                return
            reply = QMessageBox.question(
                self.view, "Confirmer la restauration",
                f"Cette action remplacera la base de données actuelle par :\n{path.name}\n\n"
                f"Une sauvegarde automatique de sécurité sera créée avant. Continuer ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            auto_backup = self.backup_dir / f"avant_restauration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if self.db_path.exists():
                shutil.copy2(str(self.db_path), str(auto_backup))
            shutil.copy2(str(path), str(self.db_path))

            if self.current_user:
                self.user_repo.log_audit(
                    self.current_user.id, "RESTORE_DB", "database", None,
                    description=f"Restauration depuis {path.name}"
                )

            QMessageBox.information(
                self.view, "Restauration réussie",
                f"Base restaurée depuis {path.name}.\nRedémarrez l'application."
            )
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", str(e))

    @Slot(str)
    def delete_backup(self, backup_path: str):
        if not self._require_permission("can_configure_system", "supprimer une sauvegarde"):
            return
        try:
            path = Path(backup_path)
            reply = QMessageBox.question(
                self.view, "Supprimer la sauvegarde",
                f"Supprimer définitivement {path.name} ?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            path.unlink()
            self._refresh_backups_list()
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", str(e))

    # ────────────────────────────────────────────────────────────────
    # HELPERS
    # ────────────────────────────────────────────────────────────────

    def _report_result(self, label: str, imported: int, errors: list):
        msg = f"Import terminé.\n\n{imported} {label} traité(s) avec succès."
        if errors:
            msg += f"\n\n{len(errors)} erreur(s) :\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n... et {len(errors) - 10} autre(s)."
            QMessageBox.warning(self.view, "Import partiel", msg)
        else:
            QMessageBox.information(self.view, "Import réussi", msg)

    def _report_export(self, path: Path, count: int, label: str):
        size_kb = path.stat().st_size / 1024
        QMessageBox.information(
            self.view, "Export réussi",
            f"{count} {label} exporté(s).\n\nFichier : {path.name}\nTaille : {size_kb:.1f} KB"
        )