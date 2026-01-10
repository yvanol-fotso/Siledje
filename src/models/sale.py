"""
Modèle représentant une vente dans la librairie/papeterie.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Sale:
    """
    Classe représentant une vente.
    
    Attributes:
        product_id: ID du produit vendu
        quantity: Quantité vendue
        unit_price: Prix unitaire au moment de la vente
        total_price: Prix total (quantity × unit_price)
        id: Identifiant unique de la vente
        sale_date: Date et heure de la vente
    """
    
    product_id: int
    quantity: int
    unit_price: float
    total_price: float
    id: Optional[int] = None
    sale_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if self.product_id is None or self.product_id <= 0:
            raise ValueError("L'ID du produit doit être un entier positif")
        
        if self.quantity <= 0:
            raise ValueError("La quantité doit être supérieure à 0")
        
        if self.unit_price < 0:
            raise ValueError("Le prix unitaire ne peut pas être négatif")
        
        if self.total_price < 0:
            raise ValueError("Le prix total ne peut pas être négatif")
        
        # Vérifier la cohérence du prix total
        calculated_total = self.quantity * self.unit_price
        if abs(self.total_price - calculated_total) > 0.01:  # Tolérance de 1 centime
            raise ValueError(
                f"Prix total incohérent. Attendu: {calculated_total:.2f}, "
                f"Reçu: {self.total_price:.2f}"
            )
    
    @classmethod
    def create(cls, product_id: int, quantity: int, unit_price: float) -> 'Sale':
        """
        Crée une vente en calculant automatiquement le prix total.
        
        Args:
            product_id: ID du produit
            quantity: Quantité vendue
            unit_price: Prix unitaire
            
        Returns:
            Instance de Sale
        """
        total_price = quantity * unit_price
        return cls(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
    
    def calculate_profit(self, cost_price: float) -> float:
        """
        Calcule le profit sur cette vente.
        
        Args:
            cost_price: Prix d'achat unitaire du produit
            
        Returns:
            Montant du profit
        """
        profit_per_unit = self.unit_price - cost_price
        return profit_per_unit * self.quantity
    
    def calculate_margin_percentage(self, cost_price: float) -> float:
        """
        Calcule le pourcentage de marge sur cette vente.
        
        Args:
            cost_price: Prix d'achat unitaire du produit
            
        Returns:
            Pourcentage de marge (0-100)
        """
        if cost_price == 0:
            return 0.0
        
        margin = ((self.unit_price - cost_price) / cost_price) * 100
        return round(margin, 2)
    
    def to_dict(self) -> dict:
        """
        Convertit la vente en dictionnaire.
        
        Returns:
            Dictionnaire représentant la vente
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Sale':
        """
        Crée une vente à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données de la vente
            
        Returns:
            Instance de Sale
        """
        return cls(
            id=data.get('id'),
            product_id=data['product_id'],
            quantity=data['quantity'],
            unit_price=data['unit_price'],
            total_price=data['total_price'],
            sale_date=data.get('sale_date')
        )
    
    def __str__(self) -> str:
        """Représentation textuelle de la vente."""
        date_str = self.sale_date.strftime('%d/%m/%Y %H:%M') if self.sale_date else 'N/A'
        return (f"Vente #{self.id} - {self.quantity} unité(s) × {self.unit_price}€ = "
                f"{self.total_price}€ ({date_str})")
    
    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (f"Sale(id={self.id}, product_id={self.product_id}, "
                f"quantity={self.quantity}, total_price={self.total_price})")