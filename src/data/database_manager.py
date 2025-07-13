import sqlite3


class DatabaseManager:
    """
    Gère les interactions avec la base de données SQLite.
    Problème résolu: Persistance et récupération des données produit/code-barres.
    """

    def __init__(self, db_name="librairie.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connecté à la base de données : {self.db_name}")
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données : {e}")

    def _create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT,
                    price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS barcodes (
                    barcode_test TEXT PRIMARY KEY,
                    product_id INTEGER,
                    type TEXT, -- 'external' or 'internal'
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            self.conn.commit()
            print("Tables vérifiées/créées.")
        except sqlite3.Error as e:
            print(f"Erreur lors de la création des tables : {e}")

    def add_product(self, name, category, price, stock_quantity):
        try:
            self.cursor.execute(
                "INSERT INTO products (name, category, price, stock_quantity) VALUES (?, ?, ?, ?)",
                (name, category, price, stock_quantity)
            )
            self.conn.commit()
            product_id = self.cursor.lastrowid
            print(f"Produit '{name}' ajouté avec ID: {product_id}")
            return product_id
        except sqlite3.Error as e:
            print(f"Erreur lors de l'ajout du produit : {e}")
            return None

    def get_product_by_barcode(self, barcode):
        try:
            self.cursor.execute("""
                SELECT p.id, p.name, p.category, p.price, p.stock_quantity, b.barcode_test
                FROM products p
                JOIN barcodes b ON p.id = b.product_id
                WHERE b.barcode_test = ?
            """, (barcode,))
            row = self.cursor.fetchone()
            if row:
                product_data = {
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "price": row[3],
                    "stock_quantity": row[4],
                    "barcode_test": row[5]
                }
                return product_data
            return None
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération du produit par code-barres : {e}")
            return None

    def associate_barcode_with_product(self, barcode, product_id, barcode_type='internal'):
        try:
            self.cursor.execute(
                "INSERT INTO barcodes (barcode_test, product_id, type) VALUES (?, ?, ?)",
                (barcode, product_id, barcode_type)
            )
            self.conn.commit()
            print(f"Code-barres '{barcode}' associé au produit ID: {product_id}")
            return True
        except sqlite3.IntegrityError:
            print(f"Erreur: Le code-barres '{barcode}' existe déjà.")
            return False
        except sqlite3.Error as e:
            print(f"Erreur lors de l'association du code-barres : {e}")
            return False

    def update_product_stock(self, product_id, quantity_change):
        try:
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (quantity_change, product_id)
            )
            self.conn.commit()
            print(f"Stock du produit ID {product_id} mis à jour de {quantity_change}.")
            return True
        except sqlite3.Error as e:
            print(f"Erreur lors de la mise à jour du stock : {e}")
            return False

    def get_all_products(self):
        try:
            self.cursor.execute("SELECT id, name, category, price, stock_quantity FROM products")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération de tous les produits : {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("Connexion à la base de données fermée.")