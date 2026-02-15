"""
Gestionnaire de gestion des utilisateurs.
Séparation complète de la logique métier et de l'interface.
Utilise ModalView générique pour tous les dialogues.
"""

from PySide6.QtCore import QObject, Slot, QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox, QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel
from datetime import datetime


class User:
    """Modèle de données pour un utilisateur."""
    def __init__(self, user_id=None, username="", name="", email="", role="", 
                 is_active=True, created_at=None, last_login=None, password=""):
        self.id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_login = last_login
        self.password = password  # En production: hash bcrypt

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_login': self.last_login
        }


class UserTableModel(QAbstractTableModel):
    """Modèle de table pour les utilisateurs."""
    
    def __init__(self, users, headers):
        super().__init__()
        self._users = users
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._users)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        user = self._users[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return str(user.id)
            elif col == 1:
                return user.username
            elif col == 2:
                return user.name
            elif col == 3:
                return user.email
            elif col == 4:
                return user.role
            elif col == 5:
                return "Actif" if user.is_active else "Inactif"
            elif col == 6:
                return user.last_login or "Jamais"
        
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None
    
    def get_user(self, row):
        """Retourne l'utilisateur à la ligne donnée."""
        if 0 <= row < len(self._users):
            return self._users[row]
        return None
    
    def add_user(self, user):
        """Ajoute un utilisateur."""
        self.beginInsertRows(QModelIndex(), len(self._users), len(self._users))
        self._users.append(user)
        self.endInsertRows()
    
    def update_user(self, row, user):
        """Met à jour un utilisateur."""
        if 0 <= row < len(self._users):
            self._users[row] = user
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1)
            )
            return True
        return False
    
    def remove_user(self, row):
        """Supprime un utilisateur."""
        if 0 <= row < len(self._users):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._users[row]
            self.endRemoveRows()
            return True
        return False
    
    def filter_users(self, search_text):
        """Filtre les utilisateurs selon le texte de recherche."""
        # Simple refresh - dans une vraie app, implémenter un proxy model
        self.layoutChanged.emit()


class AdminManager(QObject):
    """Gestionnaire de gestion des utilisateurs."""
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Données
        self.users = self._load_sample_users()
        self.roles = ["Administrateur", "Gestionnaire", "Vendeur", "Caissier"]
        self.headers = ["ID", "Nom d'utilisateur", "Nom complet", "Email", "Rôle", "Statut", "Dernière connexion"]
        self.model = UserTableModel(self.users, self.headers)
        
        print(f"[AdminManager v{self.version}] Initialisé avec {len(self.users)} utilisateurs")
    
    def _load_sample_users(self):
        """Charge des utilisateurs de démonstration."""
        return [
            User(1, "admin", "Administrateur Principal", "admin@siledje.cm", "Administrateur", True, 
                 "2025-01-01 10:00:00", "2025-01-08 08:30:00", "admin123"),
            User(2, "manager", "Jean Dupont", "jean.dupont@siledje.cm", "Gestionnaire", True,
                 "2025-01-02 14:00:00", "2025-01-07 16:45:00", "manager123"),
            User(3, "vendeur1", "Marie Kamga", "marie.kamga@siledje.cm", "Vendeur", True,
                 "2025-01-03 09:00:00", "2025-01-08 07:15:00", "vendeur123"),
            User(4, "caissier1", "Paul Nkeng", "paul.nkeng@siledje.cm", "Caissier", False,
                 "2025-01-04 08:00:00", "2025-01-05 10:00:00", "caissier123"),
        ]
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.admin_view import AdminView
            
            self.view = AdminView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[AdminManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.view.set_table_model(self.model)
        print("[AdminManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_requested.connect(self.on_search_requested)
        self.view.add_user_requested.connect(self.add_user)
        self.view.edit_user_requested.connect(self.edit_user)
        self.view.delete_user_requested.connect(self.delete_user)
        self.view.refresh_requested.connect(self.refresh)
        print("[AdminManager] Signaux connectés")
    
    # ========== CRÉATION DU FORMULAIRE UTILISATEUR ==========
    
    def _create_user_form(self, user=None):
        """
        Crée un formulaire utilisateur avec ModalView générique.
        """
        from src.ui.widgets.ModalView import ModalView
        
        is_edit = user is not None
        title = "Modifier l'utilisateur" if is_edit else "Nouvel utilisateur"
        
        # Créer le modal
        modal = ModalView(
            title=title,
            parent=self.view,
            width=700,
            height=600,
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
        
        # Fonction helper pour labels
        def create_label(text):
            label = QLabel(text)
            label.setStyleSheet(label_style)
            return label
        
        # ===== CHAMPS DU FORMULAIRE =====
        
        # Nom d'utilisateur
        username_input = QLineEdit()
        username_input.setStyleSheet(input_style)
        username_input.setPlaceholderText("Nom d'utilisateur unique")
        if is_edit:
            username_input.setText(user.username)
        
        # Nom complet
        name_input = QLineEdit()
        name_input.setStyleSheet(input_style)
        name_input.setPlaceholderText("Nom complet")
        if is_edit:
            name_input.setText(user.name)
        
        # Email
        email_input = QLineEdit()
        email_input.setStyleSheet(input_style)
        email_input.setPlaceholderText("email@example.com")
        if is_edit:
            email_input.setText(user.email)
        
        # Mot de passe
        password_input = QLineEdit()
        password_input.setStyleSheet(input_style)
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Mot de passe" if not is_edit else "Laisser vide pour ne pas changer")
        
        # Rôle
        role_combo = QComboBox()
        role_combo.setStyleSheet(input_style)
        role_combo.addItems(self.roles)
        if is_edit:
            role_combo.setCurrentText(user.role)
        
        # Compte actif
        active_checkbox = QCheckBox("Compte actif")
        active_checkbox.setStyleSheet("font-size: 14px; color: #2c3e50;")
        active_checkbox.setChecked(True if not is_edit else user.is_active)
        
        # Ajouter au formulaire
        form_layout.addRow(create_label("Nom d'utilisateur *:"), username_input)
        form_layout.addRow(create_label("Nom complet *:"), name_input)
        form_layout.addRow(create_label("Email *:"), email_input)
        form_layout.addRow(create_label("Mot de passe *:"), password_input)
        form_layout.addRow(create_label("Rôle *:"), role_combo)
        form_layout.addRow(create_label(""), active_checkbox)
        
        form_widget.setLayout(form_layout)
        modal.set_content(form_widget)
        
        # Stocker les widgets pour récupération
        modal.username_input = username_input
        modal.name_input = name_input
        modal.email_input = email_input
        modal.password_input = password_input
        modal.role_combo = role_combo
        modal.active_checkbox = active_checkbox
        
        return modal
    
    def _validate_user_form(self, modal, is_edit=False):
        """Valide les données du formulaire."""
        username = modal.username_input.text().strip()
        name = modal.name_input.text().strip()
        email = modal.email_input.text().strip()
        password = modal.password_input.text().strip()
        
        if not username or not name or not email:
            QMessageBox.warning(
                self.view,
                "Validation",
                "Tous les champs obligatoires doivent être remplis."
            )
            return False
        
        if not is_edit and not password:
            QMessageBox.warning(
                self.view,
                "Validation",
                "Le mot de passe est obligatoire pour un nouvel utilisateur."
            )
            return False
        
        return True
    
    # ========== SLOTS - GESTION DES UTILISATEURS ==========
    
    @Slot(str)
    def on_search_requested(self, search_text: str):
        """Filtre les utilisateurs selon le texte de recherche."""
        # Implémentation simple - dans une vraie app, utiliser QSortFilterProxyModel
        print(f"[AdminManager] Recherche: {search_text}")
        self.model.filter_users(search_text)
    
    @Slot()
    def add_user(self):
        """Ajoute un nouvel utilisateur."""
        try:
            modal = self._create_user_form()
            
            def on_save():
                if not self._validate_user_form(modal, is_edit=False):
                    return
                
                # Générer un nouvel ID
                new_id = max((u.id for u in self.users), default=0) + 1
                
                new_user = User(
                    user_id=new_id,
                    username=modal.username_input.text().strip(),
                    name=modal.name_input.text().strip(),
                    email=modal.email_input.text().strip(),
                    role=modal.role_combo.currentText(),
                    is_active=modal.active_checkbox.isChecked(),
                    password=modal.password_input.text().strip()
                )
                
                self.users.append(new_user)
                self.model.add_user(new_user)
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"L'utilisateur '{new_user.name}' a été créé avec succès."
                )
                
                print(f"[AdminManager] Utilisateur ajouté: ID {new_id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de l'ajout de l'utilisateur:\n{str(e)}"
            )
            print(f"[AdminManager] ERREUR ajout utilisateur: {e}")
    
    @Slot(int)
    def edit_user(self, row: int):
        """Modifie un utilisateur existant."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un utilisateur à modifier."
            )
            return
        
        try:
            user = self.model.get_user(row)
            if not user:
                return
            
            modal = self._create_user_form(user)
            
            def on_save():
                if not self._validate_user_form(modal, is_edit=True):
                    return
                
                user.username = modal.username_input.text().strip()
                user.name = modal.name_input.text().strip()
                user.email = modal.email_input.text().strip()
                user.role = modal.role_combo.currentText()
                user.is_active = modal.active_checkbox.isChecked()
                
                password = modal.password_input.text().strip()
                if password:
                    user.password = password
                
                self.model.update_user(row, user)
                modal.accept()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"L'utilisateur '{user.name}' a été modifié avec succès."
                )
                
                print(f"[AdminManager] Utilisateur modifié: ID {user.id}")
            
            modal.ok_clicked.connect(on_save)
            modal.exec()
            
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la modification de l'utilisateur:\n{str(e)}"
            )
            print(f"[AdminManager] ERREUR modification utilisateur: {e}")
    
    @Slot(int)
    def delete_user(self, row: int):
        """Supprime un utilisateur après confirmation."""
        if row < 0 or row >= self.model.rowCount():
            QMessageBox.warning(
                self.view,
                "Sélection requise",
                "Veuillez sélectionner un utilisateur à supprimer."
            )
            return
        
        try:
            user = self.model.get_user(row)
            if not user:
                return
            
            reply = QMessageBox.question(
                self.view,
                "Confirmer la suppression",
                f"Êtes-vous sûr de vouloir supprimer l'utilisateur:\n\n'{user.name}' ?\n\nCette action est irréversible.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.model.remove_user(row)
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"L'utilisateur '{user.name}' a été supprimé avec succès."
                )
                
                print(f"[AdminManager] Utilisateur supprimé: ID {user.id}")
                
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la suppression de l'utilisateur:\n{str(e)}"
            )
            print(f"[AdminManager] ERREUR suppression utilisateur: {e}")
    
    @Slot()
    def refresh(self):
        """Rafraîchit l'affichage."""
        self.model.layoutChanged.emit()
        print("[AdminManager] Vue rafraîchie")