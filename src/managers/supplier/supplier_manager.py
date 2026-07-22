"""
Manager des fournisseurs — connecté à CatalogRepository (table suppliers réelle).
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt
from PySide6.QtWidgets import QMessageBox, QWidget, QFormLayout, QLineEdit, QLabel, QTextEdit

from src.database.repositories.catalog_repository import CatalogRepository


class SupplierTableModel(QAbstractTableModel):

    HEADERS = ["ID", "Nom", "Contact", "Téléphone", "Email", "Ville", "Actif"]

    def __init__(self, suppliers: list):
        super().__init__()
        self._suppliers = suppliers

    def rowCount(self, parent=None):
        return len(self._suppliers)

    def columnCount(self, parent=None):
        return len(self.HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        s = self._suppliers[index.row()]
        if role == Qt.DisplayRole:
            values = [str(s["id"]), s["name"], s.get("contact_name") or "—",
                      s.get("phone") or "—", s.get("email") or "—",
                      s.get("city") or "—", "Oui" if s["is_active"] else "Non"]
            return values[index.column()]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignLeft
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_supplier(self, row):
        return self._suppliers[row] if 0 <= row < len(self._suppliers) else None

    def set_suppliers(self, suppliers):
        self.beginResetModel()
        self._suppliers = suppliers
        self.endResetModel()


class SupplierManager(QObject):

    version = "2.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.catalog = CatalogRepository()

        self.suppliers = self.catalog.get_all_suppliers()
        self.model = SupplierTableModel(self.suppliers)

        print(f"[SupplierManager v{self.version}] Initialisé avec {len(self.suppliers)} fournisseurs")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.supplier_view import SupplierView
            self.view = SupplierView(self.parent)
            self._connect_signals()
            self.view.set_table_model(self.model)
        return self.view

    def _connect_signals(self):
        self.view.search_requested.connect(self.on_search)
        self.view.add_supplier_requested.connect(self.add_supplier)
        self.view.edit_supplier_requested.connect(self.edit_supplier)
        self.view.delete_supplier_requested.connect(self.delete_supplier)
        self.view.refresh_requested.connect(self.refresh)

    def _create_supplier_form(self, supplier=None):
        from src.ui.widgets.ModalView import ModalView

        is_edit = supplier is not None
        modal = ModalView(
            title="Modifier le fournisseur" if is_edit else "Nouveau fournisseur",
            parent=self.view, width=680, height=580,
            ok_text="Enregistrer", cancel_text="Annuler"
        )

        content = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(16)

        inp_s = "font-size: 14px; padding: 8px; border: 2px solid #bdc3c7; border-radius: 8px; min-height: 36px;"

        def lbl(t):
            l = QLabel(t)
            return l

        name_input = QLineEdit(supplier["name"] if is_edit else "")
        contact_input = QLineEdit(supplier.get("contact_name", "") if is_edit else "")
        phone_input = QLineEdit(supplier.get("phone", "") if is_edit else "")
        phone2_input = QLineEdit(supplier.get("phone2", "") if is_edit else "")
        email_input = QLineEdit(supplier.get("email", "") if is_edit else "")
        city_input = QLineEdit(supplier.get("city", "") if is_edit else "")
        address_input = QLineEdit(supplier.get("address", "") if is_edit else "")
        terms_input = QLineEdit(supplier.get("payment_terms", "") if is_edit else "")
        notes_input = QTextEdit(supplier.get("notes", "") if is_edit else "")
        notes_input.setMaximumHeight(70)

        for w in [name_input, contact_input, phone_input, phone2_input,
                  email_input, city_input, address_input, terms_input]:
            w.setStyleSheet(inp_s)
        notes_input.setStyleSheet(inp_s)

        form_layout.addRow(lbl("Nom *:"), name_input)
        form_layout.addRow(lbl("Contact:"), contact_input)
        form_layout.addRow(lbl("Téléphone:"), phone_input)
        form_layout.addRow(lbl("Téléphone 2:"), phone2_input)
        form_layout.addRow(lbl("Email:"), email_input)
        form_layout.addRow(lbl("Ville:"), city_input)
        form_layout.addRow(lbl("Adresse:"), address_input)
        form_layout.addRow(lbl("Conditions de paiement:"), terms_input)
        form_layout.addRow(lbl("Notes:"), notes_input)

        content.setLayout(form_layout)
        modal.set_content(content)

        modal.name_input = name_input
        modal.contact_input = contact_input
        modal.phone_input = phone_input
        modal.phone2_input = phone2_input
        modal.email_input = email_input
        modal.city_input = city_input
        modal.address_input = address_input
        modal.terms_input = terms_input
        modal.notes_input = notes_input

        return modal

    @Slot(str)
    def on_search(self, text: str):
        text = text.strip().lower()
        all_suppliers = self.catalog.get_all_suppliers()
        if text:
            all_suppliers = [s for s in all_suppliers if text in s["name"].lower()]
        self.suppliers = all_suppliers
        self.model.set_suppliers(self.suppliers)

    @Slot()
    def add_supplier(self):
        modal = self._create_supplier_form()

        def on_save():
            name = modal.name_input.text().strip()
            if not name:
                QMessageBox.warning(self.view, "Validation", "Le nom est obligatoire.")
                return

            self.catalog.create_supplier(
                name=name, contact_name=modal.contact_input.text().strip() or None,
                email=modal.email_input.text().strip() or None,
                phone=modal.phone_input.text().strip() or None,
                phone2=modal.phone2_input.text().strip() or None,
                address=modal.address_input.text().strip() or None,
                city=modal.city_input.text().strip() or None,
                payment_terms=modal.terms_input.text().strip() or None,
                notes=modal.notes_input.toPlainText().strip() or None,
            )
            self.refresh()
            modal.accept()
            QMessageBox.information(self.view, "Succès", f"Fournisseur '{name}' ajouté.")

        modal.ok_clicked.connect(on_save)
        modal.exec()

    @Slot(int)
    def edit_supplier(self, row: int):
        supplier = self.model.get_supplier(row)
        if not supplier:
            QMessageBox.warning(self.view, "Sélection requise", "Sélectionnez un fournisseur.")
            return

        modal = self._create_supplier_form(supplier)

        def on_save():
            name = modal.name_input.text().strip()
            if not name:
                QMessageBox.warning(self.view, "Validation", "Le nom est obligatoire.")
                return

            self.catalog.update_supplier(
                supplier["id"], name=name,
                contact_name=modal.contact_input.text().strip() or None,
                email=modal.email_input.text().strip() or None,
                phone=modal.phone_input.text().strip() or None,
                phone2=modal.phone2_input.text().strip() or None,
                address=modal.address_input.text().strip() or None,
                city=modal.city_input.text().strip() or None,
                payment_terms=modal.terms_input.text().strip() or None,
                notes=modal.notes_input.toPlainText().strip() or None,
            )
            self.refresh()
            modal.accept()
            QMessageBox.information(self.view, "Succès", f"Fournisseur '{name}' mis à jour.")

        modal.ok_clicked.connect(on_save)
        modal.exec()

    @Slot(int)
    def delete_supplier(self, row: int):
        supplier = self.model.get_supplier(row)
        if not supplier:
            return
        reply = QMessageBox.question(
            self.view, "Confirmation",
            f"Désactiver '{supplier['name']}' ?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.catalog.set_supplier_active(supplier["id"], False)
            self.refresh()
            QMessageBox.information(self.view, "Succès", "Fournisseur désactivé.")

    @Slot()
    def refresh(self):
        self.suppliers = self.catalog.get_all_suppliers()
        self.model.set_suppliers(self.suppliers)