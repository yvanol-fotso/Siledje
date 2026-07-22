"""
Accès aux données des manuels scolaires — conforme au schéma SILEDJE.
Couvre : school_levels, school_systems, school_classes, books.
Seed conforme aux données déjà utilisées par AccueilManager
(Maternelle/Primaire/Secondaire, Anglophone/Francophone).
"""

from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SchoolRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

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
                intitule TEXT
            )
        """)

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

        # Classes standard par niveau/système (reprend celles déjà vues dans AccueilManager)
        cursor.execute("SELECT COUNT(*) as c FROM school_classes")
        if cursor.fetchone()["c"] > 0:
            return

        level_ids = {r["name"]: r["id"] for r in
                     cursor.execute("SELECT id, name FROM school_levels").fetchall()}
        system_ids = {r["name"]: r["id"] for r in
                      cursor.execute("SELECT id, name FROM school_systems").fetchall()}

        classes_map = {
            ("Maternelle", "Anglophone"): ["Nursery 1", "Nursery 2", "Nursery 3"],
            ("Maternelle", "Francophone"): ["Petite Section", "Grande Section"],
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

    # ── BOOKS ────────────────────────────────────────────────────────

    def get_books_for_class(self, school_class_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT b.*, p.name as product_name, p.sell_price, p.stock_quantity
            FROM books b
            JOIN products p ON b.product_id = p.id
            WHERE b.school_class_id = ? AND p.is_active = 1
        """, (school_class_id,))
        return [dict(row) for row in cursor.fetchall()]

    def create_book(self, product_id: int, school_class_id: int, title: str,
                     subject: str, publisher: str = None, edition: str = None,
                     isbn: str = None, price_fcfa: float = None) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO books (product_id, school_class_id, title, subject,
                                publisher, edition, isbn, price_fcfa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (product_id, school_class_id, title, subject, publisher, edition, isbn, price_fcfa))
        self.db.commit()
        return cursor.lastrowid