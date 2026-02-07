"""
Manager de la gestion du stock - CORRIGÉ avec TOUS les champs.
Inclut: Description, Emplacement, Niveau, Langue
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex, QDate
from PySide6.QtWidgets import QMessageBox, QDialog, QWidget, QFormLayout, QLineEdit, QComboBox, QSpinBox, QLabel
from data.dummy_data.data_dummy_stock import dummy_stock_data, stock_headers


class StockTableModel(QAbstractTableModel):
    """Modèle de données pour le tableau de stock."""
    
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None
    
    def get_row_data(self, row):
        """Retourne les données d'une ligne."""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None
    
    def add_row(self, row_data):
        """Ajoute une ligne."""
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(row_data)
        self.endInsertRows()
    
    def update_row(self, row_index, new_data):
        """Met à jour une ligne."""
        if 0 <= row_index < len(self._data):
            self._data[row_index] = new_data
            self.dataChanged.emit(
                self.index(row_index, 0),
                self.index(row_index, self.columnCount() - 1)
            )
            return True
        return False
    
    def remove_row(self, row_index):
        """Supprime une ligne."""
        if 0 <= row_index < len(self._data):
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            del self._data[row_index]
            self.endRemoveRows()
            return True
        return False


class StockManager(QObject):
    """Manager de gestion du stock avec ModalView générique."""
    
    version = "4.1"  # Version avec tous les champs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Données
        self.data = list(dummy_stock_data)
        self.headers = stock_headers
        self.model = StockTableModel(self.data, self.headers)
        
        # État des filtres
        self.current_filters = {
            'search': '',
            'category': 'Toutes',
            'supplier': 'Tous',
            'packaging': 'tous',
            'class': 'Toutes',
            'start_date': QDate(2024, 1, 1),
            'end_date': QDate.currentDate()
        }
        
        print(f"[StockManager v{self.version}] Initialisé avec {len(self.data)} produits")
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.stock_view import StockView
            
            self.view = StockView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[StockManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.view.set_table_model(self.model)
        self._update_filter_options()
        self.apply_filters()
        print("[StockManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_requested.connect(self.on_search_requested)
        self.view.category_filter_changed.connect(self.on_category_changed)
        self.view.supplier_filter_changed.connect(self.on_supplier_changed)
        self.view.packaging_filter_changed.connect(self.on_packaging_changed)
        self.view.class_filter_changed.connect(self.on_class_changed)
        self.view.date_range_changed.connect(self.on_date_range_changed)
        self.view.add_product_requested.connect(self.add_product)
        self.view.edit_product_requested.connect(self.edit_product)
        self.view.delete_product_requested.connect(self.delete_product)
        self.view.refresh_requested.connect(self.refresh)
        print("[StockManager] Signaux connectés")
    
    def _update_filter_options(self):
        """Met à jour les options de filtres dynamiques."""
        categories = sorted(list(set(
            item[self.headers.index("Catégorie")] for item in self.data
            if item[self.headers.index("Catégorie")]
        )))
        self.view.update_categories(categories)
        
        suppliers = sorted(list(set(
            item[self.headers.index("Fournisseur")] for item in self.data
            if item[self.headers.index("Fournisseur")]
        )))
        self.view.update_suppliers(suppliers)
        
        classes = sorted(list(set(
            item[self.headers.index("Classe")] for item in self.data
            if item[self.headers.index("Catégorie")] == "Manuels"
            and item[self.headers.index("Classe")]
        )))
        self.view.update_classes(classes)
    
    # ========== SLOTS - GESTION DES FILTRES ==========
    
    @Slot(str)
    def on_search_requested(self, search_text: str):
        self.current_filters['search'] = search_text.lower()
        self.apply_filters()
    
    @Slot(str)
    def on_category_changed(self, category: str):
        self.current_filters['category'] = category
        self.apply_filters()
    
    @Slot(str)
    def on_supplier_changed(self, supplier: str):
        self.current_filters['supplier'] = supplier
        self.apply_filters()
    
    @Slot(str)
    def on_packaging_changed(self, packaging: str):
        self.current_filters['packaging'] = packaging.lower()
        self.apply_filters()
    
    @Slot(str)
    def on_class_changed(self, class_name: str):
        self.current_filters['class'] = class_name
        self.apply_filters()
    
    @Slot(QDate, QDate)
    def on_date_range_changed(self, start_date: QDate, end_date: QDate):
        self.current_filters['start_date'] = start_date
        self.current_filters['end_date'] = end_date
        self.apply_filters()
    
    # ========== LOGIQUE DE FILTRAGE ==========
    
    def apply_filters(self):
        """Applique tous les filtres actifs aux données."""
        filtered_data = []
        
        for item in self.data:
            if self._matches_filters(item):
                filtered_data.append(item)
        
        self.model = StockTableModel(filtered_data, self.headers)
        self.view.set_table_model(self.model)
        
        print(f"[StockManager] {len(filtered_data)}/{len(self.data)} produits affichés")
    
    def _matches_filters(self, item) -> bool:
        """Vérifie si un item correspond à tous les filtres actifs."""
        # Recherche textuelle
        if self.current_filters['search']:
            searchable_text = " ".join(str(item[i]) for i in range(len(item))).lower()
            if self.current_filters['search'] not in searchable_text:
                return False
        
        # Filtre catégorie
        if self.current_filters['category'] != "Toutes":
            if item[self.headers.index("Catégorie")] != self.current_filters['category']:
                return False
        
        # Filtre fournisseur
        if self.current_filters['supplier'] != "Tous":
            if item[self.headers.index("Fournisseur")] != self.current_filters['supplier']:
                return False
        
        # Filtre emballage
        if self.current_filters['packaging'] != "tous":
            item_packaging = item[self.headers.index("Type d'emballage")].lower()
            if item_packaging != self.current_filters['packaging']:
                return False
        
        # Filtre classe
        if (self.current_filters['category'] == "Manuels" and 
            self.current_filters['class'] != "Toutes"):
            if item[self.headers.index("Classe")] != self.current_filters['class']:
                return False
        
        # Filtre dates
        item_date_str = item[self.headers.index("Date d'ajout")]
        item_date = QDate.fromString(item_date_str, "yyyy-MM-dd")
        if not item_date.isValid():
            return False
        if not (self.current_filters['start_date'] <= item_date <= self.current_filters['end_date']):
            return False
        
        return True
    
    # ========== CRÉATION DU FORMULAIRE PRODUIT ==========
    
    def _create_product_form(self, product_data=None):
        """
        Crée un formulaire produit avec ModalView générique.
        INCLUT TOUS LES CHAMPS: Description, Emplacement, Niveau, Langue
        """
        from src.ui.widgets.ModalView import ModalView
        
        is_edit = product_data is not None
        title = "Modifier le Produit" if is_edit else "Ajouter un Produit"
        
        # Créer le modal
        modal = ModalView(
            title=title,
            parent=self.view,
            width=900,
            height=800,  # Plus haut pour les champs supplémentaires
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )
        
        # Créer le formulaire
        form_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # Styles
        label_style = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        input_style = """
            font-size: 14px;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #ffffff;
            color: #2c3e50;
            min-height: 40px;
        """
        
        # Récupérer les options dynamiques
        categories = sorted(list(set(
            item[self.headers.index("Catégorie")] for item in self.data
            if item[self.headers.index("Catégorie")]
        ))) if self.data else ["Papeterie", "Fournitures", "Manuels"]
        
        suppliers = sorted(list(set(
            item[self.headers.index("Fournisseur")] for item in self.data
            if item[self.headers.index("Fournisseur")]
        ))) if self.data else ["Fournisseur A", "Fournisseur B"]
        
        # ===== CRÉATION DES CHAMPS =====
        
        # Nom
        name_input = QLineEdit()
        name_input.setStyleSheet(input_style)
        name_input.setPlaceholderText("Nom du produit")
        if is_edit:
            name_input.setText(str(product_data[self.headers.index("Nom")]))
        
        # Catégorie
        category_combo = QComboBox()
        category_combo.setStyleSheet(input_style)
        category_combo.addItems(categories)
        if is_edit:
            category_combo.setCurrentText(str(product_data[self.headers.index("Catégorie")]))
        
        # Quantité
        quantity_spin = QSpinBox()
        quantity_spin.setStyleSheet(input_style)
        quantity_spin.setRange(0, 100000)
        if is_edit:
            quantity_spin.setValue(int(product_data[self.headers.index("Quantité")]))
        
        # Prix
        price_input = QLineEdit()
        price_input.setStyleSheet(input_style)
        price_input.setPlaceholderText("0.00")
        if is_edit:
            price_input.setText(str(product_data[self.headers.index("Prix")]))
        
        # Code-barres
        barcode_input = QLineEdit()
        barcode_input.setStyleSheet(input_style)
        barcode_input.setPlaceholderText("Code-barres")
        if is_edit:
            barcode_input.setText(str(product_data[self.headers.index("Code-barres")]))
        
        # Type d'emballage
        packaging_combo = QComboBox()
        packaging_combo.setStyleSheet(input_style)
        packaging_combo.addItems(["carton", "unité", "pièce", "lot", "autre"])
        if is_edit:
            packaging_combo.setCurrentText(str(product_data[self.headers.index("Type d'emballage")]).lower())
        
        # Fournisseur
        supplier_combo = QComboBox()
        supplier_combo.setStyleSheet(input_style)
        supplier_combo.addItems(suppliers)
        if is_edit:
            supplier_combo.setCurrentText(str(product_data[self.headers.index("Fournisseur")]))
        
        # Contact Fournisseur
        contact_input = QLineEdit()
        contact_input.setStyleSheet(input_style)
        contact_input.setPlaceholderText("contact@fournisseur.com")
        if is_edit:
            contact_input.setText(str(product_data[self.headers.index("Contact Fournisseur")]))
        
        # ===== CHAMPS SUPPLÉMENTAIRES =====
        
        # Description
        description_input = QLineEdit()
        description_input.setStyleSheet(input_style)
        description_input.setPlaceholderText("Description du produit")
        if is_edit and "Description" in self.headers:
            desc_value = product_data[self.headers.index("Description")]
            description_input.setText(str(desc_value) if desc_value else "")
        
        # Emplacement
        emplacement_input = QLineEdit()
        emplacement_input.setStyleSheet(input_style)
        emplacement_input.setPlaceholderText("Ex: Section Manuels")
        if is_edit and "Emplacement" in self.headers:
            emp_value = product_data[self.headers.index("Emplacement")]
            emplacement_input.setText(str(emp_value) if emp_value else "")
        
        # Niveau
        niveau_combo = QComboBox()
        niveau_combo.setStyleSheet(input_style)
        niveau_combo.addItems(["Primaire", "Secondaire", "Supérieur", "Autre"])
        if is_edit and "Niveau" in self.headers:
            niv_value = product_data[self.headers.index("Niveau")]
            if niv_value:
                niveau_combo.setCurrentText(str(niv_value))
        
        # Langue
        langue_combo = QComboBox()
        langue_combo.setStyleSheet(input_style)
        langue_combo.addItems(["Francophone", "Anglophone", "Bilingue", "Autre"])
        if is_edit and "Langue" in self.headers:
            lang_value = product_data[self.headers.index("Langue")]
            if lang_value:
                langue_combo.setCurrentText(str(lang_value))
        
        # Classe (pour Manuels)
        classe_input = QLineEdit()
        classe_input.setStyleSheet(input_style)
        classe_input.setPlaceholderText("Ex: Form 2")
        if is_edit and "Classe" in self.headers:
            class_value = product_data[self.headers.index("Classe")]
            classe_input.setText(str(class_value) if class_value else "")
        
        # Fonction helper pour labels
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # ===== AJOUTER TOUS LES CHAMPS AU FORMULAIRE =====
        form_layout.addRow(create_label("Nom:"), name_input)
        form_layout.addRow(create_label("Catégorie:"), category_combo)
        form_layout.addRow(create_label("Quantité:"), quantity_spin)
        form_layout.addRow(create_label("Prix:"), price_input)
        form_layout.addRow(create_label("Code-barres:"), barcode_input)
        form_layout.addRow(create_label("Type d'emballage:"), packaging_combo)
        form_layout.addRow(create_label("Fournisseur:"), supplier_combo)
        form_layout.addRow(create_label("Contact Fournisseur:"), contact_input)
        form_layout.addRow(create_label("Description:"), description_input)
        form_layout.addRow(create_label("Emplacement:"), emplacement_input)
        form_layout.addRow(create_label("Niveau:"), niveau_combo)
        form_layout.addRow(create_label("Langue:"), langue_combo)
        form_layout.addRow(create_label("Classe:"), classe_input)
        
        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)
        
        # Stocker les widgets pour récupération
        modal.name_input = name_input
        modal.category_combo = category_combo
        modal.quantity_spin = quantity_spin
        modal.price_input = price_input
        modal.barcode_input = barcode_input
        modal.packaging_combo = packaging_combo
        modal.supplier_combo = supplier_combo
        modal.contact_input = contact_input
        modal.description_input = description_input
        modal.emplacement_input = emplacement_input
        modal.niveau_combo = niveau_combo
        modal.langue_combo = langue_combo
        modal.classe_input = classe_input
        
        return modal
    
    def _get_product_data_from_modal(self, modal):
        """Récupère les données du formulaire du modal."""
        product_data = [None] * len(self.headers)
        
        # Remplir les données
        product_data[self.headers.index("Nom")] = modal.name_input.text()
        product_data[self.headers.index("Catégorie")] = modal.category_combo.currentText()
        product_data[self.headers.index("Quantité")] = modal.quantity_spin.value()
        product_data[self.headers.index("Prix")] = modal.price_input.text()
        product_data[self.headers.index("Code-barres")] = modal.barcode_input.text()
        product_data[self.headers.index("Type d'emballage")] = modal.packaging_combo.currentText()
        product_data[self.headers.index("Fournisseur")] = modal.supplier_combo.currentText()
        product_data[self.headers.index("Contact Fournisseur")] = modal.contact_input.text()
        product_data[self.headers.index("Date d'ajout")] = QDate.currentDate().toString("yyyy-MM-dd")
        
        # Champs supplémentaires
        if "Description" in self.headers:
            product_data[self.headers.index("Description")] = modal.description_input.text()
        if "Emplacement" in self.headers:
            product_data[self.headers.index("Emplacement")] = modal.emplacement_input.text()
        if "Niveau" in self.headers:
            product_data[self.headers.index("Niveau")] = modal.niveau_combo.currentText()
        if "Langue" in self.headers:
            product_data[self.headers.index("Langue")] = modal.langue_combo.currentText()
        if "Classe" in self.headers:
            product_data[self.headers.index("Classe")] = modal.classe_input.text()
        
        return product_data
    
    # ========== SLOTS - GESTION DES PRODUITS ==========
    
    @Slot()
    def add_product(self):
        """Ouvre le dialogue d'ajout de produit avec ModalView."""
        try:
            modal = self._create_product_form()
            
            def on_save():
                new_product_data = self._get_product_data_from_modal(modal)
                
                # Générer un nouvel ID
                new_id = max(
                    (item[self.headers.index("ID")] for item in self.data),
                    default=0
                ) + 1
                new_product_data[self.headers.index("ID")] = new_id
                
                self.data.append(new_product_data)
                self.refresh()
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le produit '{new_product_data[self.headers.index('Nom')]}' a été ajouté avec succès."
                )
                
                print(f"[StockManager] Produit ajouté: ID {new_id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de l'ajout du produit:\n{str(e)}"
            )
            print(f"[StockManager] ERREUR ajout produit: {e}")
    
    @Slot(int)
    def edit_product(self, row: int):
        """Ouvre le dialogue d'édition de produit avec ModalView."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un produit à modifier."
            )
            return
        
        try:
            item_in_filtered_view = self.model.get_row_data(row)
            
            if not item_in_filtered_view:
                QMessageBox.warning(self.view, "Erreur", "Impossible de récupérer les données du produit.")
                return
            
            # Trouver l'index dans les données originales
            item_id = item_in_filtered_view[self.headers.index("ID")]
            original_index = -1
            
            for i, data_item in enumerate(self.data):
                if data_item[self.headers.index("ID")] == item_id:
                    original_index = i
                    break
            
            if original_index == -1:
                QMessageBox.warning(self.view, "Erreur", "Produit introuvable dans les données.")
                return
            
            product_to_edit = list(self.data[original_index])
            modal = self._create_product_form(product_to_edit)
            
            def on_save():
                updated_product_data = self._get_product_data_from_modal(modal)
                updated_product_data[self.headers.index("ID")] = item_id
                
                self.data[original_index] = updated_product_data
                self.refresh()
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le produit '{updated_product_data[self.headers.index('Nom')]}' a été modifié avec succès."
                )
                
                print(f"[StockManager] Produit modifié: ID {item_id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la modification du produit:\n{str(e)}"
            )
            print(f"[StockManager] ERREUR modification produit: {e}")
    
    @Slot(int)
    def delete_product(self, row: int):
        """Supprime un produit après confirmation."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un produit à supprimer."
            )
            return
        
        try:
            item_to_delete = self.model.get_row_data(row)
            
            if not item_to_delete:
                QMessageBox.warning(self.view, "Erreur", "Impossible de récupérer les données du produit.")
                return
            
            product_name = item_to_delete[self.headers.index('Nom')]
            
            reply = QMessageBox.question(
                self.view,
                "Confirmer la suppression",
                f"Êtes-vous sûr de vouloir supprimer le produit:\n\n'{product_name}' ?\n\nCette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                item_id = item_to_delete[self.headers.index("ID")]
                
                for i, item in enumerate(self.data):
                    if item[self.headers.index("ID")] == item_id:
                        del self.data[i]
                        break
                
                self.refresh()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le produit '{product_name}' a été supprimé avec succès."
                )
                
                print(f"[StockManager] Produit supprimé: ID {item_id}")
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la suppression du produit:\n{str(e)}"
            )
            print(f"[StockManager] ERREUR suppression produit: {e}")
    
    @Slot()
    def refresh(self):
        """Rafraîchit complètement l'affichage."""
        self._update_filter_options()
        self.apply_filters()
        print("[StockManager] Vue rafraîchie")
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def get_product_count(self) -> int:
        """Retourne le nombre total de produits."""
        return len(self.data)
    
    def get_filtered_count(self) -> int:
        """Retourne le nombre de produits après filtrage."""
        return self.model.rowCount()
    
    def export_to_csv(self, filepath: str) -> bool:
        """Exporte les données filtrées vers un fichier CSV."""
        try:
            import csv
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(self.headers)
                
                for row in range(self.model.rowCount()):
                    row_data = self.model.get_row_data(row)
                    if row_data:
                        writer.writerow(row_data)
            
            print(f"[StockManager] Export CSV réussi: {filepath}")
            return True
            
        except Exception as e:
            print(f"[StockManager] ERREUR export CSV: {e}")
            return False