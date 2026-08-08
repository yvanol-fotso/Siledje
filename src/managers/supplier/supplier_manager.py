"""
Manager fournisseurs — CatalogRepository + InfoDialog.
"""

from PySide6.QtCore import QObject, Slot

from src.database.repositories.catalog_repository import CatalogRepository
from src.ui.views.supplier.supplier_form import SupplierForm
from src.ui.widgets.ModalView import ModalView
from src.ui.widgets.InfoDialog import InfoDialog


class SupplierManager(QObject):
    version = "3.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.catalog = CatalogRepository()
        self.suppliers = self.catalog.get_all_suppliers()
        print(
            f"[SupplierManager v{self.version}] Initialise avec "
            f"{len(self.suppliers)} fournisseurs"
        )

    def get_ui(self):
        if self.view is None:
            from src.ui.views.supplier.supplier_view import SupplierView

            self.view = SupplierView(self.parent)
            self._connect_signals()
            self.view.update_suppliers(self.suppliers)
            print("[SupplierManager] Vue creee et initialisee")
        return self.view

    def _connect_signals(self):
        self.view.search_requested.connect(self.on_search)
        self.view.add_supplier_requested.connect(self.add_supplier)
        self.view.edit_supplier_requested.connect(self.edit_supplier)
        self.view.delete_supplier_requested.connect(self.delete_supplier)
        self.view.refresh_requested.connect(self.refresh)

    @Slot(str)
    def on_search(self, text: str):
        text = text.strip().lower()
        all_suppliers = self.catalog.get_all_suppliers()
        if text:
            all_suppliers = [
                s for s in all_suppliers if text in s["name"].lower()
            ]
        self.suppliers = all_suppliers
        self.view.update_suppliers(self.suppliers)
        print(
            f"[SupplierManager] Recherche: {len(all_suppliers)} fournisseurs"
        )

    @Slot()
    def add_supplier(self):
        try:
            form = SupplierForm()
            modal = ModalView(
                title="Nouveau fournisseur",
                parent=self.view,
                width=680,
                height=580,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return
                data = form.get_data()
                self.catalog.create_supplier(**data)
                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"Fournisseur '{data['name']}' ajoute.",
                )
                print(f"[SupplierManager] Cree: {data['name']}")

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur", f"Erreur lors de l'ajout:\n{e}"
            )
            print(f"[SupplierManager] ERREUR ajout: {e}")

    @Slot(int)
    def edit_supplier(self, row: int):
        if row < 0 or row >= len(self.suppliers):
            InfoDialog.warning(
                self.view, "Selection requise",
                "Selectionnez un fournisseur.",
            )
            return
        supplier = self.suppliers[row]
        try:
            form = SupplierForm(supplier)
            modal = ModalView(
                title="Modifier le fournisseur",
                parent=self.view,
                width=680,
                height=580,
                ok_text="Enregistrer",
                cancel_text="Annuler",
            )
            modal.set_content(form)

            def on_save():
                valid, msg = form.validate()
                if not valid:
                    InfoDialog.warning(self.view, "Validation", msg)
                    return
                data = form.get_data()
                self.catalog.update_supplier(supplier["id"], **data)
                self.refresh()
                modal.accept()
                InfoDialog.success(
                    self.view, "Succes",
                    f"Fournisseur '{data['name']}' mis a jour.",
                )
                print(
                    f"[SupplierManager] Modifie: ID {supplier['id']}"
                )

            modal.ok_clicked.connect(on_save)
            modal.exec()
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la modification:\n{e}",
            )
            print(f"[SupplierManager] ERREUR modification: {e}")

    @Slot(int)
    def delete_supplier(self, row: int):
        if row < 0 or row >= len(self.suppliers):
            return
        supplier = self.suppliers[row]
        ok = InfoDialog.question(
            self.view,
            "Confirmation",
            f"Desactiver '{supplier['name']}' ?\n\n"
            "Le fournisseur sera desactive mais son historique sera conserve.",
            ok_text="Yes",
            cancel_text="No",
        )
        if not ok:
            return
        try:
            self.catalog.set_supplier_active(supplier["id"], False)
            self.refresh()
            InfoDialog.success(
                self.view, "Succes", "Fournisseur desactive."
            )
            print(
                f"[SupplierManager] Desactive: ID {supplier['id']}"
            )
        except Exception as e:
            InfoDialog.error(
                self.view, "Erreur",
                f"Erreur lors de la suppression:\n{e}",
            )

    @Slot()
    def refresh(self):
        self.suppliers = self.catalog.get_all_suppliers()
        if self.view:
            self.view.update_suppliers(self.suppliers)
        print(
            f"[SupplierManager] Rafraichi: {len(self.suppliers)} fournisseurs"
        )

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(
                f"[SupplierManager] Theme: "
                f"{'dark' if is_dark else 'light'}"
            )