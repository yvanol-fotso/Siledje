"""
Accès aux données du catalogue produits — conforme au schéma SILEDJE.
Couvre : categories, suppliers, products, barcodes, product_components,
stock_movements.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.database.connection import get_db_connection


class CatalogRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    # ────────────────────────────────────────────────────────────────
    # SCHÉMA — conforme exactement au PDF (Module : Produits et Stock)
    # ────────────────────────────────────────────────────────────────

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        # ── categories ──────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                description TEXT,
                icon TEXT,
                color TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── suppliers ───────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                contact_name TEXT,
                email TEXT,
                phone TEXT,
                phone2 TEXT,
                address TEXT,
                city TEXT,
                payment_terms TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── products (table centrale) ──────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
                buy_price REAL NOT NULL DEFAULT 0,
                sell_price REAL NOT NULL DEFAULT 0,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                min_stock_threshold INTEGER DEFAULT 10,
                packaging_type TEXT DEFAULT 'unitaire',
                units_per_pack INTEGER DEFAULT 1,
                location TEXT,
                image_path TEXT,
                sku TEXT UNIQUE,
                tax_rate REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                is_book INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)")

        # ── barcodes ────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode_text TEXT NOT NULL UNIQUE,
                product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                barcode_type TEXT DEFAULT 'internal',
                is_primary INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_barcodes_text ON barcodes(barcode_text)")

        # ── product_components (composition paquets/cartons) ──────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                child_product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ── stock_movements ─────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL REFERENCES products(id),
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                quantity_before INTEGER NOT NULL,
                quantity_after INTEGER NOT NULL,
                unit_cost REAL,
                reason TEXT,
                reference_id INTEGER,
                reference_type TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_movements_created "
                       "ON stock_movements(created_at)")

        self.db.commit()
        self._seed_default_categories()

    def _seed_default_categories(self):
        """Catégories racines minimales — pas de produits factices."""
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM categories")
        if cursor.fetchone()["c"] > 0:
            return

        defaults = ["Papeterie", "Fournitures", "Manuels Scolaires", "Divers"]
        for name in defaults:
            cursor.execute(
                "INSERT INTO categories (name, is_active) VALUES (?, 1)", (name,)
            )
        self.db.commit()

    # ────────────────────────────────────────────────────────────────
    # CATEGORIES
    # ────────────────────────────────────────────────────────────────

    def get_all_categories(self, active_only: bool = True) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        query = "SELECT * FROM categories"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY sort_order, name"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM categories WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_category(self, name: str, parent_id: int = None, description: str = None,
                         icon: str = None, color: str = None, sort_order: int = 0) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO categories (name, parent_id, description, icon, color, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, parent_id, description, icon, color, sort_order))
        self.db.commit()
        return cursor.lastrowid

    def update_category(self, category_id: int, **fields) -> bool:
        allowed = {'name', 'parent_id', 'description', 'icon', 'color',
                   'sort_order', 'is_active'}
        updates, values = [], []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                values.append(value)
        if not updates:
            return False
        values.append(category_id)
        cursor = self.db.get_cursor()
        cursor.execute(f"UPDATE categories SET {', '.join(updates)} WHERE id = ?", values)
        self.db.commit()
        return True

    # ────────────────────────────────────────────────────────────────
    # SUPPLIERS
    # ────────────────────────────────────────────────────────────────

    def get_all_suppliers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        query = "SELECT * FROM suppliers"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def create_supplier(self, name: str, contact_name: str = None, email: str = None,
                         phone: str = None, phone2: str = None, address: str = None,
                         city: str = None, payment_terms: str = None, notes: str = None) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO suppliers (name, contact_name, email, phone, phone2,
                                    address, city, payment_terms, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, contact_name, email, phone, phone2, address, city, payment_terms, notes))
        self.db.commit()
        return cursor.lastrowid

    def update_supplier(self, supplier_id: int, **fields) -> bool:
        allowed = {'name', 'contact_name', 'email', 'phone', 'phone2', 'address',
                   'city', 'payment_terms', 'notes', 'is_active'}
        updates, values = [], []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                values.append(value)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(supplier_id)
        cursor = self.db.get_cursor()
        cursor.execute(f"UPDATE suppliers SET {', '.join(updates)} WHERE id = ?", values)
        self.db.commit()
        return True

    def set_supplier_active(self, supplier_id: int, is_active: bool):
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE suppliers SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if is_active else 0, supplier_id)
        )
        self.db.commit()

    # ────────────────────────────────────────────────────────────────
    # PRODUCTS
    # ────────────────────────────────────────────────────────────────

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = ?
        """, (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_products(self, active_only: bool = True) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        query = """
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
        """
        if active_only:
            query += " WHERE p.is_active = 1"
        query += " ORDER BY p.name"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        term = f"%{search_term}%"
        cursor.execute("""
            SELECT p.*, c.name as category_name, s.name as supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.is_active = 1
              AND (p.name LIKE ? OR p.sku LIKE ? OR c.name LIKE ?)
            ORDER BY p.name
        """, (term, term, term))
        return [dict(row) for row in cursor.fetchall()]

    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Produits dont le stock est sous leur propre seuil min_stock_threshold."""
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.stock_quantity <= p.min_stock_threshold
            ORDER BY p.stock_quantity ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def create_product(self, name: str, description: str = None, category_id: int = None,
                        supplier_id: int = None, buy_price: float = 0, sell_price: float = 0,
                        stock_quantity: int = 0, min_stock_threshold: int = 10,
                        packaging_type: str = "unitaire", units_per_pack: int = 1,
                        location: str = None, image_path: str = None, sku: str = None,
                        tax_rate: float = 0, is_book: bool = False, notes: str = None) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO products (
                name, description, category_id, supplier_id, buy_price, sell_price,
                stock_quantity, min_stock_threshold, packaging_type, units_per_pack,
                location, image_path, sku, tax_rate, is_book, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, description, category_id, supplier_id, buy_price, sell_price,
              stock_quantity, min_stock_threshold, packaging_type, units_per_pack,
              location, image_path, sku, tax_rate, 1 if is_book else 0, notes))
        self.db.commit()
        return cursor.lastrowid

    def update_product(self, product_id: int, **fields) -> bool:
        allowed = {'name', 'description', 'category_id', 'supplier_id', 'buy_price',
                   'sell_price', 'stock_quantity', 'min_stock_threshold', 'packaging_type',
                   'units_per_pack', 'location', 'image_path', 'sku', 'tax_rate',
                   'is_active', 'is_book', 'notes'}
        updates, values = [], []
        for key, value in fields.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                values.append(value)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(product_id)
        cursor = self.db.get_cursor()
        cursor.execute(f"UPDATE products SET {', '.join(updates)} WHERE id = ?", values)
        self.db.commit()
        return True

    def set_product_active(self, product_id: int, is_active: bool):
        """Désactivation logique — jamais de suppression physique (FK RESTRICT ailleurs)."""
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE products SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if is_active else 0, product_id)
        )
        self.db.commit()

    def sku_exists(self, sku: str, exclude_id: int = None) -> bool:
        if not sku:
            return False
        cursor = self.db.get_cursor()
        if exclude_id:
            cursor.execute("SELECT id FROM products WHERE sku = ? AND id != ?", (sku, exclude_id))
        else:
            cursor.execute("SELECT id FROM products WHERE sku = ?", (sku,))
        return cursor.fetchone() is not None

    # ────────────────────────────────────────────────────────────────
    # BARCODES (relation 1-N avec products)
    # ────────────────────────────────────────────────────────────────

    def get_barcodes_for_product(self, product_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM barcodes WHERE product_id = ?
            ORDER BY is_primary DESC, created_at
        """, (product_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_product_by_barcode(self, barcode_text: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT p.*, b.barcode_text, b.barcode_type, b.is_primary,
                   c.name as category_name, s.name as supplier_name
            FROM barcodes b
            JOIN products p ON b.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE b.barcode_text = ?
        """, (barcode_text,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def barcode_exists(self, barcode_text: str) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT id FROM barcodes WHERE barcode_text = ?", (barcode_text,))
        return cursor.fetchone() is not None

    def add_barcode(self, barcode_text: str, product_id: int,
                     barcode_type: str = "internal", is_primary: bool = False) -> Optional[int]:
        try:
            cursor = self.db.get_cursor()
            if is_primary:
                # Un seul code-barres principal par produit
                cursor.execute(
                    "UPDATE barcodes SET is_primary = 0 WHERE product_id = ?", (product_id,)
                )
            cursor.execute("""
                INSERT INTO barcodes (barcode_text, product_id, barcode_type, is_primary)
                VALUES (?, ?, ?, ?)
            """, (barcode_text, product_id, barcode_type, 1 if is_primary else 0))
            self.db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete_barcode(self, barcode_id: int) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM barcodes WHERE id = ?", (barcode_id,))
        self.db.commit()
        return cursor.rowcount > 0

    def set_primary_barcode(self, product_id: int, barcode_id: int):
        cursor = self.db.get_cursor()
        cursor.execute("UPDATE barcodes SET is_primary = 0 WHERE product_id = ?", (product_id,))
        cursor.execute("UPDATE barcodes SET is_primary = 1 WHERE id = ?", (barcode_id,))
        self.db.commit()

    # ────────────────────────────────────────────────────────────────
    # PRODUCT_COMPONENTS (composition paquets/cartons)
    # ────────────────────────────────────────────────────────────────

    def get_components(self, parent_product_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT pc.*, p.name as child_name, p.sell_price as child_sell_price
            FROM product_components pc
            JOIN products p ON pc.child_product_id = p.id
            WHERE pc.parent_product_id = ?
        """, (parent_product_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_component(self, parent_product_id: int, child_product_id: int, quantity: int) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO product_components (parent_product_id, child_product_id, quantity)
            VALUES (?, ?, ?)
        """, (parent_product_id, child_product_id, quantity))
        self.db.commit()
        return cursor.lastrowid

    def remove_component(self, component_id: int) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM product_components WHERE id = ?", (component_id,))
        self.db.commit()
        return cursor.rowcount > 0

    # ────────────────────────────────────────────────────────────────
    # STOCK_MOVEMENTS (historique + mise à jour de stock atomique)
    # ────────────────────────────────────────────────────────────────

    def adjust_stock(self, product_id: int, quantity_change: int, movement_type: str,
                      user_id: int = None, reason: str = None, unit_cost: float = None,
                      reference_id: int = None, reference_type: str = None,
                      notes: str = None) -> Optional[int]:
        """
        Modifie le stock d'un produit ET trace le mouvement dans stock_movements.
        movement_type : entry / sale / return / adjustment / inventory
        quantity_change : positif = entrée, négatif = sortie
        """
        try:
            cursor = self.db.get_cursor()

            cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                return None
            quantity_before = row["stock_quantity"]
            quantity_after = quantity_before + quantity_change

            cursor.execute("""
                UPDATE products SET stock_quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quantity_after, product_id))

            cursor.execute("""
                INSERT INTO stock_movements (
                    product_id, user_id, movement_type, quantity,
                    quantity_before, quantity_after, unit_cost, reason,
                    reference_id, reference_type, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (product_id, user_id, movement_type, quantity_change,
                  quantity_before, quantity_after, unit_cost, reason,
                  reference_id, reference_type, notes))

            self.db.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Erreur adjust_stock: {e}")
            self.db.rollback()
            return None

    def get_stock_movements(self, product_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        if product_id:
            cursor.execute("""
                SELECT sm.*, p.name as product_name
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                WHERE sm.product_id = ?
                ORDER BY sm.created_at DESC LIMIT ?
            """, (product_id, limit))
        else:
            cursor.execute("""
                SELECT sm.*, p.name as product_name
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                ORDER BY sm.created_at DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]