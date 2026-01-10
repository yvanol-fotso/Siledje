"""
Module de Gestion de la Sécurité - Utilisateurs et Rôles
Auteur: Mr FOTSO TATCHUM Yvanol Rosly
Date: Janvier 2025
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QDialog,
    QFormLayout, QCheckBox, QGroupBox, QTabWidget, QHeaderView,
    QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from datetime import datetime
import json


class User:
    """Modèle de données pour un utilisateur"""
    def __init__(self, user_id=None, username="", name="", email="", role="", 
                 is_active=True, created_at=None, last_login=None):
        self.id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_login = last_login

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


class Role:
    """Modèle de données pour un rôle"""
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


class UserDialog(QDialog):
    """Dialog pour créer/modifier un utilisateur"""
    def __init__(self, parent=None, user=None, roles=None):
        super().__init__(parent)
        self.user = user
        self.roles = roles or ["Administrateur", "Gestionnaire", "Vendeur", "Caissier"]
        self.setWindowTitle("Ajouter Utilisateur" if not user else "Modifier Utilisateur")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Formulaire
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(self.roles)
        self.active_checkbox = QCheckBox("Compte actif")
        self.active_checkbox.setChecked(True)

        form_layout.addRow("Nom d'utilisateur *:", self.username_input)
        form_layout.addRow("Nom complet *:", self.name_input)
        form_layout.addRow("Email *:", self.email_input)
        form_layout.addRow("Mot de passe *:", self.password_input)
        form_layout.addRow("Rôle *:", self.role_combo)
        form_layout.addRow("", self.active_checkbox)

        layout.addLayout(form_layout)

        # Si modification, pré-remplir les champs
        if self.user:
            self.username_input.setText(self.user.username)
            self.name_input.setText(self.user.name)
            self.email_input.setText(self.user.email)
            self.password_input.setPlaceholderText("Laisser vide pour ne pas changer")
            self.role_combo.setCurrentText(self.user.role)
            self.active_checkbox.setChecked(self.user.is_active)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Enregistrer")
        btn_cancel = QPushButton("❌ Annuler")
        
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_cancel.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px;")
        
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_user_data(self):
        """Retourne les données saisies"""
        return {
            'username': self.username_input.text().strip(),
            'name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'password': self.password_input.text().strip(),
            'role': self.role_combo.currentText(),
            'is_active': self.active_checkbox.isChecked()
        }

    def validate(self):
        """Valide les données du formulaire"""
        data = self.get_user_data()
        if not data['username'] or not data['name'] or not data['email']:
            QMessageBox.warning(self, "Erreur", "Tous les champs obligatoires doivent être remplis.")
            return False
        if not self.user and not data['password']:
            QMessageBox.warning(self, "Erreur", "Le mot de passe est obligatoire pour un nouvel utilisateur.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()


class RoleDialog(QDialog):
    """Dialog pour créer/modifier un rôle"""
    def __init__(self, parent=None, role=None):
        super().__init__(parent)
        self.role = role
        self.setWindowTitle("Ajouter Rôle" if not role else "Modifier Rôle")
        self.setMinimumWidth(600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Informations de base
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        
        form_layout.addRow("Nom du rôle *:", self.name_input)
        form_layout.addRow("Description:", self.description_input)
        layout.addLayout(form_layout)

        # Permissions
        perm_group = QGroupBox("Permissions")
        perm_layout = QVBoxLayout()
        
        self.permissions = {}
        perms_list = [
            ("Gestion du stock", "stock_manage"),
            ("Point de vente", "sales_access"),
            ("Rapports et statistiques", "reports_view"),
            ("Gestion des utilisateurs", "users_manage"),
            ("Configuration système", "system_config"),
            ("Gestion des barcodes", "barcode_manage"),
            ("Paramètres IA", "ai_settings")
        ]

        for label, key in perms_list:
            checkbox = QCheckBox(label)
            self.permissions[key] = checkbox
            perm_layout.addWidget(checkbox)

        perm_group.setLayout(perm_layout)
        layout.addWidget(perm_group)

        # Si modification, pré-remplir
        if self.role:
            self.name_input.setText(self.role.name)
            self.description_input.setText(self.role.description)
            for perm in self.role.permissions:
                if perm in self.permissions:
                    self.permissions[perm].setChecked(True)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Enregistrer")
        btn_cancel = QPushButton("❌ Annuler")
        
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_cancel.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 16px; border-radius: 4px;")
        
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_role_data(self):
        """Retourne les données saisies"""
        selected_perms = [key for key, checkbox in self.permissions.items() if checkbox.isChecked()]
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.text().strip(),
            'permissions': selected_perms
        }

    def validate(self):
        data = self.get_role_data()
        if not data['name']:
            QMessageBox.warning(self, "Erreur", "Le nom du rôle est obligatoire.")
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()


class SecurityManager:
    """Gestionnaire principal du module Sécurité"""
    version = "1.0.0"

    def __init__(self):
        self.users = self.load_sample_users()
        self.roles = self.load_sample_roles()

    def load_sample_users(self):
        """Charge des utilisateurs de démonstration"""
        return [
            User(1, "admin", "Administrateur Principal", "admin@siledje.cm", "Administrateur", True, 
                 "2025-01-01 10:00:00", "2025-01-08 08:30:00"),
            User(2, "manager", "Jean Dupont", "jean.dupont@siledje.cm", "Gestionnaire", True,
                 "2025-01-02 14:00:00", "2025-01-07 16:45:00"),
            User(3, "vendeur1", "Marie Kamga", "marie.kamga@siledje.cm", "Vendeur", True,
                 "2025-01-03 09:00:00", "2025-01-08 07:15:00"),
        ]

    def load_sample_roles(self):
        """Charge des rôles de démonstration"""
        return [
            Role(1, "Administrateur", "Accès complet au système", 
                 ["stock_manage", "sales_access", "reports_view", "users_manage", "system_config", "barcode_manage", "ai_settings"]),
            Role(2, "Gestionnaire", "Gestion quotidienne", 
                 ["stock_manage", "sales_access", "reports_view", "barcode_manage"]),
            Role(3, "Vendeur", "Point de vente uniquement", 
                 ["sales_access"]),
        ]

    def get_ui(self):
        """Retourne l'interface graphique du module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # En-tête
        header = QLabel("🔐 Administration - Gestion des Utilisateurs et Rôles")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(header)

        # Tabs pour Utilisateurs et Rôles
        tabs = QTabWidget()
        tabs.addTab(self.create_users_tab(), "👥 Utilisateurs")
        tabs.addTab(self.create_roles_tab(), "🎭 Rôles")
        tabs.addTab(self.create_logs_tab(), "📋 Journal d'activité")
        
        layout.addWidget(tabs)

        return widget

    def create_users_tab(self):
        """Crée l'onglet de gestion des utilisateurs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Barre de recherche et boutons d'action
        top_bar = QHBoxLayout()
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Rechercher un utilisateur...")
        search_input.textChanged.connect(self.filter_users)
        
        btn_add = QPushButton("➕ Nouvel Utilisateur")
        btn_add.setStyleSheet("background-color: #3498db; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_add.clicked.connect(self.add_user)
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.refresh_users)
        
        top_bar.addWidget(search_input)
        top_bar.addWidget(btn_add)
        top_bar.addWidget(btn_refresh)
        layout.addLayout(top_bar)

        # Table des utilisateurs
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Nom d'utilisateur", "Nom complet", "Email", "Rôle", 
            "Statut", "Dernière connexion", "Actions"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setAlternatingRowColors(True)
        
        self.populate_users_table()
        layout.addWidget(self.users_table)

        return widget

    def populate_users_table(self):
        """Remplit la table des utilisateurs"""
        self.users_table.setRowCount(len(self.users))
        
        for row, user in enumerate(self.users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row, 1, QTableWidgetItem(user.username))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.name))
            self.users_table.setItem(row, 3, QTableWidgetItem(user.email))
            self.users_table.setItem(row, 4, QTableWidgetItem(user.role))
            
            status = "✅ Actif" if user.is_active else "❌ Inactif"
            self.users_table.setItem(row, 5, QTableWidgetItem(status))
            self.users_table.setItem(row, 6, QTableWidgetItem(user.last_login or "Jamais"))
            
            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Modifier")
            btn_edit.clicked.connect(lambda checked, u=user: self.edit_user(u))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Supprimer")
            btn_delete.clicked.connect(lambda checked, u=user: self.delete_user(u))
            
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            
            self.users_table.setCellWidget(row, 7, actions_widget)

    def create_roles_tab(self):
        """Crée l'onglet de gestion des rôles"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Boutons d'action
        top_bar = QHBoxLayout()
        
        btn_add_role = QPushButton("➕ Nouveau Rôle")
        btn_add_role.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px 16px; border-radius: 4px;")
        btn_add_role.clicked.connect(self.add_role)
        
        top_bar.addStretch()
        top_bar.addWidget(btn_add_role)
        layout.addLayout(top_bar)

        # Table des rôles
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(4)
        self.roles_table.setHorizontalHeaderLabels([
            "ID", "Nom du rôle", "Description", "Actions"
        ])
        self.roles_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.populate_roles_table()
        layout.addWidget(self.roles_table)

        return widget

    def populate_roles_table(self):
        """Remplit la table des rôles"""
        self.roles_table.setRowCount(len(self.roles))
        
        for row, role in enumerate(self.roles):
            self.roles_table.setItem(row, 0, QTableWidgetItem(str(role.id)))
            self.roles_table.setItem(row, 1, QTableWidgetItem(role.name))
            self.roles_table.setItem(row, 2, QTableWidgetItem(role.description))
            
            # Boutons d'action
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Modifier")
            btn_edit.clicked.connect(lambda checked, r=role: self.edit_role(r))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setToolTip("Supprimer")
            btn_delete.clicked.connect(lambda checked, r=role: self.delete_role(r))
            
            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            
            self.roles_table.setCellWidget(row, 3, actions_widget)

    def create_logs_tab(self):
        """Crée l'onglet du journal d'activité"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("📋 Journal d'activité - En cours de développement")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 50px;")
        layout.addWidget(label)
        
        return widget

    def add_user(self):
        """Ouvre le dialog pour ajouter un utilisateur"""
        dialog = UserDialog(roles=[r.name for r in self.roles])
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_user_data()
            new_user = User(
                user_id=len(self.users) + 1,
                username=data['username'],
                name=data['name'],
                email=data['email'],
                role=data['role'],
                is_active=data['is_active']
            )
            self.users.append(new_user)
            self.populate_users_table()
            QMessageBox.information(None, "Succès", f"Utilisateur '{data['name']}' créé avec succès !")

    def edit_user(self, user):
        """Ouvre le dialog pour modifier un utilisateur"""
        dialog = UserDialog(user=user, roles=[r.name for r in self.roles])
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_user_data()
            user.username = data['username']
            user.name = data['name']
            user.email = data['email']
            user.role = data['role']
            user.is_active = data['is_active']
            self.populate_users_table()
            QMessageBox.information(None, "Succès", "Utilisateur modifié avec succès !")

    def delete_user(self, user):
        """Supprime un utilisateur"""
        reply = QMessageBox.question(
            None, "Confirmation", 
            f"Voulez-vous vraiment supprimer l'utilisateur '{user.name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.users.remove(user)
            self.populate_users_table()
            QMessageBox.information(None, "Succès", "Utilisateur supprimé avec succès !")

    def add_role(self):
        """Ouvre le dialog pour ajouter un rôle"""
        dialog = RoleDialog()
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_role_data()
            new_role = Role(
                role_id=len(self.roles) + 1,
                name=data['name'],
                description=data['description'],
                permissions=data['permissions']
            )
            self.roles.append(new_role)
            self.populate_roles_table()
            QMessageBox.information(None, "Succès", f"Rôle '{data['name']}' créé avec succès !")

    def edit_role(self, role):
        """Ouvre le dialog pour modifier un rôle"""
        dialog = RoleDialog(role=role)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_role_data()
            role.name = data['name']
            role.description = data['description']
            role.permissions = data['permissions']
            self.populate_roles_table()
            QMessageBox.information(None, "Succès", "Rôle modifié avec succès !")

    def delete_role(self, role):
        """Supprime un rôle"""
        reply = QMessageBox.question(
            None, "Confirmation",
            f"Voulez-vous vraiment supprimer le rôle '{role.name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.roles.remove(role)
            self.populate_roles_table()
            QMessageBox.information(None, "Succès", "Rôle supprimé avec succès !")

    def filter_users(self, text):
        """Filtre les utilisateurs selon la recherche"""
        for row in range(self.users_table.rowCount()):
            show = False
            for col in range(self.users_table.columnCount() - 1):
                item = self.users_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show = True
                    break
            self.users_table.setRowHidden(row, not show)

    def refresh_users(self):
        """Actualise la liste des utilisateurs"""
        self.populate_users_table()
        QMessageBox.information(None, "Info", "Liste des utilisateurs actualisée !")