"""
Script pour ajouter la colonne is_active à la table books.
"""

import sys
from pathlib import Path
import sqlite3

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_db_connection


def add_book_active_column():
    """Ajoute la colonne is_active à la table books."""
    
    db = get_db_connection()
    cursor = db.get_cursor()
    
    print("\n" + "=" * 60)
    print("🔧 AJOUT DE LA COLONNE is_active DANS books")
    print("=" * 60)
    
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN is_active INTEGER DEFAULT 1")
        print("✅ Colonne is_active ajoutée avec succès !")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ La colonne is_active existe déjà.")
        else:
            print(f"❌ Erreur: {e}")
    
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✅ Colonne created_at ajoutée avec succès !")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ La colonne created_at existe déjà.")
        else:
            print(f"❌ Erreur: {e}")
    
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✅ Colonne updated_at ajoutée avec succès !")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ La colonne updated_at existe déjà.")
        else:
            print(f"❌ Erreur: {e}")
    
    db.commit()
    
    # Vérifier
    cursor.execute("PRAGMA table_info(books)")
    columns = [row["name"] for row in cursor.fetchall()]
    print(f"\n📋 Colonnes de la table books: {columns}")
    
    db.close()
    print("\n✅ Terminé !")


if __name__ == "__main__":
    add_book_active_column()