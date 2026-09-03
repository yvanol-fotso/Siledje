"""
Accès aux données des manuels scolaires — conforme au schéma SILEDJE.
Couvre : school_levels, school_systems, school_classes, books.
Seed conforme aux données déjà utilisées par AccueilManager
(Maternelle/Primaire/Secondaire, Anglophone/Francophone).

CENTRALISATION DE LA RESOLUTION DE NOM DE CLASSE
=================================================
Avant, chaque manager qui important des livres (StockManager, FileManager)
avait sa PROPRE logique de tolérance (normalisation accents/casse, cache
local) pour retrouver une classe à partir d'un nom saisi dans un CSV. Deux
copies du même problème = deux endroits à corriger si une règle change.

Toute la logique vit maintenant ICI, et nulle part ailleurs :

  - resolve_class_name(name)  : point d'entrée UNIQUE pour retrouver une
    classe à partir d'un texte libre (CSV, formulaire...). Essaie dans
    l'ordre : correspondance exacte -> alias connu -> nom normalisé
    (accents/casse/espaces ignorés).
  - known_class_names()       : liste triée des noms de classes existants,
    pour construire des messages d'erreur utiles ("classe inconnue, voici
    les noms valides : ...") sans dupliquer de requête ailleurs.
  - CLASS_NAME_ALIASES        : LE seul endroit à modifier si vous voulez
    accepter une nouvelle abréviation (ex: "6eme" est déjà couvert par la
    normalisation, mais "6e" ne l'est pas — il faut un alias explicite
    car ce n'est pas qu'une histoire d'accent, voir plus bas).

Tout le reste de l'application (StockManager, FileManager, futurs
imports) doit appeler self.school_repo.resolve_class_name(...) plutôt que
de réimplémenter sa propre tolérance.
"""

import re
import sqlite3
import unicodedata
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SchoolRepository:

    # ────────────────────────────────────────────────────────────────
    # ALIAS DE NOMS DE CLASSE — SEUL ENDROIT A MODIFIER
    #
    # Clé   : forme abrégée/alternative normalisée (voir _normalize_name)
    # Valeur: nom EXACT tel qu'il existe dans school_classes.name
    #
    # "6e" -> "6ème" n'est PAS une histoire d'accent : "6e" normalisé
    # donne "6e" (2 caractères) alors que "6ème" normalisé donne "6eme"
    # (4 caractères) — ce sont deux écritures différentes du même
    # niveau, donc la normalisation seule ne peut jamais les rapprocher.
    # Si vous voulez accepter une autre abréviation plus tard (ex: "T"
    # pour "Terminale", "2de" pour "2nde"), ajoutez UNE ligne ici — rien
    # à toucher dans StockManager ni FileManager.
    # ────────────────────────────────────────────────────────────────
    CLASS_NAME_ALIASES = {
        "6e": "6ème", "5e": "5ème", "4e": "4ème", "3e": "3ème",
        "2de": "2nde", "1re": "1ère",
        "tle": "Terminale", "term": "Terminale",
    }

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()
        self._class_cache = None  # invalidé à chaque écriture sur school_classes

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sort_order INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS school_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_id INTEGER NOT NULL REFERENCES school_levels(id) ON DELETE CASCADE,
                system_id INTEGER NOT NULL REFERENCES school_systems(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0
            )
        """)

        # ✅ AJOUT de is_active dans books
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL UNIQUE REFERENCES products(id) ON DELETE CASCADE,
                school_class_id INTEGER NOT NULL REFERENCES school_classes(id),
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                publisher TEXT,
                edition TEXT,
                isbn TEXT UNIQUE,
                cover_image_path TEXT,
                price_fcfa REAL,
                intitule TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ✅ AJOUT de la colonne is_active si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE books ADD COLUMN is_active INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # La colonne existe déjà

        try:
            cursor.execute("ALTER TABLE books ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE books ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass

        self.db.commit()
        self._seed_levels_and_systems()

    def _seed_levels_and_systems(self):
        cursor = self.db.get_cursor()

        cursor.execute("SELECT COUNT(*) as c FROM school_levels")
        if cursor.fetchone()["c"] == 0:
            for i, name in enumerate(["Maternelle", "Primaire", "Secondaire"]):
                cursor.execute(
                    "INSERT INTO school_levels (name, sort_order) VALUES (?, ?)", (name, i)
                )

        cursor.execute("SELECT COUNT(*) as c FROM school_systems")
        if cursor.fetchone()["c"] == 0:
            for name in ["Francophone", "Anglophone"]:
                cursor.execute("INSERT INTO school_systems (name) VALUES (?)", (name,))

        self.db.commit()

        cursor.execute("SELECT COUNT(*) as c FROM school_classes")
        if cursor.fetchone()["c"] > 0:
            return

        level_ids = {r["name"]: r["id"] for r in
                     cursor.execute("SELECT id, name FROM school_levels").fetchall()}
        system_ids = {r["name"]: r["id"] for r in
                      cursor.execute("SELECT id, name FROM school_systems").fetchall()}

        classes_map = {
            ("Maternelle", "Anglophone"): ["Nursery 1", "Nursery 2", "Nursery 3"],
            ("Maternelle", "Francophone"): ["Petite Section", "Moyenne Section", "Grande Section"],
            ("Primaire", "Francophone"): ["CP", "CE1", "CE2", "CM1", "CM2"],
            ("Primaire", "Anglophone"): ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"],
            ("Secondaire", "Anglophone"): ["Form 1", "Form 2", "Form 3", "Form 4", "Form 5"],
            ("Secondaire", "Francophone"): ["6ème", "5ème", "4ème", "3ème", "2nde", "1ère", "Terminale"],
        }

        for (level_name, system_name), classes in classes_map.items():
            level_id = level_ids.get(level_name)
            system_id = system_ids.get(system_name)
            if not level_id or not system_id:
                continue
            for i, class_name in enumerate(classes):
                cursor.execute("""
                    INSERT INTO school_classes (level_id, system_id, name, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (level_id, system_id, class_name, i))

        self.db.commit()

    # ── LOOKUPS ──────────────────────────────────────────────────────

    def get_levels(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM school_levels ORDER BY sort_order")
        return [dict(row) for row in cursor.fetchall()]

    def get_systems(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM school_systems ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def get_classes(self, level_name: str, system_name: str) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT sc.* FROM school_classes sc
            JOIN school_levels sl ON sc.level_id = sl.id
            JOIN school_systems ss ON sc.system_id = ss.id
            WHERE sl.name = ? AND ss.name = ?
            ORDER BY sc.sort_order
        """, (level_name, system_name))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_classes(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT sc.id, sc.name, sl.name as level_name, ss.name as system_name
            FROM school_classes sc
            JOIN school_levels sl ON sc.level_id = sl.id
            JOIN school_systems ss ON sc.system_id = ss.id
            ORDER BY sl.sort_order, ss.name, sc.sort_order
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_product_ids_for_class(self, class_id: int) -> set:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT product_id FROM books WHERE school_class_id = ?", (class_id,))
        return {row["product_id"] for row in cursor.fetchall()}

    def get_class_by_name(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Correspondance EXACTE uniquement (comportement historique,
        conservé pour compatibilité). Pour un texte saisi/importé qui
        peut varier en casse/accents/abréviation, utilisez plutôt
        resolve_class_name()."""
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM school_classes WHERE name = ?", (class_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_class_by_id(self, class_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM school_classes WHERE id = ?", (class_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── RESOLUTION TOLERANTE (point d'entrée central) ────────────────

    @staticmethod
    def _normalize_name(s: str) -> str:
        """Ignore accents, casse et espaces/ponctuation. Ne rapproche
        PAS les abreviations differentes (ex: "6e" reste distinct de
        "6eme") — c'est le role de CLASS_NAME_ALIASES."""
        s = (s or "").strip().lower()
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9]", "", s)

    def _classes_by_normalized_name(self) -> Dict[str, Dict[str, Any]]:
        """Cache interne (invalide au prochain get_all_classes() si vous
        appelez invalidate_class_cache() apres une creation/modification
        de classe). Une seule requete SQL par cycle d'import au lieu
        d'une par ligne de CSV."""
        if self._class_cache is None:
            self._class_cache = {
                self._normalize_name(c["name"]): c
                for c in self.get_all_classes()
            }
        return self._class_cache

    def invalidate_class_cache(self):
        """A appeler apres toute creation/renommage de classe, pour que
        resolve_class_name() voie immediatement le changement."""
        self._class_cache = None

    def resolve_class_name(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Point d'entree UNIQUE pour retrouver une classe a partir d'un
        texte libre (CSV importe, saisie utilisateur...). Essaie dans
        l'ordre :
          1. Correspondance exacte (le cas normal, le plus rapide)
          2. Alias connu (CLASS_NAME_ALIASES — "6e" -> "6ème")
          3. Nom normalise (accents/casse/espaces ignores)
        Retourne None si rien ne correspond — a l'appelant de decider
        quoi faire (erreur, message a l'utilisateur, etc.), cette
        methode ne devine jamais au-dela des regles explicites ci-dessus.
        """
        class_name = (class_name or "").strip()
        if not class_name:
            return None

        exact = self.get_class_by_name(class_name)
        if exact:
            return exact

        normalized = self._normalize_name(class_name)

        alias_target = self.CLASS_NAME_ALIASES.get(normalized)
        if alias_target:
            aliased = self.get_class_by_name(alias_target)
            if aliased:
                return aliased

        return self._classes_by_normalized_name().get(normalized)

    def known_class_names(self) -> List[str]:
        """Liste triee des noms de classes existants — utile pour
        construire un message d'erreur explicite quand
        resolve_class_name() ne trouve rien."""
        return sorted({c["name"] for c in self.get_all_classes()})

    # ── BOOKS ────────────────────────────────────────────────────────

    def get_books_for_class(self, school_class_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT b.*, p.name as product_name, p.sell_price, p.stock_quantity
            FROM books b
            JOIN products p ON b.product_id = p.id
            WHERE b.school_class_id = ? AND p.is_active = 1 AND b.is_active = 1
        """, (school_class_id,))
        return [dict(row) for row in cursor.fetchall()]

    def create_book(self, product_id: int, school_class_id: int, title: str,
                     subject: str, publisher: str = None, edition: str = None,
                     isbn: str = None, price_fcfa: float = None, 
                     intitule: str = None, is_active: bool = True) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO books (product_id, school_class_id, title, subject,
                                publisher, edition, isbn, price_fcfa, intitule, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, school_class_id, title, subject, publisher, edition, 
              isbn, price_fcfa, intitule, 1 if is_active else 0))
        self.db.commit()
        return cursor.lastrowid

    def update_book(self, product_id: int, school_class_id: int = None, 
                    title: str = None, subject: str = None, 
                    publisher: str = None, edition: str = None,
                    isbn: str = None, price_fcfa: float = None,
                    intitule: str = None, is_active: bool = None) -> bool:
        cursor = self.db.get_cursor()
        
        updates = []
        values = []
        
        if school_class_id is not None:
            updates.append("school_class_id = ?")
            values.append(school_class_id)
        if title is not None:
            updates.append("title = ?")
            values.append(title)
        if subject is not None:
            updates.append("subject = ?")
            values.append(subject)
        if publisher is not None:
            updates.append("publisher = ?")
            values.append(publisher)
        if edition is not None:
            updates.append("edition = ?")
            values.append(edition)
        if isbn is not None:
            updates.append("isbn = ?")
            values.append(isbn)
        if price_fcfa is not None:
            updates.append("price_fcfa = ?")
            values.append(price_fcfa)
        if intitule is not None:
            updates.append("intitule = ?")
            values.append(intitule)
        if is_active is not None:
            updates.append("is_active = ?")
            values.append(1 if is_active else 0)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(product_id)
        
        cursor.execute(f"""
            UPDATE books SET {', '.join(updates)} WHERE product_id = ?
        """, values)
        self.db.commit()
        return cursor.rowcount > 0

    def set_book_active(self, product_id: int, is_active: bool) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE books SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?
        """, (1 if is_active else 0, product_id))
        self.db.commit()
        return cursor.rowcount > 0

    def get_all_books_with_classes(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Recupere TOUS les livres avec leurs classes."""
        cursor = self.db.get_cursor()
        
        # ✅ Si active_only est False, on ne filtre pas par is_active
        active_condition = " AND p.is_active = 1"  # Toujours filtrer les produits actifs
        
        # ✅ On ne filtre par b.is_active que si active_only est True
        if active_only:
            active_condition += " AND b.is_active = 1"
        
        cursor.execute(f"""
            SELECT 
                b.*,
                p.name as product_name,
                p.sell_price,
                p.stock_quantity,
                sc.name as class_name,
                sl.name as level_name,
                ss.name as system_name
            FROM books b
            JOIN products p ON b.product_id = p.id
            LEFT JOIN school_classes sc ON b.school_class_id = sc.id
            LEFT JOIN school_levels sl ON sc.level_id = sl.id
            LEFT JOIN school_systems ss ON sc.system_id = ss.id
            WHERE p.is_book = 1 {active_condition}
            ORDER BY p.name
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_book_by_product_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT b.*, p.name as product_name, p.sell_price, p.stock_quantity
            FROM books b
            JOIN products p ON b.product_id = p.id
            WHERE b.product_id = ?
        """, (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None