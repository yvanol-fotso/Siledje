"""
Package contenant les modèles de données de l'application.

Ce package définit toutes les classes représentant les entités métier :
- Product : Produits (livres, papeterie)
- Barcode : Codes-barres associés aux produits
- Sale : Ventes effectuées
- StockMovement : Mouvements de stock (entrées/sorties)
- User : Utilisateurs de l'application
"""

from .product import Product
from .barcode import Barcode
from .sale import Sale
from .stock import StockMovement, StockMovementType
from .user import User, UserRole

__all__ = [
    # Modèles principaux
    'Product',
    'Barcode',
    'Sale',
    'StockMovement',
    'User',
    
    # Enums
    'StockMovementType',
    'UserRole',
]