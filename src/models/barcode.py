"""
Modèle représentant un code-barres associé à un produit.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Barcode:
    """
    Classe représentant un code-barres.
    
    Attributes:
        barcode_text: Texte du code-barres (identifiant unique)
        product_id: ID du produit associé
        type: Type de code-barres ('internal' ou 'external')
        created_at: Date de création
    """
    
    barcode_text: str
    product_id: int
    type: str = 'internal'  # 'internal' ou 'external'
    created_at: Optional[datetime] = None
    
    VALID_TYPES = ['internal', 'external']
    
    def __post_init__(self):
        """Validation des données après initialisation."""
        if not self.barcode_text or not self.barcode_text.strip():
            raise ValueError("Le code-barres ne peut pas être vide")
        
        if self.type not in self.VALID_TYPES:
            raise ValueError(f"Type invalide. Doit être parmi : {', '.join(self.VALID_TYPES)}")
        
        if self.product_id is None or self.product_id <= 0:
            raise ValueError("L'ID du produit doit être un entier positif")
    
    def is_internal(self) -> bool:
        """
        Vérifie si le code-barres est généré en interne.
        
        Returns:
            True si le code-barres est interne
        """
        return self.type == 'internal'
    
    def is_external(self) -> bool:
        """
        Vérifie si le code-barres provient d'un fournisseur externe.
        
        Returns:
            True si le code-barres est externe
        """
        return self.type == 'external'
    
    def to_dict(self) -> dict:
        """
        Convertit le code-barres en dictionnaire.
        
        Returns:
            Dictionnaire représentant le code-barres
        """
        return {
            'barcode_text': self.barcode_text,
            'product_id': self.product_id,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Barcode':
        """
        Crée un code-barres à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du code-barres
            
        Returns:
            Instance de Barcode
        """
        return cls(
            barcode_text=data['barcode_text'],
            product_id=data['product_id'],
            type=data.get('type', 'internal'),
            created_at=data.get('created_at')
        )
    
    def __str__(self) -> str:
        """Représentation textuelle du code-barres."""
        return f"Barcode({self.barcode_text}) - Type: {self.type} - Product ID: {self.product_id}"
    
    def __repr__(self) -> str:
        """Représentation pour le débogage."""
        return (f"Barcode(barcode_text='{self.barcode_text}', product_id={self.product_id}, "
                f"type='{self.type}')")