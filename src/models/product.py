"""
Modèle représentant un produit de la librairie/papeterie.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Classe représentant un produit (livre ou article de papeterie).
    
    Attributes:
        id: Identifiant unique du produit
        name: Nom du produit
        category: Catégorie du produit
        price: Prix du produit
        stock_quantity: Quantité en stock
        created_at: Date de création
        updated_at: Date de dernière modification
    """
    
    name: str
    category: str
    price: float
    stock_quantity: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if self.price < 0:
            raise ValueError("Le prix ne peut pas être négatif")
        if self.stock_quantity < 0:
            raise ValueError("La quantité en stock ne peut pas être négative")
        if not self.name or not self.name.strip():
            raise ValueError("Le nom du produit est obligatoire")
    
    def is_low_stock(self, threshold: int = 10) -> bool:
        """
        Vérifie si le stock est faible.
        
        Args:
            threshold: Seuil de stock minimal
            
        Returns:
            True si le stock est inférieur ou égal au seuil
        """
        return self.stock_quantity <= threshold
    
    def is_in_stock(self) -> bool:
        """
        Vérifie si le produit est disponible en stock.
        
        Returns:
            True si le stock est supérieur à 0
        """
        return self.stock_quantity > 0
    
    def update_stock(self, quantity_change: int) -> int:
        """
        Met à jour le stock du produit.
        
        Args:
            quantity_change: Changement de quantité (positif = ajout, négatif = retrait)
            
        Returns:
            Nouvelle quantité en stock
            
        Raises:
            ValueError: Si le stock devient négatif
        """
        new_stock = self.stock_quantity + quantity_change
        if new_stock < 0:
            raise ValueError(f"Stock insuffisant. Stock actuel: {self.stock_quantity}")
        self.stock_quantity = new_stock
        return self.stock_quantity
    
    def to_dict(self) -> dict:
        """
        Convertit le produit en dictionnaire.
        
        Returns:
            Dictionnaire représentant le produit
        """
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """
        Crée un produit à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du produit
            
        Returns:
            Instance de Product
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            category=data['category'],
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du produit."""
        return f"{self.name} ({self.category}) - {self.price}€ - Stock: {self.stock_quantity}"
    
    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (f"Product(id={self.id}, name='{self.name}', category='{self.category}', "
                f"price={self.price}, stock_quantity={self.stock_quantity})")