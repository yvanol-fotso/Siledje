"""
Accès aux données de vente — conforme au schéma SILEDJE.
Couvre : clients, payment_methods, sales, sale_items, sale_payments,
returns, return_items.
"""

import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SalesRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                email TEXT UNIQUE,
                address TEXT,
                loyalty_points INTEGER DEFAULT 0,
                total_spent REAL DEFAULT 0,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT,
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL UNIQUE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
                subtotal REAL NOT NULL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL DEFAULT 0,
                status TEXT DEFAULT 'completed',
                notes TEXT,
                camera_event_id INTEGER,
                video_timestamp TIMESTAMP,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                total_price REAL NOT NULL,
                product_name_snap TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
                payment_method_id INTEGER REFERENCES payment_methods(id),
                amount REAL NOT NULL,
                reference TEXT,
                paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_sale_id INTEGER NOT NULL REFERENCES sales(id),
                processed_by INTEGER NOT NULL REFERENCES users(id),
                approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                reason TEXT NOT NULL,
                total_refund REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS return_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL REFERENCES returns(id) ON DELETE CASCADE,
                sale_item_id INTEGER NOT NULL REFERENCES sale_items(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL,
                refund_amount REAL NOT NULL
            )
        """)

        self.db.commit()
        self._seed_payment_methods()

    def _seed_payment_methods(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM payment_methods")
        if cursor.fetchone()["c"] > 0:
            return
        defaults = [
            ("Espèces", 1), ("Carte bancaire", 2), ("M-Pesa", 3),
            ("Orange Money", 4), ("MTN Mobile Money", 5), ("Virement", 6),
        ]
        for name, order in defaults:
            cursor.execute(
                "INSERT INTO payment_methods (name, sort_order) VALUES (?, ?)",
                (name, order)
            )
        self.db.commit()

    # ── PAYMENT METHODS ─────────────────────────────────────────────

    def get_payment_methods(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT * FROM payment_methods WHERE is_active = 1 ORDER BY sort_order"
        )
        return [dict(row) for row in cursor.fetchall()]

    # ── CLIENTS ──────────────────────────────────────────────────────

    def get_client_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        if not phone:
            return None
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM clients WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_or_create_client(self, name: str, phone: str) -> Optional[int]:
        existing = self.get_client_by_phone(phone)
        if existing:
            return existing["id"]
        cursor = self.db.get_cursor()
        cursor.execute(
            "INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone)
        )
        self.db.commit()
        return cursor.lastrowid

    def add_client_spending(self, client_id: int, amount: float):
        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE clients SET total_spent = total_spent + ?,
                                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (amount, client_id))
        self.db.commit()

    def get_all_clients(self) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM clients WHERE is_active = 1 ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    # ── VENTES ───────────────────────────────────────────────────────

    def _generate_invoice_number(self) -> str:
        year = datetime.now().year
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT COUNT(*) as c FROM sales WHERE invoice_number LIKE ?",
            (f"INV-{year}-%",)
        )
        count = cursor.fetchone()["c"] + 1
        return f"INV-{year}-{count:05d}"

    def create_sale(self, user_id: int, items: List[Dict[str, Any]],
                     payment_method_id: int, client_id: int = None,
                     subtotal: float = 0, tax_amount: float = 0,
                     discount_amount: float = 0, total_amount: float = 0,
                     notes: str = None) -> Optional[Dict[str, Any]]:
        """
        items: [{product_id, quantity, unit_price, discount, total_price, product_name_snap}]
        Retourne {"sale_id": int, "invoice_number": str} ou None en cas d'échec.
        """
        try:
            cursor = self.db.get_cursor()
            invoice_number = self._generate_invoice_number()

            cursor.execute("""
                INSERT INTO sales (invoice_number, user_id, client_id, subtotal,
                                    tax_amount, discount_amount, total_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (invoice_number, user_id, client_id, subtotal, tax_amount,
                  discount_amount, total_amount, notes))
            sale_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price,
                                             discount, total_price, product_name_snap)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sale_id, item["product_id"], item["quantity"], item["unit_price"],
                      item.get("discount", 0), item["total_price"], item.get("product_name_snap")))

            cursor.execute("""
                INSERT INTO sale_payments (sale_id, payment_method_id, amount)
                VALUES (?, ?, ?)
            """, (sale_id, payment_method_id, total_amount))

            self.db.commit()

            if client_id:
                self.add_client_spending(client_id, total_amount)

            return {"sale_id": sale_id, "invoice_number": invoice_number}
        except sqlite3.Error as e:
            print(f" Erreur create_sale: {e}")
            self.db.rollback()
            return None

    def get_sale_by_id(self, sale_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT s.*, c.name as client_name, c.phone as client_phone,
                   pm.name as payment_method_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN sale_payments sp ON sp.sale_id = s.id
            LEFT JOIN payment_methods pm ON sp.payment_method_id = pm.id
            WHERE s.id = ?
        """, (sale_id,))
        row = cursor.fetchone()
        if not row:
            return None
        sale = dict(row)
        cursor.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,))
        sale["items"] = [dict(r) for r in cursor.fetchall()]
        return sale

    def get_sales_between(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT s.*, c.name as client_name, pm.name as payment_method_name
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            LEFT JOIN sale_payments sp ON sp.sale_id = s.id
            LEFT JOIN payment_methods pm ON sp.payment_method_id = pm.id
            WHERE date(s.sale_date) BETWEEN date(?) AND date(?)
            ORDER BY s.sale_date DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        sales = [dict(row) for row in cursor.fetchall()]

        for sale in sales:
            cursor.execute(
                "SELECT * FROM sale_items WHERE sale_id = ?", (sale["id"],)
            )
            sale["items"] = [dict(r) for r in cursor.fetchall()]
        return sales

    def count_sales(self) -> int:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT COUNT(*) as c FROM sales")
        return cursor.fetchone()["c"]

    # ── RETOURS ──────────────────────────────────────────────────────

    def create_return(self, original_sale_id: int, processed_by: int, reason: str,
                       total_refund: float, items: List[Dict[str, Any]]) -> Optional[int]:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO returns (original_sale_id, processed_by, reason, total_refund)
                VALUES (?, ?, ?, ?)
            """, (original_sale_id, processed_by, reason, total_refund))
            return_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO return_items (return_id, sale_item_id, product_id,
                                               quantity, refund_amount)
                    VALUES (?, ?, ?, ?, ?)
                """, (return_id, item["sale_item_id"], item["product_id"],
                      item["quantity"], item["refund_amount"]))

            self.db.commit()
            return return_id
        except sqlite3.Error as e:
            print(f" Erreur create_return: {e}")
            self.db.rollback()
            return None