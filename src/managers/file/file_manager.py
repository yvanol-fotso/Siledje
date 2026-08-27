"""
Gestionnaire des opérations sur les fichiers.
Import/Export CSV + Sauvegarde/Restauration + Licence.
Messages UI : InfoDialog uniquement (thémé dark/light).
"""

import csv
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot, QTimer

from src.ui.widgets.InfoDialog import InfoDialog
from src.database.repositories.catalog_repository import CatalogRepository
from src.database.repositories.user_repository import UserRepository
from src.managers.license.license_manager import LicenseManager
from src.utils.backup_service import get_backup_service


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
    """Gère toutes les opérations fichier (import/export/sauvegarde/licence)."""

    version = "3.3.0"

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

    CATEGORY_COLUMNS_FR = [
        "Nom", "Catégorie Parent", "Description", "Icône", "Couleur", "Ordre",
    ]
    CATEGORY_HEADER_MAP = {
        "nom": "name",
        "categorieparent": "parent_name", "parent": "parent_name",
        "description": "description",
        "icone": "icon",
        "couleur": "color",
        "ordre": "sort_order",
    }

    # Colonne "Mot de passe" volontairement en dernier avant "Actif" :
    # optionnelle a la modification (on ne change pas un mot de passe
    # existant si la cellule est vide), obligatoire a la creation.
    USER_COLUMNS_FR = [
        "Nom d'utilisateur", "Nom complet", "Email", "Telephone",
        "Role", "Mot de passe", "Actif",
    ]
    USER_HEADER_MAP = {
        "nomdutilisateur": "username", "utilisateur": "username",
        "username": "username",
        "nomcomplet": "full_name", "nom": "full_name",
        "email": "email",
        "telephone": "phone", "tel": "phone",
        "role": "role",
        "motdepasse": "password", "password": "password",
        "actif": "is_active",
    }

    def __init__(self, parent=None, current_user=None, auth_manager=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None
        self.current_user = current_user
        # Nécessaire pour hacher les mots de passe lors de l'import
        # d'utilisateurs (création ou changement de mot de passe).
        # Optionnel : si absent, l'import de nouveaux comptes ou de
        # changements de mot de passe est bloqué proprement (voir
        # import_users_csv), le reste du module continue de fonctionner.
        self.auth_manager = auth_manager

        self.catalog_repo = CatalogRepository()
        self.user_repo = UserRepository()
        self.license_manager = LicenseManager()

        # Backup : plus de logique locale, tout passe par le service partagé.
        self.backup_service = get_backup_service()

        # db_path emprunté au service (une seule résolution du chemin
        # de la BDD dans toute l'app, voir backup_service.py) plutôt que
        # recalculé séparément ici.
        self.db_path = self.backup_service.db_path

        print(f"[FileManager v{self.version}] Initialisé — BDD : {self.db_path}")

    # ────────────────────────────────────────────────────────────────
    # PERMISSIONS
    # ────────────────────────────────────────────────────────────────

    def _has_permission(self, permission_name: str) -> bool:
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission_name)

    def _require_permission(self, permission_name: str, action_label: str) -> bool:
        if self._has_permission(permission_name):
            return True
        InfoDialog.warning(
            self.view,
            "Permission refusee",
            f"Vous n'avez pas la permission d'effectuer cette action : {action_label}.\n"
            "Contactez un administrateur si vous pensez que c'est une erreur.",
        )
        return False

    def get_ui(self):
        if self.view is None:
            from src.ui.views.file.file_view import FileView

            self.view = FileView(self.parent_window)
            self._connect_signals()
            self._apply_permissions()
            self._refresh_backups_list()
            QTimer.singleShot(100, self._refresh_license_panel)
            QTimer.singleShot(200, self._refresh_all_panels)
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

        v.import_users_requested.connect(self.import_users_csv)
        v.export_users_requested.connect(self.export_users_csv)
        v.template_users_requested.connect(self.generate_users_template)

        v.activate_license_requested.connect(self.activate_license)

        v.create_backup_requested.connect(self.create_backup)
        v.restore_backup_requested.connect(self.restore_backup)
        v.delete_backup_requested.connect(self.delete_backup)
        v.refresh_backups_requested.connect(self._refresh_backups_list)

    def _refresh_backups_list(self):
        if self.view:
            self.view.update_backups_list(self._get_backups_list())

    def _get_backups_list(self) -> list:
        # Déléguée entièrement au service : plus de scan manuel du dossier ici.
        return self.backup_service.get_backups_info()

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

            self.view.update_entity_stats(
                "products", len(products), f"{len(low_stock)} en stock bas"
            )
            self.view.update_entity_stats(
                "suppliers",
                len(suppliers),
                f"{sum(1 for s in suppliers if s.get('email'))} avec email",
            )
            self.view.update_entity_stats(
                "categories",
                len(categories),
                f"{sum(1 for c in categories if not c.get('parent_id'))} principales",
            )

            if self._has_permission("can_manage_users"):
                active_users = sum(1 for u in users if u.get("is_active"))
                self.view.update_entity_stats(
                    "users", len(users), f"{active_users} actifs"
                )

            self.view.update_entity_chart("products", [
                ("En stock", len([p for p in products if p.get("stock_quantity", 0) > 10])),
                ("Stock bas", len(low_stock)),
                ("Rupture", len([p for p in products if p.get("stock_quantity", 0) == 0])),
            ])
            self.view.update_entity_chart("suppliers", [
                ("Actifs", len([s for s in suppliers if s.get("is_active", 1)])),
                ("Avec email", sum(1 for s in suppliers if s.get("email"))),
                ("Avec téléphone", sum(1 for s in suppliers if s.get("phone"))),
            ])
        except Exception as e:
            print(f"[FileManager] Erreur rafraîchissement résumés : {e}")

        self._refresh_license_panel()

    def _refresh_license_panel(self):
        if not self.view:
            return
        try:
            status = self.license_manager.check_current_license()
            info = self.license_manager.current_license
            days = self.license_manager.days_remaining()
            self.view.set_license_status(status, info, days)
            print(f"[FileManager] Licence rafraîchie: {status}")
        except Exception as e:
            print(f"[FileManager] Erreur rafraîchissement licence : {e}")

    # ────────────────────────────────────────────────────────────────
    # LICENCE
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def activate_license(self, key_text: str):
        if not self._require_permission("can_configure_system", "activer une licence"):
            return

        key = (key_text or "").strip()
        if not key:
            InfoDialog.warning(
                self.view, "Cle requise",
                "Veuillez saisir ou charger une cle de licence.",
            )
            return
        try:
            ok = self.license_manager.activate_license(key)
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur", f"Erreur lors de l'activation :\n{e}"
            )
            return

        if ok:
            InfoDialog.success(
                self.view, "Licence activee",
                "La nouvelle licence a ete activee avec succes.",
            )
        else:
            InfoDialog.error(
                self.view, "Licence invalide",
                "Cette cle est invalide, corrompue, ou deja expiree.",
            )
        self._refresh_license_panel()

    # ────────────────────────────────────────────────────────────────
    # PRODUITS
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_products_csv(self, file_path: str):
        if not self._require_permission("can_manage_stock", "importer des produits"):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                InfoDialog.warning(self.view, "Fichier introuvable", str(file_path))
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    InfoDialog.warning(
                        self.view, "CSV vide",
                        "Le fichier est vide ou mal formate.",
                    )
                    return

                cols = self._map_headers(reader.fieldnames, self.PRODUCT_HEADER_MAP)
                if "name" not in cols:
                    InfoDialog.warning(
                        self.view, "Colonne manquante",
                        f"La colonne 'Nom' est obligatoire.\n\n"
                        f"Colonnes trouvees :\n{', '.join(reader.fieldnames)}",
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
                                existing = self.catalog_repo.get_category_by_name(
                                    category_name
                                )
                                category_id = (
                                    existing["id"] if existing
                                    else self.catalog_repo.create_category(category_name)
                                )
                                category_cache[category_name.lower()] = category_id

                        supplier_id = None
                        if supplier_name:
                            supplier_id = supplier_cache.get(supplier_name.lower())
                            if supplier_id is None:
                                match = next(
                                    (
                                        s for s in self.catalog_repo.get_all_suppliers(
                                            active_only=False
                                        )
                                        if s["name"].lower() == supplier_name.lower()
                                    ),
                                    None,
                                )
                                supplier_id = (
                                    match["id"] if match
                                    else self.catalog_repo.create_supplier(supplier_name)
                                )
                                supplier_cache[supplier_name.lower()] = supplier_id

                        is_book_raw = row.get(
                            cols.get("is_book", ""), ""
                        ).strip().lower()
                        is_book = is_book_raw in ("1", "oui", "true", "vrai", "yes")

                        sku = row.get(cols.get("sku", ""), "").strip() or None
                        if sku and self.catalog_repo.sku_exists(sku):
                            existing_product = self.catalog_repo.get_product_by_sku(sku)
                            self.catalog_repo.update_product(
                                existing_product["id"],
                                name=name,
                                description=row.get(
                                    cols.get("description", ""), ""
                                ).strip(),
                                category_id=category_id,
                                supplier_id=supplier_id,
                                buy_price=num("buy_price"),
                                sell_price=num("sell_price"),
                                stock_quantity=integer("stock_quantity"),
                                min_stock_threshold=integer("min_stock_threshold", 10),
                                packaging_type=row.get(
                                    cols.get("packaging_type", ""), "unitaire"
                                ).strip() or "unitaire",
                                units_per_pack=integer("units_per_pack", 1),
                                location=row.get(
                                    cols.get("location", ""), ""
                                ).strip(),
                                tax_rate=num("tax_rate"),
                                is_book=is_book,
                                notes=row.get(cols.get("notes", ""), "").strip(),
                            )
                        else:
                            self.catalog_repo.create_product(
                                name=name,
                                description=row.get(
                                    cols.get("description", ""), ""
                                ).strip(),
                                category_id=category_id,
                                supplier_id=supplier_id,
                                buy_price=num("buy_price"),
                                sell_price=num("sell_price"),
                                stock_quantity=integer("stock_quantity"),
                                min_stock_threshold=integer("min_stock_threshold", 10),
                                packaging_type=row.get(
                                    cols.get("packaging_type", ""), "unitaire"
                                ).strip() or "unitaire",
                                units_per_pack=integer("units_per_pack", 1),
                                location=row.get(
                                    cols.get("location", ""), ""
                                ).strip(),
                                sku=sku,
                                tax_rate=num("tax_rate"),
                                is_book=is_book,
                                notes=row.get(cols.get("notes", ""), "").strip(),
                            )
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("produit(s)", imported, errors)
            self._refresh_all_panels()

        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_products_csv(self, file_path: str):
        try:
            products = self.catalog_repo.get_all_products(active_only=False)
            if not products:
                InfoDialog.info(
                    self.view, "Aucune donnee",
                    "Il n'y a aucun produit a exporter.",
                )
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
                        p.get("location") or "",
                        p.get("packaging_type") or "unitaire",
                        p.get("units_per_pack") or 1,
                        str(p.get("tax_rate") or 0).replace(".", ","),
                        "Oui" if p.get("is_book") else "Non",
                        p.get("notes") or "",
                    ])

            self._report_export(path, len(products), "produit(s)")
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'export", str(e))

    def generate_products_template(self, file_path: str):
        if not self._require_permission(
            "can_manage_stock", "telecharger un modele d'import"
        ):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.PRODUCT_COLUMNS_FR)
            writer.writerow([
                "Stylo Bic", "Stylo a bille bleu", "Papeterie", "Fournisseur ABC",
                "STY-001", "150", "250", "100", "10", "Rayon A2",
                "unitaire", "1", "19,25", "Non", "",
            ])
            writer.writerow([
                "Dictionnaire Larousse", "Edition 2024", "Manuels Scolaires", "",
                "DIC-002", "3000", "5000", "20", "5", "Rayon B1",
                "unitaire", "1", "0", "Oui", "",
            ])
        InfoDialog.success(
            self.view, "Modele cree",
            f"Modele produits cree :\n{path.absolute()}",
        )

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
                InfoDialog.warning(self.view, "Fichier introuvable", str(file_path))
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    InfoDialog.warning(
                        self.view, "CSV vide",
                        "Le fichier est vide ou mal formate.",
                    )
                    return
                cols = self._map_headers(reader.fieldnames, self.SUPPLIER_HEADER_MAP)
                if "name" not in cols:
                    InfoDialog.warning(
                        self.view, "Colonne manquante",
                        "La colonne 'Nom' est obligatoire.",
                    )
                    return

                existing_suppliers = {
                    s["name"].lower(): s
                    for s in self.catalog_repo.get_all_suppliers(active_only=False)
                }

                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get(cols.get("name", ""), "").strip()
                        if not name:
                            errors.append(f"Ligne {row_num} : nom manquant")
                            continue

                        fields = dict(
                            contact_name=row.get(
                                cols.get("contact_name", ""), ""
                            ).strip(),
                            email=row.get(cols.get("email", ""), "").strip(),
                            phone=row.get(cols.get("phone", ""), "").strip(),
                            phone2=row.get(cols.get("phone2", ""), "").strip(),
                            address=row.get(cols.get("address", ""), "").strip(),
                            city=row.get(cols.get("city", ""), "").strip(),
                            payment_terms=row.get(
                                cols.get("payment_terms", ""), ""
                            ).strip(),
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
            InfoDialog.error(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_suppliers_csv(self, file_path: str):
        try:
            suppliers = self.catalog_repo.get_all_suppliers(active_only=False)
            if not suppliers:
                InfoDialog.info(
                    self.view, "Aucune donnee",
                    "Il n'y a aucun fournisseur a exporter.",
                )
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
                        s.get("phone") or "", s.get("phone2") or "",
                        s.get("address") or "", s.get("city") or "",
                        s.get("payment_terms") or "", s.get("notes") or "",
                    ])
            self._report_export(path, len(suppliers), "fournisseur(s)")
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'export", str(e))

    def generate_suppliers_template(self, file_path: str):
        if not self._require_permission(
            "can_manage_stock", "telecharger un modele d'import"
        ):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.SUPPLIER_COLUMNS_FR)
            writer.writerow([
                "Fournisseur ABC", "Jean Dupont", "contact@abc.cm", "699000000",
                "", "Rue du Marche", "Bafoussam", "30 jours", "",
            ])
        InfoDialog.success(
            self.view, "Modele cree",
            f"Modele fournisseurs cree :\n{path.absolute()}",
        )

    # ────────────────────────────────────────────────────────────────
    # CATÉGORIES
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_categories_csv(self, file_path: str):
        if not self._require_permission("can_manage_stock", "importer des categories"):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                InfoDialog.warning(self.view, "Fichier introuvable", str(file_path))
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    InfoDialog.warning(
                        self.view, "CSV vide",
                        "Le fichier est vide ou mal formate.",
                    )
                    return
                cols = self._map_headers(reader.fieldnames, self.CATEGORY_HEADER_MAP)
                if "name" not in cols:
                    InfoDialog.warning(
                        self.view, "Colonne manquante",
                        "La colonne 'Nom' est obligatoire.",
                    )
                    return

                name_to_id = {
                    c["name"].lower(): c["id"]
                    for c in self.catalog_repo.get_all_categories(active_only=False)
                }

                for row_num, row in enumerate(reader, start=2):
                    try:
                        name = row.get(cols.get("name", ""), "").strip()
                        if not name:
                            errors.append(f"Ligne {row_num} : nom manquant")
                            continue
                        parent_name = row.get(
                            cols.get("parent_name", ""), ""
                        ).strip()
                        parent_id = (
                            name_to_id.get(parent_name.lower()) if parent_name else None
                        )

                        sort_order_raw = row.get(
                            cols.get("sort_order", ""), "0"
                        ).strip()
                        sort_order = int(sort_order_raw) if sort_order_raw else 0

                        if name.lower() in name_to_id:
                            self.catalog_repo.update_category(
                                name_to_id[name.lower()],
                                parent_id=parent_id,
                                description=row.get(
                                    cols.get("description", ""), ""
                                ).strip(),
                                icon=row.get(cols.get("icon", ""), "").strip(),
                                color=row.get(cols.get("color", ""), "").strip(),
                                sort_order=sort_order,
                            )
                        else:
                            new_id = self.catalog_repo.create_category(
                                name=name,
                                parent_id=parent_id,
                                description=row.get(
                                    cols.get("description", ""), ""
                                ).strip(),
                                icon=row.get(cols.get("icon", ""), "").strip(),
                                color=row.get(cols.get("color", ""), "").strip(),
                                sort_order=sort_order,
                            )
                            name_to_id[name.lower()] = new_id
                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("categorie(s)", imported, errors)
            self._refresh_all_panels()
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_categories_csv(self, file_path: str):
        try:
            categories = self.catalog_repo.get_all_categories(active_only=False)
            if not categories:
                InfoDialog.info(
                    self.view, "Aucune donnee",
                    "Il n'y a aucune categorie a exporter.",
                )
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
            self._report_export(path, len(categories), "categorie(s)")
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'export", str(e))

    def generate_categories_template(self, file_path: str):
        if not self._require_permission(
            "can_manage_stock", "telecharger un modele d'import"
        ):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.CATEGORY_COLUMNS_FR)
            writer.writerow([
                "Cahiers", "Papeterie", "Tous formats de cahiers", "", "", "1",
            ])
        InfoDialog.success(
            self.view, "Modele cree",
            f"Modele categories cree :\n{path.absolute()}",
        )

    # ────────────────────────────────────────────────────────────────
    # UTILISATEURS
    #
    # IMPORTANT : reservé à can_manage_users (rôle admin/gérant), comme
    # l'export existant. La création d'un compte exige un mot de passe
    # et un self.auth_manager valide pour le hacher — si ce dernier est
    # absent, l'import échoue proprement ligne par ligne plutôt que de
    # stocker un mot de passe en clair ou planter.
    # ────────────────────────────────────────────────────────────────

    @Slot(str)
    def import_users_csv(self, file_path: str):
        if not self._require_permission(
            "can_manage_users", "importer des utilisateurs"
        ):
            return
        try:
            path = Path(file_path)
            if not path.exists():
                InfoDialog.warning(self.view, "Fichier introuvable", str(file_path))
                return

            imported, errors = 0, []
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                if not reader.fieldnames:
                    InfoDialog.warning(
                        self.view, "CSV vide",
                        "Le fichier est vide ou mal formate.",
                    )
                    return

                cols = self._map_headers(reader.fieldnames, self.USER_HEADER_MAP)
                if "username" not in cols:
                    InfoDialog.warning(
                        self.view, "Colonne manquante",
                        f"La colonne 'Nom d'utilisateur' est obligatoire.\n\n"
                        f"Colonnes trouvees :\n{', '.join(reader.fieldnames)}",
                    )
                    return

                existing_users = {
                    u["username"].lower(): u for u in self.user_repo.get_all_users()
                }
                roles_by_name = {
                    r["name"].lower(): r for r in self.user_repo.get_all_roles()
                }

                for row_num, row in enumerate(reader, start=2):
                    try:
                        username = row.get(cols.get("username", ""), "").strip()
                        if not username:
                            errors.append(f"Ligne {row_num} : nom d'utilisateur manquant")
                            continue

                        full_name = row.get(cols.get("full_name", ""), "").strip()
                        email = row.get(cols.get("email", ""), "").strip()
                        phone = row.get(cols.get("phone", ""), "").strip()
                        password = row.get(cols.get("password", ""), "").strip()

                        role_name = row.get(cols.get("role", ""), "").strip()
                        role = roles_by_name.get(role_name.lower()) if role_name else None
                        if role_name and not role:
                            errors.append(
                                f"Ligne {row_num} : role '{role_name}' inconnu"
                            )
                            continue

                        active_raw = row.get(
                            cols.get("is_active", ""), ""
                        ).strip().lower()
                        # Cellule vide -> actif par defaut (comportement le
                        # moins surprenant pour un import en masse).
                        is_active = active_raw in (
                            "1", "oui", "true", "vrai", "yes", ""
                        )

                        existing = existing_users.get(username.lower())

                        if existing:
                            if self.user_repo.username_exists(
                                username, exclude_id=existing["id"]
                            ):
                                errors.append(
                                    f"Ligne {row_num} : nom d'utilisateur "
                                    f"'{username}' en conflit"
                                )
                                continue

                            fields = {
                                "full_name": full_name,
                                "email": email,
                                "is_active": 1 if is_active else 0,
                            }
                            if role:
                                fields["role_id"] = role["id"]
                            if password:
                                if not self.auth_manager:
                                    errors.append(
                                        f"Ligne {row_num} : mot de passe fourni "
                                        f"pour '{username}' mais aucun "
                                        f"gestionnaire d'authentification "
                                        f"disponible — mot de passe ignore"
                                    )
                                else:
                                    fields["password_hash"] = (
                                        self.auth_manager.hash_password(password)
                                    )
                            self.user_repo.update_user(existing["id"], **fields)
                        else:
                            if not password:
                                errors.append(
                                    f"Ligne {row_num} : mot de passe obligatoire "
                                    f"pour creer '{username}'"
                                )
                                continue
                            if not self.auth_manager:
                                errors.append(
                                    f"Ligne {row_num} : gestionnaire "
                                    f"d'authentification indisponible, "
                                    f"impossible de creer '{username}'"
                                )
                                continue
                            if self.user_repo.username_exists(username):
                                errors.append(
                                    f"Ligne {row_num} : '{username}' existe deja"
                                )
                                continue

                            password_hash = self.auth_manager.hash_password(password)
                            new_id = self.user_repo.create_user(
                                username=username,
                                password_hash=password_hash,
                                role_id=role["id"] if role else None,
                                full_name=full_name,
                                email=email,
                            )
                            if not is_active:
                                self.user_repo.set_active(new_id, False)
                            existing_users[username.lower()] = {"id": new_id}

                        imported += 1
                    except Exception as e:
                        errors.append(f"Ligne {row_num} : {e}")

            self._report_result("utilisateur(s)", imported, errors)
            self._refresh_all_panels()

            if self.current_user:
                self.user_repo.log_audit(
                    self.current_user.id, "IMPORT_USERS", "user", None,
                    description=f"Import CSV : {imported} utilisateur(s), "
                                f"{len(errors)} erreur(s) — fichier {path.name}",
                )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'import", str(e))

    @Slot(str)
    def export_users_csv(self, file_path: str):
        if not self._require_permission(
            "can_manage_users", "exporter la liste des utilisateurs"
        ):
            return
        try:
            users = self.user_repo.get_all_users()
            if not users:
                InfoDialog.info(
                    self.view, "Aucune donnee",
                    "Il n'y a aucun utilisateur a exporter.",
                )
                return
            path = Path(file_path)
            if not path.suffix:
                path = path.with_suffix(".csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Nom d'utilisateur", "Nom complet", "Email", "Telephone",
                    "Role", "Actif", "Derniere connexion",
                ])
                for u in users:
                    writer.writerow([
                        u["username"], u.get("full_name") or "",
                        u.get("email") or "", u.get("phone") or "",
                        u.get("role_name") or "",
                        "Oui" if u.get("is_active") else "Non",
                        u.get("last_login_at") or "",
                    ])
            self._report_export(path, len(users), "utilisateur(s)")
            InfoDialog.info(
                self.view, "Rappel securite",
                "Cet export ne contient jamais les mots de passe (haches ou non).",
            )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur d'export", str(e))

    def generate_users_template(self, file_path: str):
        if not self._require_permission(
            "can_manage_users", "telecharger un modele d'import"
        ):
            return
        path = Path(file_path)
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(self.USER_COLUMNS_FR)
            writer.writerow([
                "jdupont", "Jean Dupont", "jdupont@example.cm", "699000000",
                "employe", "MotDePasse123", "Oui",
            ])
        InfoDialog.success(
            self.view, "Modele cree",
            f"Modele utilisateurs cree :\n{path.absolute()}\n\n"
            "Rappel : le mot de passe n'est requis que pour creer un "
            "nouveau compte ; laissez-le vide pour ne pas modifier le "
            "mot de passe d'un utilisateur existant.",
        )

    # ────────────────────────────────────────────────────────────────
    # SAUVEGARDE / RESTAURATION
    #
    # IMPORTANT : ce bloc ne fait plus AUCUN shutil.copy2 pour créer un
    # backup — c'est le rôle exclusif de self.backup_service. Ici, on ne
    # fait que : (a) demander un backup au service, (b) gérer l'UI, et
    # (c) pour la restauration, copier un backup EXISTANT vers la BDD
    # active — ce qui est une opération différente (restaurer, pas
    # sauvegarder), donc légitimement câblée ici avec shutil.
    # ────────────────────────────────────────────────────────────────

    @Slot()
    def create_backup(self):
        try:
            backup_path = self.backup_service.create_backup(prefix="sauvegarde")
            # Rétention : purge les vieux backups (>7 jours), en garde toujours 3 minimum.
            self.backup_service.cleanup_old_backups(retain_days=7, keep_minimum=3)
            self._refresh_backups_list()
            size_kb = backup_path.stat().st_size / 1024
            InfoDialog.success(
                self.view, "Sauvegarde creee",
                f"Fichier : {backup_path.name}\nTaille : {size_kb:.1f} KB",
            )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur", str(e))

    @Slot(str)
    def restore_backup(self, backup_path: str):
        if not self._require_permission(
            "can_configure_system", "restaurer une sauvegarde"
        ):
            return
        try:
            path = Path(backup_path)
            if not path.exists():
                InfoDialog.warning(self.view, "Fichier introuvable", str(backup_path))
                return

            ok = InfoDialog.question(
                self.view,
                "Confirmer la restauration",
                f"Cette action remplacera la base de donnees actuelle par :\n"
                f"{path.name}\n\n"
                "Une sauvegarde automatique de securite sera creee avant. Continuer ?",
                ok_text="Yes",
                cancel_text="No",
            )
            if not ok:
                return

            # Filet de sécurité avant restauration : on passe par le service,
            # comme tout autre backup, pour rester dans le même dossier unique.
            if self.db_path.exists():
                self.backup_service.create_backup(prefix="avant_restauration")

            # Ici, on restaure : on copie un backup EXISTANT par-dessus la BDD
            # active. C'est l'opération inverse d'un backup, donc ce
            # shutil.copy2 reste ici — ce n'est pas une logique dupliquée.
            shutil.copy2(str(path), str(self.db_path))

            if self.current_user:
                self.user_repo.log_audit(
                    self.current_user.id, "RESTORE_DB", "database", None,
                    description=f"Restauration depuis {path.name}",
                )

            InfoDialog.success(
                self.view, "Restauration reussie",
                f"Base restauree depuis {path.name}.\nRedemarrez l'application.",
            )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur", str(e))

    @Slot(str)
    def delete_backup(self, backup_path: str):
        if not self._require_permission(
            "can_configure_system", "supprimer une sauvegarde"
        ):
            return
        try:
            path = Path(backup_path)
            ok = InfoDialog.question(
                self.view,
                "Supprimer la sauvegarde",
                f"Supprimer definitivement {path.name} ?",
                ok_text="Yes",
                cancel_text="No",
            )
            if not ok:
                return
            self.backup_service.delete_backup(backup_path)
            self._refresh_backups_list()
            InfoDialog.success(
                self.view, "Sauvegarde supprimee",
                f"{path.name} a ete supprime.",
            )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur", str(e))

    # ────────────────────────────────────────────────────────────────
    # HELPERS
    # ────────────────────────────────────────────────────────────────

    def _report_result(self, label: str, imported: int, errors: list):
        msg = f"Import termine.\n\n{imported} {label} traite(s) avec succes."
        if errors:
            msg += f"\n\n{len(errors)} erreur(s) :\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n... et {len(errors) - 10} autre(s)."
            InfoDialog.warning(self.view, "Import partiel", msg)
        else:
            InfoDialog.success(self.view, "Import reussi", msg)

    def _report_export(self, path: Path, count: int, label: str):
        size_kb = path.stat().st_size / 1024
        InfoDialog.success(
            self.view, "Export reussi",
            f"{count} {label} exporte(s).\n\n"
            f"Fichier : {path.name}\nTaille : {size_kb:.1f} KB",
        )

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(
                f"[FileManager] Theme applique: "
                f"{'dark' if is_dark else 'light'}"
            )