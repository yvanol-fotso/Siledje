"""
Gestionnaire de gestion des rôles et permissions.
Séparation complète de la logique métier et de l'interface.
Utilise ModalView générique pour tous les dialogues.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox, QWidget, QFormLayout, QLineEdit, QLabel, QVBoxLayout, QCheckBox, QGroupBox


class Role:
    """Modèle de données pour un rôle."""
    def __init__(self, role_id=None, name="", description="", permissions=None):
        self.id = role_id
        self.name = name
        self.description = description
        self.permissions = permissions or []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions
        }


class RoleTableModel(QAbstractTableModel):
    """Modèle de table pour les rôles."""
    
    def __init__(self, roles, headers):
        super().__init__()
        self._roles = roles
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._roles)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        role_obj = self._roles[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return str(role_obj.id)
            elif col == 1:
                return role_obj.name
            elif col == 2:
                return role_obj.description
            elif col == 3:
                return f"{len(role_obj.permissions)} permission(s)"
        
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None
    
    def get_role(self, row):
        """Retourne le rôle à la ligne donnée."""
        if 0 <= row < len(self._roles):
            return self._roles[row]
        return None
    
    def add_role(self, role):
        """Ajoute un rôle."""
        self.beginInsertRows(QModelIndex(), len(self._roles), len(self._roles))
        self._roles.append(role)
        self.endInsertRows()
    
    def update_role(self, row, role):
        """Met à jour un rôle."""
        if 0 <= row < len(self._roles):
            self._roles[row] = role
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1)
            )
            return True
        return False
    
    def remove_role(self, row):
        """Supprime un rôle."""
        if 0 <= row < len(self._roles):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._roles[row]
            self.endRemoveRows()
            return True
        return False


class SecurityManager(QObject):
    """Gestionnaire de gestion des rôles et permissions."""
    
    version = "1.0.0"
    
    # Liste complète des permissions disponibles
    AVAILABLE_PERMISSIONS = [
        ("stock_manage", "Gestion du stock"),
        ("sales_access", "Point de vente"),
        ("reports_view", "Rapports et statistiques"),
        ("users_manage", "Gestion des utilisateurs"),
        ("roles_manage", "Gestion des rôles"),
        ("system_config", "Configuration système"),
        ("barcode_manage", "Gestion des barcodes"),
        ("ai_settings", "Paramètres IA"),
        ("export_data", "Exportation de données"),
        ("import_data", "Importation de données"),
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Données
        self.roles = self._load_sample_roles()
        self.headers = ["ID", "Nom du rôle", "Description", "Permissions"]
        self.model = RoleTableModel(self.roles, self.headers)
        
        print(f"[SecurityManager v{self.version}] Initialisé avec {len(self.roles)} rôles")
    
    def _load_sample_roles(self):
        """Charge des rôles de démonstration."""
        return [
            Role(
                1, 
                "Administrateur", 
                "Accès complet au système",
                [perm[0] for perm in self.AVAILABLE_PERMISSIONS]  # Toutes les permissions
            ),
            Role(
                2, 
                "Gestionnaire", 
                "Gestion quotidienne de la librairie",
                ["stock_manage", "sales_access", "reports_view", "barcode_manage", "export_data"]
            ),
            Role(
                3, 
                "Vendeur", 
                "Point de vente uniquement",
                ["sales_access"]
            ),
            Role(
                4,
                "Caissier",
                "Caisse et ventes",
                ["sales_access", "reports_view"]
            ),
        ]
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.security_view import SecurityView
            
            self.view = SecurityView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[SecurityManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.view.set_table_model(self.model)
        print("[SecurityManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_role_requested.connect(self.add_role)
        self.view.edit_role_requested.connect(self.edit_role)
        self.view.delete_role_requested.connect(self.delete_role)
        self.view.refresh_requested.connect(self.refresh)
        print("[SecurityManager] Signaux connectés")
    
    # ========== CRÉATION DU FORMULAIRE RÔLE ==========
    
    def _create_role_form(self, role=None):
        """
        Crée un formulaire de rôle avec ModalView générique.
        """
        from src.ui.widgets.ModalView import ModalView
        
        is_edit = role is not None
        title = "Modifier le rôle" if is_edit else "Nouveau rôle"
        
        # Créer le modal
        modal = ModalView(
            title=title,
            parent=self.view,
            width=800,
            height=700,
            ok_text="Enregistrer",
            cancel_text="Annuler"
        )
        
        # Créer le formulaire
        form_widget = QWidget()
        form_layout = QVBoxLayout()
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
        
        # Fonction helper pour labels
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # ===== INFORMATIONS DE BASE =====
        
        info_layout = QFormLayout()
        info_layout.setSpacing(15)
        
        # Nom du rôle
        name_input = QLineEdit()
        name_input.setStyleSheet(input_style)
        name_input.setPlaceholderText("Nom du rôle")
        if is_edit:
            name_input.setText(role.name)
        
        # Description
        description_input = QLineEdit()
        description_input.setStyleSheet(input_style)
        description_input.setPlaceholderText("Description du rôle")
        if is_edit:
            description_input.setText(role.description)
        
        info_layout.addRow(create_label("Nom du rôle *:"), name_input)
        info_layout.addRow(create_label("Description:"), description_input)
        
        form_layout.addLayout(info_layout)
        
        # ===== PERMISSIONS =====
        
        perm_group = QGroupBox("Permissions")
        perm_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 20px;
                color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: #ffffff;
            }
        """)
        
        perm_layout = QVBoxLayout()
        perm_layout.setSpacing(10)
        
        # Créer les checkboxes pour chaque permission
        permission_checkboxes = {}
        
        for perm_key, perm_label in self.AVAILABLE_PERMISSIONS:
            checkbox = QCheckBox(perm_label)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #2c3e50;
                    spacing: 8px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    background-color: #ffffff;
                }
                QCheckBox::indicator:checked {
                    background-color: #3498db;
                    border-color: #3498db;
                }
                QCheckBox::indicator:checked:after {
                    content: "✓";
                    color: white;
                }
            """)
            
            # Cocher si le rôle a cette permission
            if is_edit and perm_key in role.permissions:
                checkbox.setChecked(True)
            
            permission_checkboxes[perm_key] = checkbox
            perm_layout.addWidget(checkbox)
        
        perm_group.setLayout(perm_layout)
        form_layout.addWidget(perm_group)
        
        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)
        
        # Stocker les widgets pour récupération
        modal.name_input = name_input
        modal.description_input = description_input
        modal.permission_checkboxes = permission_checkboxes
        
        return modal
    
    def _validate_role_form(self, modal):
        """Valide les données du formulaire."""
        name = modal.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(
                self.view,
                "Validation",
                "Le nom du rôle est obligatoire."
            )
            return False
        
        # Vérifier qu'au moins une permission est sélectionnée
        selected_perms = [
            key for key, checkbox in modal.permission_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not selected_perms:
            QMessageBox.warning(
                self.view,
                "Validation",
                "Veuillez sélectionner au moins une permission."
            )
            return False
        
        return True
    
    # ========== SLOTS - GESTION DES RÔLES ==========
    
    @Slot(str)
    def on_search_requested(self, search_text: str):
        """Filtre les rôles selon le texte de recherche."""
        print(f"[SecurityManager] Recherche: {search_text}")
        self.model.layoutChanged.emit()
    
    @Slot()
    def add_role(self):
        """Ajoute un nouveau rôle."""
        try:
            modal = self._create_role_form()
            
            def on_save():
                if not self._validate_role_form(modal):
                    return
                
                # Générer un nouvel ID
                new_id = max((r.id for r in self.roles), default=0) + 1
                
                # Récupérer les permissions sélectionnées
                selected_perms = [
                    key for key, checkbox in modal.permission_checkboxes.items()
                    if checkbox.isChecked()
                ]
                
                new_role = Role(
                    role_id=new_id,
                    name=modal.name_input.text().strip(),
                    description=modal.description_input.text().strip(),
                    permissions=selected_perms
                )
                
                self.roles.append(new_role)
                self.model.add_role(new_role)
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le rôle '{new_role.name}' a été créé avec succès."
                )
                
                print(f"[SecurityManager] Rôle ajouté: ID {new_id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de l'ajout du rôle:\n{str(e)}"
            )
            print(f"[SecurityManager] ERREUR ajout rôle: {e}")
    
    @Slot(int)
    def edit_role(self, row: int):
        """Modifie un rôle existant."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un rôle à modifier."
            )
            return
        
        try:
            role = self.model.get_role(row)
            if not role:
                return
            
            modal = self._create_role_form(role)
            
            def on_save():
                if not self._validate_role_form(modal):
                    return
                
                # Récupérer les permissions sélectionnées
                selected_perms = [
                    key for key, checkbox in modal.permission_checkboxes.items()
                    if checkbox.isChecked()
                ]
                
                role.name = modal.name_input.text().strip()
                role.description = modal.description_input.text().strip()
                role.permissions = selected_perms
                
                self.model.update_role(row, role)
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le rôle '{role.name}' a été modifié avec succès."
                )
                
                print(f"[SecurityManager] Rôle modifié: ID {role.id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la modification du rôle:\n{str(e)}"
            )
            print(f"[SecurityManager] ERREUR modification rôle: {e}")
    
    @Slot(int)
    def delete_role(self, row: int):
        """Supprime un rôle après confirmation."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un rôle à supprimer."
            )
            return
        
        try:
            role = self.model.get_role(row)
            if not role:
                return
            
            # Vérifier si c'est un rôle système
            if role.name in ["Administrateur", "Gestionnaire", "Vendeur"]:
                QMessageBox.warning(
                    self.view,
                    "Suppression impossible",
                    f"Le rôle '{role.name}' est un rôle système et ne peut pas être supprimé."
                )
                return
            
            reply = QMessageBox.question(
                self.view,
                "Confirmer la suppression",
                f"Êtes-vous sûr de vouloir supprimer le rôle:\n\n'{role.name}' ?\n\nCette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.model.remove_role(row)
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"Le rôle '{role.name}' a été supprimé avec succès."
                )
                
                print(f"[SecurityManager] Rôle supprimé: ID {role.id}")
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la suppression du rôle:\n{str(e)}"
            )
            print(f"[SecurityManager] ERREUR suppression rôle: {e}")
    
    @Slot()
    def refresh(self):
        """Rafraîchit l'affichage."""
        self.model.layoutChanged.emit()
        print("[SecurityManager] Vue rafraîchie")