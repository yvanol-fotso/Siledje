import sqlite3
from typing import Optional, List, Dict
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class DatabaseManager(QObject):
    database_error = Signal(str)

    def __init__(self, db_path: str = "data/app.db"):
        super().__init__()
        self.db_path = Path(db_path)
        self.connection = None
        self._setup_database()

    def _setup_database(self):
        """Initialise la base de données et les tables si nécessaire"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self._create_tables()
        except sqlite3.Error as e:
            self.database_error.emit(f"Erreur DB: {str(e)}")

    def _create_tables(self):
        """Crée les tables principales"""
        tables = [
            """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                price REAL,
                barcode_test TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                total_price REAL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )""",
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                last_login TIMESTAMP
            )"""
        ]

        with self.connection:
            cursor = self.connection.cursor()
            for table in tables:
                cursor.execute(table)

    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[Dict]]:
        """Exécute une requête SELECT et retourne les résultats"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            self.database_error.emit(f"Query error: {str(e)}")
            return None

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Exécute une requête INSERT/UPDATE/DELETE"""
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(query, params)
                return True
        except sqlite3.Error as e:
            self.database_error.emit(f"Update error: {str(e)}")
            return False

    def backup_database(self, backup_path: str) -> bool:
        """Crée une sauvegarde de la base de données"""
        try:
            new_conn = sqlite3.connect(backup_path)
            with new_conn:
                self.connection.backup(new_conn)
            return True
        except sqlite3.Error as e:
            self.database_error.emit(f"Backup error: {str(e)}")
            return False

    def close(self):
        """Ferme proprement la connexion"""
        if self.connection:
            self.connection.close()