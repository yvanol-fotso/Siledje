"""
Module de gestion de la connexion à la base de données SQLite.
Fournit un singleton pour garantir une connexion unique dans toute l'application.

IMPORTANT — Architecture du schéma :
Ce fichier gère UNIQUEMENT la connexion physique à SQLite (ouverture,
pragmas, singleton, fermeture). Il ne crée AUCUNE table métier.

Chaque domaine métier possède son propre repository, responsable de créer
et faire évoluer son propre schéma via une méthode _ensure_schema() :

    - users, roles, audit_logs          → src/database/repositories/user_repository.py
    - licenses                          → src/database/repositories/license_repository.py
    - categories, suppliers, products,
      barcodes, product_components,
      stock_movements                   → src/database/repositories/catalog_repository.py
    - (à venir) clients, sales,
      sale_items, sale_payments,
      returns, return_items             → src/database/repositories/sales_repository.py
    - (à venir) supplier_orders,
      supplier_order_items              → src/database/repositories/supplier_repository.py
    - (à venir) cameras, camera_events,
      alerts                            → src/database/repositories/surveillance_repository.py
    - (à venir) school_levels,
      school_systems, school_classes,
      books                             → src/database/repositories/school_repository.py
    - (à venir) sync_logs, settings     → src/database/repositories/system_repository.py

Chaque repository appelle get_db_connection() pour récupérer cette même
connexion singleton, puis crée ses tables avec CREATE TABLE IF NOT EXISTS.
Cela permet d'ajouter un domaine sans jamais toucher à ce fichier.
"""

import sqlite3
import os
from typing import Optional


class DatabaseConnection:
    """
    Gère la connexion unique (Singleton) à la base de données SQLite.
    Ne définit aucun schéma métier — voir les repositories pour cela.
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
        """Initialise la connexion physique à la base de données."""
        try:
            # Créer le dossier contenant le fichier .db s'il n'existe pas
            db_dir = os.path.dirname(self.db_name)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            self._connection = sqlite3.connect(
                self.db_name,
                check_same_thread=False  # Pour utilisation multi-thread (Qt)
            )

            # Activer les clés étrangères (SQLite les désactive par défaut)
            self._connection.execute("PRAGMA foreign_keys = ON")

            # Retourner les résultats sous forme de sqlite3.Row (accès par nom de colonne)
            self._connection.row_factory = sqlite3.Row

            print(f"✅ Connecté à la base de données : {self.db_name}")

        except sqlite3.Error as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """
        Retourne la connexion active à la base de données.
        Rouvre la connexion si elle a été fermée entre-temps.

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

    def execute_script(self, sql_script: str):
        """
        Exécute un script SQL multi-instructions (utile pour des migrations
        ponctuelles). À utiliser avec précaution.
        """
        if self._connection:
            self._connection.executescript(sql_script)
            self._connection.commit()

    def table_exists(self, table_name: str) -> bool:
        """Vérifie si une table existe déjà dans la base."""
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    def list_tables(self) -> list:
        """Retourne la liste de toutes les tables existantes (hors tables internes SQLite)."""
        cursor = self.get_cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
        return [row["name"] for row in cursor.fetchall()]

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