"""
Module de gestion de la connexion à la base de données SQLite.
Fournit un singleton pour garantir une connexion unique dans toute l'application.
"""

import sqlite3
import os
from typing import Optional


class DatabaseConnection:
    """
    Gère la connexion unique (Singleton) à la base de données SQLite.
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls, db_name: str = "librairie.db"):
        """
        Crée une instance unique de DatabaseConnection (pattern Singleton).
        
        Args:
            db_name: Nom du fichier de base de données
            
        Returns:
            Instance unique de DatabaseConnection
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.db_name = db_name
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        """Initialise la connexion à la base de données."""
        try:
            # Créer le dossier data s'il n'existe pas
            db_dir = os.path.dirname(self.db_name)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            self._connection = sqlite3.connect(
                self.db_name,
                check_same_thread=False  # Pour utilisation multi-thread
            )
            # Activer les clés étrangères
            self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Configuration pour retourner les résultats sous forme de dictionnaires
            self._connection.row_factory = sqlite3.Row
            
            print(f"✅ Connecté à la base de données : {self.db_name}")
            
            # Créer les tables si elles n'existent pas
            self._create_tables()
            
        except sqlite3.Error as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            raise
    
    def _create_tables(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        try:
            cursor = self._connection.cursor()
            
            # Table des produits
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des codes-barres
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS barcodes (
                    barcode_text TEXT PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    type TEXT NOT NULL DEFAULT 'internal',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)
            
            # Table des ventes (pour l'historique)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Table des utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self._connection.commit()
            print("✅ Tables vérifiées/créées avec succès")
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la création des tables : {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Retourne la connexion active à la base de données.
        
        Returns:
            Connexion SQLite active
        """
        if self._connection is None:
            self._initialize_connection()
        return self._connection
    
    def get_cursor(self) -> sqlite3.Cursor:
        """
        Retourne un curseur pour exécuter des requêtes.
        
        Returns:
            Curseur SQLite
        """
        return self.get_connection().cursor()
    
    def commit(self):
        """Commit les changements dans la base de données."""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """Annule les changements non commités."""
        if self._connection:
            self._connection.rollback()
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self._connection:
            self._connection.close()
            self._connection = None
            DatabaseConnection._instance = None
            print("🔒 Connexion à la base de données fermée")
    
    def __del__(self):
        """Destructeur pour fermer la connexion proprement."""
        self.close()


# Instance globale (facilite l'import)
def get_db_connection() -> DatabaseConnection:
    """
    Fonction utilitaire pour obtenir l'instance de connexion.
    
    Returns:
        Instance de DatabaseConnection
    """
    return DatabaseConnection()