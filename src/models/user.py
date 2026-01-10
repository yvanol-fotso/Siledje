"""
Modèle représentant un utilisateur de l'application.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum
import hashlib


class UserRole(Enum):
    """Rôles utilisateur disponibles."""
    ADMIN = "admin"          # Administrateur (tous les droits)
    MANAGER = "manager"      # Gestionnaire (gestion stock, ventes, rapports)
    CASHIER = "cashier"      # Caissier (ventes uniquement)
    USER = "user"            # Utilisateur basique (lecture seule)


@dataclass
class User:
    """
    Classe représentant un utilisateur.
    
    Attributes:
        username: Nom d'utilisateur (unique)
        password_hash: Hash du mot de passe (ne jamais stocker en clair)
        role: Rôle de l'utilisateur (admin, manager, cashier, user)
        id: Identifiant unique de l'utilisateur
        created_at: Date de création du compte
        last_login: Date de dernière connexion
        is_active: Compte actif ou désactivé
    """
    
    username: str
    password_hash: str
    role: UserRole
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if not self.username or not self.username.strip():
            raise ValueError("Le nom d'utilisateur ne peut pas être vide")
        
        if len(self.username) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        
        if not self.password_hash:
            raise ValueError("Le hash du mot de passe ne peut pas être vide")
        
        # Convertir le rôle si c'est une chaîne
        if isinstance(self.role, str):
            try:
                self.role = UserRole(self.role)
            except ValueError:
                raise ValueError(
                    f"Rôle invalide: {self.role}. "
                    f"Valeurs valides: {', '.join([r.value for r in UserRole])}"
                )
    
    @classmethod
    def create(
        cls, 
        username: str, 
        password: str, 
        role: UserRole = UserRole.USER
    ) -> 'User':
        """
        Crée un utilisateur en hashant automatiquement le mot de passe.
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair
            role: Rôle de l'utilisateur
            
        Returns:
            Instance de User
        """
        password_hash = cls.hash_password(password)
        return cls(
            username=username,
            password_hash=password_hash,
            role=role
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash un mot de passe avec SHA-256.
        
        Args:
            password: Mot de passe en clair
            
        Returns:
            Hash du mot de passe
            
        Note:
            Pour une application en production, utiliser bcrypt ou argon2
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """
        Vérifie si un mot de passe correspond à celui de l'utilisateur.
        
        Args:
            password: Mot de passe à vérifier
            
        Returns:
            True si le mot de passe est correct
        """
        password_hash = self.hash_password(password)
        return password_hash == self.password_hash
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change le mot de passe de l'utilisateur.
        
        Args:
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
            
        Returns:
            True si le changement a réussi
        """
        if not self.verify_password(old_password):
            return False
        
        if len(new_password) < 6:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 6 caractères")
        
        self.password_hash = self.hash_password(new_password)
        return True
    
    # ==================== GESTION DES RÔLES ====================
    
    def is_admin(self) -> bool:
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == UserRole.ADMIN
    
    def is_manager(self) -> bool:
        """Vérifie si l'utilisateur est gestionnaire."""
        return self.role == UserRole.MANAGER
    
    def is_cashier(self) -> bool:
        """Vérifie si l'utilisateur est caissier."""
        return self.role == UserRole.CASHIER
    
    def has_permission(self, required_role: UserRole) -> bool:
        """
        Vérifie si l'utilisateur a au moins le rôle requis.
        
        Hiérarchie: ADMIN > MANAGER > CASHIER > USER
        
        Args:
            required_role: Rôle minimum requis
            
        Returns:
            True si l'utilisateur a la permission
        """
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.MANAGER: 2,
            UserRole.CASHIER: 1,
            UserRole.USER: 0
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def can_manage_stock(self) -> bool:
        """Vérifie si l'utilisateur peut gérer le stock."""
        return self.has_permission(UserRole.MANAGER)
    
    def can_make_sales(self) -> bool:
        """Vérifie si l'utilisateur peut effectuer des ventes."""
        return self.has_permission(UserRole.CASHIER)
    
    def can_view_reports(self) -> bool:
        """Vérifie si l'utilisateur peut voir les rapports."""
        return self.has_permission(UserRole.MANAGER)
    
    def can_manage_users(self) -> bool:
        """Vérifie si l'utilisateur peut gérer les autres utilisateurs."""
        return self.is_admin()
    
    # ==================== GESTION DE L'ACTIVITÉ ====================
    
    def activate(self):
        """Active le compte utilisateur."""
        self.is_active = True
    
    def deactivate(self):
        """Désactive le compte utilisateur."""
        self.is_active = False
    
    def update_last_login(self):
        """Met à jour la date de dernière connexion."""
        self.last_login = datetime.now()
    
    # ==================== CONVERSION ====================
    
    def to_dict(self, include_password: bool = False) -> dict:
        """
        Convertit l'utilisateur en dictionnaire.
        
        Args:
            include_password: Inclure le hash du mot de passe (défaut: False)
            
        Returns:
            Dictionnaire représentant l'utilisateur
        """
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Crée un utilisateur à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données de l'utilisateur
            
        Returns:
            Instance de User
        """
        return cls(
            id=data.get('id'),
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            created_at=data.get('created_at'),
            last_login=data.get('last_login'),
            is_active=data.get('is_active', True)
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de l'utilisateur."""
        status = "actif" if self.is_active else "inactif"
        return f"{self.username} ({self.role.value}) - {status}"
    
    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (f"User(id={self.id}, username='{self.username}', "
                f"role={self.role.value}, is_active={self.is_active})")