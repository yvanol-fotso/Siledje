"""
Package de gestion de la base de données.
Fournit les outils pour se connecter et interagir avec la base SQLite.
"""

from .connection import DatabaseConnection, get_db_connection
from .manager import DatabaseManager

__all__ = [
    'DatabaseConnection',
    'get_db_connection',
    'DatabaseManager'
]