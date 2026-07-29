"""
Script pour afficher tous les livres et leurs classes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import get_db_connection


def show_books():
    """Affiche tous les livres et leurs classes."""
    
    db = get_db_connection()
    cursor = db.get_cursor()
    
    print("\n" + "=" * 70)
    print("📚 LISTE DES LIVRES ET LEURS CLASSES")
    print("=" * 70)
    
    # Tous les livres avec leurs classes
    cursor.execute("""
        SELECT 
            p.id as product_id,
            p.name as product_name,
            p.is_book,
            b.id as book_id,
            b.title,
            b.subject,
            b.publisher,
            b.isbn,
            b.school_class_id,
            sc.name as class_name,
            sl.name as level_name,
            ss.name as system_name
        FROM products p
        LEFT JOIN books b ON p.id = b.product_id
        LEFT JOIN school_classes sc ON b.school_class_id = sc.id
        LEFT JOIN school_levels sl ON sc.level_id = sl.id
        LEFT JOIN school_systems ss ON sc.system_id = ss.id
        WHERE p.is_book = 1
        ORDER BY p.name
    """)
    
    books = cursor.fetchall()
    
    if not books:
        print("\n❌ Aucun livre trouvé dans la base de données !")
        print("\nPour ajouter un livre :")
        print("  1. Gestion > Gestion de Stock > Ajouter Produit / Livre")
        print("  2. Cocher 'Ceci est un livre'")
        print("  3. Remplir les informations et sélectionner une classe")
        print("  4. Enregistrer")
    else:
        print(f"\n✅ {len(books)} livre(s) trouvé(s) :\n")
        
        for book in books:
            print(f"  📖 {book['product_name']}")
            print(f"     ID Produit : {book['product_id']}")
            print(f"     Titre      : {book['title'] or 'Non défini'}")
            print(f"     Matière    : {book['subject'] or 'Non défini'}")
            print(f"     Éditeur    : {book['publisher'] or 'Non défini'}")
            print(f"     ISBN       : {book['isbn'] or 'Non défini'}")
            
            if book['class_name']:
                print(f"     Classe     : {book['class_name']} ({book['level_name']} / {book['system_name']})")
            else:
                print(f"     Classe     : ❌ AUCUNE CLASSE !")
                print(f"                 Le livre n'apparaîtra pas dans l'accueil.")
            
            print("")
    
    print("=" * 70)
    
    # Livres sans classe
    cursor.execute("""
        SELECT p.id, p.name
        FROM products p
        LEFT JOIN books b ON p.id = b.product_id
        WHERE p.is_book = 1 AND b.id IS NULL
    """)
    
    orphans = cursor.fetchall()
    if orphans:
        print(f"\n⚠️ {len(orphans)} livre(s) sans classe (ne seront pas visibles dans l'accueil) :")
        for o in orphans:
            print(f"   - {o['name']} (ID: {o['id']})")
    
    db.close()


if __name__ == "__main__":
    show_books()