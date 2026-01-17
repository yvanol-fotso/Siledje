"""
Manager de la gestion du stock - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex, QDate
from PySide6.QtWidgets import QMessageBox, QDialog
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
        return self._data[row]
    
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
    """
    Manager de gestion du stock - Logique métier.
    Sépare complètement la logique de la présentation.
    """
    
    version = "2.5"
    
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
    
    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            from src.ui.views.stock_view import StockView
            
            self.view = StockView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        # Définir le modèle
        self.view.set_table_model(self.model)
        
        # Peupler les combos
        self._update_filter_options()
        
        # Appliquer les filtres initiaux
        self.apply_filters()
    
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
    
    def _update_filter_options(self):
        """Met à jour les options de filtres."""
        # Catégories
        categories = sorted(list(set(
            item[self.headers.index("Catégorie")] for item in self.data
        )))
        self.view.update_categories(categories)
        
        # Fournisseurs
        suppliers = sorted(list(set(
            item[self.headers.index("Fournisseur")] for item in self.data
        )))
        self.view.update_suppliers(suppliers)
        
        # Classes (pour Manuels)
        classes = sorted(list(set(
            item[self.headers.index("Classe")] for item in self.data
            if item[self.headers.index("Catégorie")] == "Manuels"
            and item[self.headers.index("Classe")]
        )))
        self.view.update_classes(classes)
    
    @Slot(str)
    def on_search_requested(self, search_text: str):
        """Gère la recherche."""
        self.current_filters['search'] = search_text.lower()
        self.apply_filters()
    
    @Slot(str)
    def on_category_changed(self, category: str):
        """Gère le changement de catégorie."""
        self.current_filters['category'] = category
        self.apply_filters()
    
    @Slot(str)
    def on_supplier_changed(self, supplier: str):
        """Gère le changement de fournisseur."""
        self.current_filters['supplier'] = supplier
        self.apply_filters()
    
    @Slot(str)
    def on_packaging_changed(self, packaging: str):
        """Gère le changement de type d'emballage."""
        self.current_filters['packaging'] = packaging.lower()
        self.apply_filters()
    
    @Slot(str)
    def on_class_changed(self, class_name: str):
        """Gère le changement de classe."""
        self.current_filters['class'] = class_name
        self.apply_filters()
    
    @Slot(QDate, QDate)
    def on_date_range_changed(self, start_date: QDate, end_date: QDate):
        """Gère le changement de plage de dates."""
        self.current_filters['start_date'] = start_date
        self.current_filters['end_date'] = end_date
        self.apply_filters()
    
    def apply_filters(self):
        """Applique tous les filtres actifs."""
        filtered_data = []
        
        for item in self.data:
            if not self._matches_filters(item):
                continue
            filtered_data.append(item)
        
        # Mettre à jour le modèle
        self.model = StockTableModel(filtered_data, self.headers)
        self.view.set_table_model(self.model)
        
        print(f"[StockManager] Filtres appliqués : {len(filtered_data)} produits")
    
    def _matches_filters(self, item) -> bool:
        """Vérifie si un item correspond aux filtres."""
        # Recherche textuelle
        if self.current_filters['search']:
            searchable_text = " ".join(str(item[i]) for i in range(len(item))).lower()
            if self.current_filters['search'] not in searchable_text:
                return False
        
        # Catégorie
        if self.current_filters['category'] != "Toutes":
            if item[self.headers.index("Catégorie")] != self.current_filters['category']:
                return False
        
        # Fournisseur
        if self.current_filters['supplier'] != "Tous":
            if item[self.headers.index("Fournisseur")] != self.current_filters['supplier']:
                return False
        
        # Type d'emballage
        if self.current_filters['packaging'] != "tous":
            if item[self.headers.index("Type d'emballage")].lower() != self.current_filters['packaging']:
                return False
        
        # Classe (pour Manuels)
        if (self.current_filters['category'] == "Manuels" and 
            self.current_filters['class'] != "Toutes"):
            if item[self.headers.index("Classe")] != self.current_filters['class']:
                return False
        
        # Plage de dates
        item_date_str = item[self.headers.index("Date d'ajout")]
        item_date = QDate.fromString(item_date_str, "yyyy-MM-dd")
        if not (self.current_filters['start_date'] <= item_date <= self.current_filters['end_date']):
            return False
        
        return True
    
    @Slot()
    def add_product(self):
        """Ouvre le dialogue d'ajout de produit."""
        # Import local pour éviter les imports circulaires
        from src.ui.dialogs.product_form_dialog import ProductFormDialog
        
        dialog = ProductFormDialog(headers=self.headers, parent=self.view, all_stock_data=self.data)
        if dialog.exec() == QDialog.Accepted:
            new_product_data = dialog.get_product_data()
            new_id = max(item[self.headers.index("ID")] for item in self.data) + 1 if self.data else 1
            new_product_data[self.headers.index("ID")] = new_id
            self.data.append(new_product_data)
            self.refresh()
            QMessageBox.information(self.view, "Succès", "Le produit a été ajouté avec succès.")
    
    @Slot(int)
    def edit_product(self, row: int):
        """Ouvre le dialogue d'édition de produit."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(self.view, "Erreur", "Veuillez sélectionner un produit à modifier.")
            return
        
        from src.ui.dialogs.product_form_dialog import ProductFormDialog
        
        item_in_filtered_view = self.model.get_row_data(row)
        
        # Trouver l'index dans les données originales
        original_index = -1
        item_id = item_in_filtered_view[self.headers.index("ID")]
        for i, data_item in enumerate(self.data):
            if data_item[self.headers.index("ID")] == item_id:
                original_index = i
                break
        
        if original_index == -1:
            QMessageBox.warning(self.view, "Erreur", "Produit introuvable.")
            return
        
        product_to_edit = list(self.data[original_index])
        dialog = ProductFormDialog(
            product_data=product_to_edit,
            headers=self.headers,
            parent=self.view,
            all_stock_data=self.data
        )
        
        if dialog.exec() == QDialog.Accepted:
            updated_product_data = dialog.get_product_data()
            self.data[original_index] = updated_product_data
            self.refresh()
            QMessageBox.information(self.view, "Succès", "Le produit a été modifié avec succès.")
    
    @Slot(int)
    def delete_product(self, row: int):
        """Supprime un produit."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(self.view, "Erreur", "Veuillez sélectionner un produit à supprimer.")
            return
        
        item_to_delete = self.model.get_row_data(row)
        
        reply = QMessageBox.question(
            self.view,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le produit '{item_to_delete[self.headers.index('Nom')]}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            item_id = item_to_delete[self.headers.index("ID")]
            
            # Trouver et supprimer dans les données originales
            for i, item in enumerate(self.data):
                if item[self.headers.index("ID")] == item_id:
                    del self.data[i]
                    break
            
            self.refresh()
            QMessageBox.information(self.view, "Succès", "Le produit a été supprimé avec succès.")
    
    @Slot()
    def refresh(self):
        """Rafraîchit l'affichage."""
        self._update_filter_options()
        self.apply_filters()
        print("[StockManager] Vue rafraîchie")