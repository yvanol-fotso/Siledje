"""
Script pour ajouter toutes les classes manquantes
du système scolaire camerounais dans la base de données.

Systèmes pris en charge :
- Francophone
- Anglophone
"""

import sys
from pathlib import Path

# Ajouter le dossier racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.connection import get_db_connection


def seed_all_classes():
    """Ajoute toutes les classes manquantes dans la base de données."""

    db = get_db_connection()
    cursor = db.get_cursor()

    try:
        # ============================================================
        # 1. RÉCUPÉRER LES NIVEAUX EXISTANTS
        # ============================================================

        cursor.execute("""
            SELECT id, name
            FROM school_levels
        """)

        levels = {
            row["name"].strip().lower(): row["id"]
            for row in cursor.fetchall()
        }

        print("\nNiveaux trouvés :")
        for level_name in levels:
            print(f"  - {level_name}")

        # ============================================================
        # 2. RÉCUPÉRER LES SYSTÈMES EXISTANTS
        # ============================================================

        cursor.execute("""
            SELECT id, name
            FROM school_systems
        """)

        systems = {
            row["name"].strip().lower(): row["id"]
            for row in cursor.fetchall()
        }

        print("\nSystèmes trouvés :")
        for system_name in systems:
            print(f"  - {system_name}")

        # ============================================================
        # 3. DÉFINITION DES CLASSES DU CAMEROUN
        # ============================================================

        all_classes = {

            # MATERNELLE

            ("Maternelle", "Francophone"): [
                "Petite Section",
                "Moyenne Section",
                "Grande Section",
            ],

            ("Maternelle", "Anglophone"): [
                "Nursery 1",
                "Nursery 2",
                "Nursery 3",
            ],

            # PRIMAIRE

            ("Primaire", "Francophone"): [
                "SIL",
                "CP",
                "CE1",
                "CE2",
                "CM1",
                "CM2",
            ],

            ("Primaire", "Anglophone"): [
                "Class 1",
                "Class 2",
                "Class 3",
                "Class 4",
                "Class 5",
                "Class 6",
            ],

            # SECONDAIRE GÉNÉRAL FRANCOPHONE

            ("Secondaire", "Francophone"): [
                "6ème",
                "5ème",
                "4ème",
                "3ème",
                "Seconde",
                "Première",
                "Terminale",
            ],

            # SECONDAIRE GÉNÉRAL ANGLOPHONE

            ("Secondaire", "Anglophone"): [
                "Form 1",
                "Form 2",
                "Form 3",
                "Form 4",
                "Form 5",
                "Lower Sixth",
                "Upper Sixth",
            ],

            # SECONDAIRE TECHNIQUE FRANCOPHONE

            ("Secondaire Technique", "Francophone"): [
                "1ère année",
                "2ème année",
                "3ème année",
                "4ème année",
                "5ème année",
                "6ème année",
                "7ème année",
            ],

            # SECONDAIRE TECHNIQUE ANGLOPHONE

            ("Secondaire Technique", "Anglophone"): [
                "Technical Form 1",
                "Technical Form 2",
                "Technical Form 3",
                "Technical Form 4",
                "Technical Form 5",
                "Technical Lower Sixth",
                "Technical Upper Sixth",
            ],

            # ENSEIGNEMENT SUPÉRIEUR

            ("Supérieur", "Francophone"): [
                "Licence 1",
                "Licence 2",
                "Licence 3",
                "Master 1",
                "Master 2",
                "Doctorat 1",
                "Doctorat 2",
                "Doctorat 3",
            ],

            ("Supérieur", "Anglophone"): [
                "Level 100",
                "Level 200",
                "Level 300",
                "Level 400",
                "Master 1",
                "Master 2",
                "PhD 1",
                "PhD 2",
                "PhD 3",
            ],
        }

        # ============================================================
        # 4. AJOUTER LES CLASSES MANQUANTES
        # ============================================================

        total_added = 0
        total_existing = 0
        missing_configurations = []

        print("\nVérification et ajout des classes...\n")

        for (level_name, system_name), classes in all_classes.items():

            # Recherche insensible aux majuscules/minuscules
            level_id = levels.get(level_name.lower())
            system_id = systems.get(system_name.lower())

            # Vérifier que le niveau existe
            if level_id is None:
                message = (
                    f"Niveau introuvable : "
                    f"'{level_name}' pour le système '{system_name}'"
                )

                print(message)
                missing_configurations.append(message)
                continue

            # Vérifier que le système existe
            if system_id is None:
                message = (
                    f"Système introuvable : "
                    f"'{system_name}'"
                )

                print(message)
                missing_configurations.append(message)
                continue

            # Récupérer les classes déjà enregistrées
            cursor.execute("""
                SELECT name
                FROM school_classes
                WHERE level_id = ?
                AND system_id = ?
            """, (level_id, system_id))

            existing_classes = {
                row["name"].strip().lower()
                for row in cursor.fetchall()
            }

            print(
                f"\n{level_name} "
                f"- {system_name}"
            )

            # Ajouter uniquement les classes absentes
            for sort_order, class_name in enumerate(classes, start=1):

                normalized_name = class_name.strip().lower()

                if normalized_name in existing_classes:

                    print(
                        f"  Déjà existante : "
                        f"{class_name}"
                    )

                    total_existing += 1
                    continue

                cursor.execute("""
                    INSERT INTO school_classes (
                        level_id,
                        system_id,
                        name,
                        sort_order
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    level_id,
                    system_id,
                    class_name,
                    sort_order,
                ))

                print(
                    f"  Ajoutée : "
                    f"{class_name}"
                )

                total_added += 1

        # ============================================================
        # 5. ENREGISTRER LES MODIFICATIONS
        # ============================================================

        db.commit()

        print("\n" + "=" * 65)

        print(
            f"Classes ajoutées : "
            f"{total_added}"
        )

        print(
            f"Classes déjà présentes : "
            f"{total_existing}"
        )

        print("=" * 65)

        # ============================================================
        # 6. AFFICHER LA LISTE FINALE
        # ============================================================

        cursor.execute("""
            SELECT
                sc.name AS classe,
                sl.name AS niveau,
                ss.name AS systeme

            FROM school_classes AS sc

            INNER JOIN school_levels AS sl
                ON sc.level_id = sl.id

            INNER JOIN school_systems AS ss
                ON sc.system_id = ss.id

            ORDER BY
                sl.sort_order,
                ss.name,
                sc.sort_order,
                sc.name
        """)

        rows = cursor.fetchall()

        print("\nLISTE COMPLÈTE DES CLASSES\n")

        current_level = None
        current_system = None

        for row in rows:

            level = row["niveau"]
            system = row["systeme"]
            class_name = row["classe"]

            if (
                level != current_level
                or system != current_system
            ):

                print(
                    f"\n{level} "
                    f"- {system}"
                )

                current_level = level
                current_system = system

            print(
                f"   - {class_name}"
            )

        # ============================================================
        # 7. AFFICHER LES CONFIGURATIONS MANQUANTES
        # ============================================================

        if missing_configurations:

            print(
                "\nCONFIGURATIONS "
                "ABSENTES DE LA BASE :"
            )

            for configuration in missing_configurations:

                print(
                    f"  - {configuration}"
                )

            print(
                "\nLes niveaux concernés "
                "doivent être ajoutés dans "
                "la table school_levels."
            )

        print(
            "\nInitialisation terminée."
        )

    except Exception as error:

        # Annuler toutes les modifications
        db.rollback()

        print(
            "\nErreur pendant "
            "l'initialisation :"
        )

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise

    finally:

        # Fermer le curseur si la méthode existe
        if hasattr(cursor, "close"):
            cursor.close()

        # Fermer la connexion si la méthode existe
        if hasattr(db, "close"):
            db.close()


if __name__ == "__main__":
    seed_all_classes()