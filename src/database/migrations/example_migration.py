"""
Exemple de migration - Ajouter une colonne description aux produits.

Ce fichier montre comment créer une migration.
Renommer ce fichier en : 001_add_product_description.py quand tu veux l'utiliser.
"""

def upgrade(connection):
    """
    Applique la migration : Ajoute une colonne 'description' à la table products.
    
    Args:
        connection: Connexion SQLite active
    """
    try:
        cursor = connection.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'description' not in columns:
            # Ajouter la colonne description
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN description TEXT
            """)
            connection.commit()
            print("✅ Migration appliquée : colonne 'description' ajoutée")
        else:
            print("⚠️ Migration déjà appliquée : colonne 'description' existe")
    
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        connection.rollback()
        raise


def downgrade(connection):
    """
    Annule la migration (optionnel).
    
    Note: SQLite ne supporte pas DROP COLUMN facilement,
    il faudrait recréer la table entière.
    
    Args:
        connection: Connexion SQLite active
    """
    print("⚠️ Downgrade non supporté pour cette migration (SQLite limitation)")
    # Pour SQLite, il faudrait :
    # 1. Créer une nouvelle table sans la colonne
    # 2. Copier les données
    # 3. Supprimer l'ancienne table
    # 4. Renommer la nouvelle table