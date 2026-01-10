"""
Gestionnaire de migrations de base de données (OPTIONNEL).

Ce fichier permet d'exécuter automatiquement les migrations.
Tu n'as pas besoin de l'utiliser tout de suite.
"""

import os
import importlib.util
from pathlib import Path
from typing import List
from src.database import get_db_connection


class MigrationManager:
    """
    Gestionnaire pour appliquer les migrations de base de données.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de migrations."""
        self.db = get_db_connection()
        self.migrations_dir = Path(__file__).parent
        self._create_migrations_table()
    
    def _create_migrations_table(self):
        """Crée la table de suivi des migrations si elle n'existe pas."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db.commit()
        except Exception as e:
            print(f"❌ Erreur création table migrations : {e}")
    
    def get_pending_migrations(self) -> List[str]:
        """
        Retourne la liste des migrations non appliquées.
        
        Returns:
            Liste des noms de fichiers de migration à appliquer
        """
        try:
            # Récupérer les migrations déjà appliquées
            cursor = self.db.get_cursor()
            cursor.execute("SELECT filename FROM migrations")
            applied = {row[0] for row in cursor.fetchall()}
            
            # Lister tous les fichiers de migration
            all_migrations = []
            for file in sorted(self.migrations_dir.glob("*.py")):
                if file.name.startswith("__") or file.name == "migration_manager.py":
                    continue
                if file.name not in applied:
                    all_migrations.append(file.name)
            
            return all_migrations
        
        except Exception as e:
            print(f"❌ Erreur récupération migrations : {e}")
            return []
    
    def apply_migration(self, filename: str) -> bool:
        """
        Applique une migration spécifique.
        
        Args:
            filename: Nom du fichier de migration
            
        Returns:
            True si la migration a réussi
        """
        try:
            # Charger le module de migration
            migration_path = self.migrations_dir / filename
            spec = importlib.util.spec_from_file_location("migration", migration_path)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            
            # Appliquer la migration
            print(f"🔄 Application de la migration : {filename}")
            migration.upgrade(self.db.get_connection())
            
            # Enregistrer que la migration a été appliquée
            cursor = self.db.get_cursor()
            cursor.execute(
                "INSERT INTO migrations (filename) VALUES (?)",
                (filename,)
            )
            self.db.commit()
            
            print(f"✅ Migration appliquée : {filename}")
            return True
        
        except Exception as e:
            print(f"❌ Erreur application migration {filename} : {e}")
            self.db.rollback()
            return False
    
    def apply_all_pending(self) -> int:
        """
        Applique toutes les migrations en attente.
        
        Returns:
            Nombre de migrations appliquées
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ Aucune migration en attente")
            return 0
        
        print(f"🔄 {len(pending)} migration(s) en attente")
        
        applied_count = 0
        for filename in pending:
            if self.apply_migration(filename):
                applied_count += 1
        
        print(f"✅ {applied_count}/{len(pending)} migration(s) appliquée(s)")
        return applied_count
    
    def rollback_last(self) -> bool:
        """
        Annule la dernière migration (si le downgrade est implémenté).
        
        Returns:
            True si le rollback a réussi
        """
        try:
            # Récupérer la dernière migration
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT filename FROM migrations 
                ORDER BY applied_at DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                print("⚠️ Aucune migration à annuler")
                return False
            
            filename = row[0]
            
            # Charger le module de migration
            migration_path = self.migrations_dir / filename
            spec = importlib.util.spec_from_file_location("migration", migration_path)
            migration = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration)
            
            # Vérifier si downgrade existe
            if not hasattr(migration, 'downgrade'):
                print(f"⚠️ Pas de fonction downgrade pour {filename}")
                return False
            
            # Appliquer le downgrade
            print(f"🔄 Annulation de la migration : {filename}")
            migration.downgrade(self.db.get_connection())
            
            # Supprimer l'entrée de la table migrations
            cursor.execute("DELETE FROM migrations WHERE filename = ?", (filename,))
            self.db.commit()
            
            print(f"✅ Migration annulée : {filename}")
            return True
        
        except Exception as e:
            print(f"❌ Erreur rollback : {e}")
            self.db.rollback()
            return False
    
    def list_applied_migrations(self) -> List[dict]:
        """
        Liste toutes les migrations appliquées.
        
        Returns:
            Liste des migrations avec leurs dates
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT filename, applied_at 
                FROM migrations 
                ORDER BY applied_at
            """)
            return [
                {'filename': row[0], 'applied_at': row[1]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"❌ Erreur liste migrations : {e}")
            return []


def run_migrations():
    """Fonction utilitaire pour lancer les migrations au démarrage de l'app."""
    manager = MigrationManager()
    manager.apply_all_pending()


if __name__ == "__main__":
    # Si ce fichier est exécuté directement
    print("="*60)
    print("GESTIONNAIRE DE MIGRATIONS")
    print("="*60)
    
    manager = MigrationManager()
    
    print("\n📋 Migrations appliquées :")
    applied = manager.list_applied_migrations()
    if applied:
        for mig in applied:
            print(f"  ✅ {mig['filename']} - {mig['applied_at']}")
    else:
        print("  Aucune migration appliquée")
    
    print("\n🔄 Application des migrations en attente...")
    manager.apply_all_pending()
    
    print("\n" + "="*60)