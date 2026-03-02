"""
Manager de gestion des fournisseurs - Logique métier uniquement.
Utilise ModalView générique pour tous les dialogues.
Architecture MVC pure.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox, QWidget, QFormLayout, QLineEdit, QLabel, QTextEdit
from datetime import datetime


class Supplier:
    """Modèle de données pour un fournisseur."""
    def __init__(self, supplier_id=None, name="", contact="", phone="",
                 email="", address="", notes="", created_at=None):
        self.id         = supplier_id
        self.name       = name
        self.contact    = contact   # Nom du contact principal
        self.phone      = phone
        self.email      = email
        self.address    = address
        self.notes      = notes
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        return {
            'id':         self.id,
            'name':       self.name,
            'contact':    self.contact,
            'phone':      self.phone,
            'email':      self.email,
            'address':    self.address,
            'notes':      self.notes,
            'created_at': self.created_at,
        }


class SupplierTableModel(QAbstractTableModel):
    """Modèle de table pour les fournisseurs."""

    HEADERS = ["ID", "Nom", "Contact", "Téléphone", "Email", "Adresse", "Date création"]

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
        col = index.column()
        if role == Qt.DisplayRole:
            return [str(s.id), s.name, s.contact, s.phone,
                    s.email, s.address, s.created_at][col]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignLeft
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def get_supplier(self, row):
        return self._suppliers[row] if 0 <= row < len(self._suppliers) else None

    def add_supplier(self, supplier):
        self.beginInsertRows(QModelIndex(), len(self._suppliers), len(self._suppliers))
        self._suppliers.append(supplier)
        self.endInsertRows()

    def update_supplier(self, row, supplier):
        if 0 <= row < len(self._suppliers):
            self._suppliers[row] = supplier
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))
            return True
        return False

    def remove_supplier(self, row):
        if 0 <= row < len(self._suppliers):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._suppliers[row]
            self.endRemoveRows()
            return True
        return False

    def filter_suppliers(self, text: str):
        self.layoutChanged.emit()


class SupplierManager(QObject):
    """Manager de gestion des fournisseurs."""

    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view   = None

        self.suppliers = self._load_sample_suppliers()
        self.model     = SupplierTableModel(self.suppliers)

        print(f"[SupplierManager v{self.version}] Initialisé avec {len(self.suppliers)} fournisseurs")

    def _load_sample_suppliers(self):
        return [
            Supplier(1, "Papeterie Centrale", "Jean Fotso",  "+237 699 123 456",
                     "papeterie@centrale.cm", "Rue 1234, Yaoundé", "Fournisseur principal", "2024-01-10"),
            Supplier(2, "Librairie du Peuple", "Marie Ngo",  "+237 677 987 654",
                     "contact@libpeuple.cm",  "Avenue Kennedy, Douala", "", "2024-03-15"),
            Supplier(3, "Imports Express",    "Paul Kamga",  "+237 655 321 789",
                     "imports@express.cm",    "Quartier Bastos, Yaoundé", "Livraison rapide", "2024-06-01"),
        ]

    def get_ui(self):
        if self.view is None:
            from src.ui.views.supplier_view import SupplierView
            self.view = SupplierView(self.parent)
            self._connect_signals()
            self.view.set_table_model(self.model)
            print("[SupplierManager] Vue créée et initialisée")
        return self.view

    def _connect_signals(self):
        self.view.search_requested.connect(self.on_search)
        self.view.add_supplier_requested.connect(self.add_supplier)
        self.view.edit_supplier_requested.connect(self.edit_supplier)
        self.view.delete_supplier_requested.connect(self.delete_supplier)
        self.view.refresh_requested.connect(self.refresh)

    # ──────────────────────────────────────────────────────────────────
    # FORMULAIRE FOURNISSEUR avec ModalView générique
    # ──────────────────────────────────────────────────────────────────

    def _create_supplier_form(self, supplier=None):
        from src.ui.widgets.ModalView import ModalView

        is_edit = supplier is not None
        modal = ModalView(
            title="Modifier le fournisseur" if is_edit else "Nouveau fournisseur",
            parent=self.view,
            width=680,
            height=580,
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )

        content    = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setContentsMargins(0, 0, 0, 0)

        lbl_s = "font-size: 14px; color: palette(text);"
        inp_s = """
            QLineEdit, QTextEdit {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                min-height: 38px;
            }
            QLineEdit:focus, QTextEdit:focus { border-color: #16a085; }
        """

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(lbl_s)
            return l

        name_input    = QLineEdit(supplier.name    if is_edit else "")
        contact_input = QLineEdit(supplier.contact if is_edit else "")
        phone_input   = QLineEdit(supplier.phone   if is_edit else "")
        email_input   = QLineEdit(supplier.email   if is_edit else "")
        address_input = QLineEdit(supplier.address if is_edit else "")
        notes_input   = QTextEdit (supplier.notes  if is_edit else "")
        notes_input.setMaximumHeight(80)

        for w in [name_input, contact_input, phone_input, email_input, address_input]:
            w.setStyleSheet(inp_s)
        notes_input.setStyleSheet(inp_s)

        name_input.setPlaceholderText("Nom du fournisseur *")
        contact_input.setPlaceholderText("Nom du contact principal")
        phone_input.setPlaceholderText("+237 6XX XXX XXX")
        email_input.setPlaceholderText("email@fournisseur.cm")
        address_input.setPlaceholderText("Adresse complète")
        notes_input.setPlaceholderText("Notes optionnelles...")

        form_layout.addRow(lbl("Nom *:"),      name_input)
        form_layout.addRow(lbl("Contact:"),    contact_input)
        form_layout.addRow(lbl("Téléphone:"),  phone_input)
        form_layout.addRow(lbl("Email:"),      email_input)
        form_layout.addRow(lbl("Adresse:"),    address_input)
        form_layout.addRow(lbl("Notes:"),      notes_input)

        content.setLayout(form_layout)
        modal.set_content(content)

        # Stocker les widgets pour récupération
        modal.name_input    = name_input
        modal.contact_input = contact_input
        modal.phone_input   = phone_input
        modal.email_input   = email_input
        modal.address_input = address_input
        modal.notes_input   = notes_input

        return modal

    # ──────────────────────────────────────────────────────────────────
    # SLOTS
    # ──────────────────────────────────────────────────────────────────

    @Slot(str)
    def on_search(self, text: str):
        self.model.filter_suppliers(text)

    @Slot()
    def add_supplier(self):
        modal = self._create_supplier_form()

        def on_save():
            name = modal.name_input.text().strip()
            if not name:
                QMessageBox.warning(self.view, "Validation", "Le nom du fournisseur est obligatoire.")
                return

            new_id = max((s.id for s in self.suppliers), default=0) + 1
            new_sup = Supplier(
                supplier_id = new_id,
                name        = name,
                contact     = modal.contact_input.text().strip(),
                phone       = modal.phone_input.text().strip(),
                email       = modal.email_input.text().strip(),
                address     = modal.address_input.text().strip(),
                notes       = modal.notes_input.toPlainText().strip(),
            )
            self.suppliers.append(new_sup)
            self.model.add_supplier(new_sup)
            modal.accept()
            QMessageBox.information(self.view, "Succès", f"Fournisseur '{name}' ajouté.")
            print(f"[SupplierManager] Fournisseur ajouté: ID {new_id}")

        modal.ok_clicked.connect(on_save)
        modal.exec()

    @Slot(int)
    def edit_supplier(self, row: int):
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un fournisseur à modifier.")
            return

        supplier = self.model.get_supplier(row)
        if not supplier:
            return

        modal = self._create_supplier_form(supplier)

        def on_save():
            name = modal.name_input.text().strip()
            if not name:
                QMessageBox.warning(self.view, "Validation", "Le nom est obligatoire.")
                return

            supplier.name    = name
            supplier.contact = modal.contact_input.text().strip()
            supplier.phone   = modal.phone_input.text().strip()
            supplier.email   = modal.email_input.text().strip()
            supplier.address = modal.address_input.text().strip()
            supplier.notes   = modal.notes_input.toPlainText().strip()

            self.model.update_supplier(row, supplier)
            modal.accept()
            QMessageBox.information(self.view, "Succès", f"Fournisseur '{name}' mis à jour.")
            print(f"[SupplierManager] Fournisseur modifié: ID {supplier.id}")

        modal.ok_clicked.connect(on_save)
        modal.exec()

    @Slot(int)
    def delete_supplier(self, row: int):
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(self.view, "Sélection requise",
                                "Veuillez sélectionner un fournisseur à supprimer.")
            return

        supplier = self.model.get_supplier(row)
        if not supplier:
            return

        reply = QMessageBox.question(
            self.view, "Confirmation",
            f"Supprimer le fournisseur '{supplier.name}' ?\n\nCette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.model.remove_supplier(row)
            QMessageBox.information(self.view, "Succès",
                                    f"Fournisseur '{supplier.name}' supprimé.")
            print(f"[SupplierManager] Fournisseur supprimé: ID {supplier.id}")

    @Slot()
    def refresh(self):
        self.model.layoutChanged.emit()
        print("[SupplierManager] Vue rafraîchie")