"""
Dossier des migrations de base de données.

Les migrations permettent de modifier la structure de la base de données
de manière contrôlée et versionnée.

Format des fichiers de migration :
- 001_nom_descriptif.py
- 002_autre_migration.py
- etc.

Chaque fichier doit contenir une fonction upgrade(connection).
"""

# Ce fichier permet à Python de reconnaître ce dossier comme un package