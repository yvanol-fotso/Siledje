"""
Modèle représentant un mouvement de stock (entrée/sortie).
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class StockMovementType(Enum):
    """Types de mouvements de stock."""
    ENTRY = "entry"          # Entrée de stock (approvisionnement)
    EXIT = "exit"            # Sortie de stock (vente)
    ADJUSTMENT = "adjustment"  # Ajustement (inventaire)
    RETURN = "return"        # Retour client


@dataclass
class StockMovement:
    """
    Classe représentant un mouvement de stock.
    
    Attributes:
        product_id: ID du produit concerné
        quantity: Quantité du mouvement (positif = entrée, négatif = sortie)
        movement_type: Type de mouvement (entry, exit, adjustment, return)
        reason: Raison du mouvement
        id: Identifiant unique du mouvement
        created_at: Date et heure du mouvement
        user_id: ID de l'utilisateur ayant effectué le mouvement
    """
    
    product_id: int
    quantity: int
    movement_type: StockMovementType
    reason: str = ""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    user_id: Optional[int] = None
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if self.product_id is None or self.product_id <= 0:
            raise ValueError("L'ID du produit doit être un entier positif")
        
        if self.quantity == 0:
            raise ValueError("La quantité ne peut pas être 0")
        
        # Convertir le type de mouvement si c'est une chaîne
        if isinstance(self.movement_type, str):
            try:
                self.movement_type = StockMovementType(self.movement_type)
            except ValueError:
                raise ValueError(
                    f"Type de mouvement invalide: {self.movement_type}. "
                    f"Valeurs valides: {', '.join([t.value for t in StockMovementType])}"
                )
    
    @classmethod
    def create_entry(
        cls, 
        product_id: int, 
        quantity: int, 
        reason: str = "Approvisionnement",
        user_id: Optional[int] = None
    ) -> 'StockMovement':
        """
        Crée un mouvement d'entrée de stock.
        
        Args:
            product_id: ID du produit
            quantity: Quantité ajoutée (positif)
            reason: Raison de l'entrée
            user_id: ID de l'utilisateur
            
        Returns:
            Instance de StockMovement
        """
        return cls(
            product_id=product_id,
            quantity=abs(quantity),  # S'assurer que c'est positif
            movement_type=StockMovementType.ENTRY,
            reason=reason,
            user_id=user_id
        )
    
    @classmethod
    def create_exit(
        cls, 
        product_id: int, 
        quantity: int, 
        reason: str = "Vente",
        user_id: Optional[int] = None
    ) -> 'StockMovement':
        """
        Crée un mouvement de sortie de stock.
        
        Args:
            product_id: ID du produit
            quantity: Quantité retirée (sera négative)
            reason: Raison de la sortie
            user_id: ID de l'utilisateur
            
        Returns:
            Instance de StockMovement
        """
        return cls(
            product_id=product_id,
            quantity=-abs(quantity),  # S'assurer que c'est négatif
            movement_type=StockMovementType.EXIT,
            reason=reason,
            user_id=user_id
        )
    
    @classmethod
    def create_adjustment(
        cls, 
        product_id: int, 
        quantity: int, 
        reason: str = "Ajustement inventaire",
        user_id: Optional[int] = None
    ) -> 'StockMovement':
        """
        Crée un mouvement d'ajustement de stock.
        
        Args:
            product_id: ID du produit
            quantity: Quantité d'ajustement (+ ou -)
            reason: Raison de l'ajustement
            user_id: ID de l'utilisateur
            
        Returns:
            Instance de StockMovement
        """
        return cls(
            product_id=product_id,
            quantity=quantity,
            movement_type=StockMovementType.ADJUSTMENT,
            reason=reason,
            user_id=user_id
        )
    
    def is_entry(self) -> bool:
        """Vérifie si c'est une entrée de stock."""
        return self.movement_type == StockMovementType.ENTRY
    
    def is_exit(self) -> bool:
        """Vérifie si c'est une sortie de stock."""
        return self.movement_type == StockMovementType.EXIT
    
    def is_adjustment(self) -> bool:
        """Vérifie si c'est un ajustement."""
        return self.movement_type == StockMovementType.ADJUSTMENT
    
    def is_return(self) -> bool:
        """Vérifie si c'est un retour."""
        return self.movement_type == StockMovementType.RETURN
    
    def get_movement_sign(self) -> str:
        """
        Retourne un symbole représentant le mouvement.
        
        Returns:
            '+' pour entrée, '-' pour sortie
        """
        return '+' if self.quantity > 0 else '-'
    
    def to_dict(self) -> dict:
        """
        Convertit le mouvement en dictionnaire.
        
        Returns:
            Dictionnaire représentant le mouvement
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'movement_type': self.movement_type.value,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StockMovement':
        """
        Crée un mouvement à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du mouvement
            
        Returns:
            Instance de StockMovement
        """
        return cls(
            id=data.get('id'),
            product_id=data['product_id'],
            quantity=data['quantity'],
            movement_type=data['movement_type'],
            reason=data.get('reason', ''),
            created_at=data.get('created_at'),
            user_id=data.get('user_id')
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du mouvement."""
        sign = self.get_movement_sign()
        date_str = self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else 'N/A'
        return (f"Mouvement #{self.id} - {self.movement_type.value.upper()} - "
                f"{sign}{abs(self.quantity)} unités ({date_str}) - {self.reason}")
    
    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (f"StockMovement(id={self.id}, product_id={self.product_id}, "
                f"quantity={self.quantity}, type={self.movement_type.value})")