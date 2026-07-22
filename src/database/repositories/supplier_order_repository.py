"""
Accès aux commandes fournisseurs — conforme au schéma SILEDJE.
Couvre : supplier_orders, supplier_order_items.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from src.database.connection import get_db_connection


class SupplierOrderRepository:

    def __init__(self):
        self.db = get_db_connection()
        self._ensure_schema()

    def _ensure_schema(self):
        cursor = self.db.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
                created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                order_number TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'pending',
                total_amount REAL DEFAULT 0,
                notes TEXT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_date DATE,
                received_date TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES supplier_orders(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity_ordered INTEGER NOT NULL,
                quantity_received INTEGER DEFAULT 0,
                unit_price REAL NOT NULL,
                notes TEXT
            )
        """)
        self.db.commit()

    def _generate_order_number(self) -> str:
        year = date.today().year
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT COUNT(*) as c FROM supplier_orders WHERE order_number LIKE ?",
            (f"CMD-{year}-%",)
        )
        count = cursor.fetchone()["c"] + 1
        return f"CMD-{year}-{count:03d}"

    def create_order(self, supplier_id: int, created_by: int,
                      items: List[Dict[str, Any]], expected_date: date = None,
                      notes: str = None) -> Optional[int]:
        cursor = self.db.get_cursor()
        order_number = self._generate_order_number()
        total = sum(i["quantity_ordered"] * i["unit_price"] for i in items)

        cursor.execute("""
            INSERT INTO supplier_orders (supplier_id, created_by, order_number,
                                          total_amount, notes, expected_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (supplier_id, created_by, order_number, total, notes,
              expected_date.isoformat() if expected_date else None))
        order_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO supplier_order_items (order_id, product_id,
                                                    quantity_ordered, unit_price, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, item["product_id"], item["quantity_ordered"],
                  item["unit_price"], item.get("notes")))

        self.db.commit()
        return order_id

    def get_orders_for_supplier(self, supplier_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT * FROM supplier_orders WHERE supplier_id = ?
            ORDER BY order_date DESC
        """, (supplier_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT soi.*, p.name as product_name
            FROM supplier_order_items soi
            JOIN products p ON soi.product_id = p.id
            WHERE soi.order_id = ?
        """, (order_id,))
        return [dict(row) for row in cursor.fetchall()]

    def mark_received(self, order_id: int, item_receipts: Dict[int, int]):
        """item_receipts: {order_item_id: quantity_received}"""
        cursor = self.db.get_cursor()
        for item_id, qty in item_receipts.items():
            cursor.execute(
                "UPDATE supplier_order_items SET quantity_received = ? WHERE id = ?",
                (qty, item_id)
            )
        cursor.execute("""
            UPDATE supplier_orders SET status = 'delivered',
                                        received_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (order_id,))
        self.db.commit()