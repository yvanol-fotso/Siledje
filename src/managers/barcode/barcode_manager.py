"""
Module de gestion des codes-barres et produits.
Refactorisé pour utiliser la base de données principale (librairie.db).
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

import barcode
from barcode.writer import ImageWriter

# Import depuis le système de compatibilité
from src.utils.compat import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QGroupBox, QScrollArea,
    QSizePolicy, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QDateEdit, Qt, Signal, QSize,
    QPixmap, QIcon, QFont, QDoubleValidator, QIntValidator, QDate
)

# Import de la configuration centralisée
from src.utils.config import get_config


# --- 1. Database Management (BarcodeDatabase) ---
class BarcodeDatabase:
    """
    Gestionnaire SQLite pour les codes-barres.
    Utilise la base de données principale définie dans config.json.
    """

    def __init__(self, db_path=None):
        """
        Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin optionnel vers la BD (sinon utilise config.json)
        """
        # Récupérer la configuration
        self.config = get_config()
        
        # Utiliser le chemin de la BD depuis config.json
        if db_path is None:
            self.db_path = self.config.db_path
        else:
            self.db_path = Path(db_path)
        
        # S'assurer que le dossier data existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
        self._connect()
        self._init_db()
        
        print(f"✅ [BarcodeDatabase] Connecté à : {self.db_path}")

    def _connect(self):
        """Établit la connexion à la base de données."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Connexion à la base de données : {self.db_path}")
        except sqlite3.Error as e:
            QMessageBox.critical(
                None, 
                "Erreur BD", 
                f"Impossible de se connecter à la base de données : {e}"
            )
            raise SystemExit(1)

    def _init_db(self):
        """
        Crée les tables si elles n'existent pas.
        Compatible avec la structure existante de librairie.db.
        """
        cursor = self.conn.cursor()
        
        # Table products
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                price REAL DEFAULT 0.0,
                stock INTEGER DEFAULT 0,
                is_internal_barcode BOOLEAN DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Table sales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_contact TEXT,
                total_amount REAL NOT NULL,
                sale_date TEXT NOT NULL
            )
        """)
        
        # Table sale_items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                barcode TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            )
        """)
        
        self.conn.commit()
        print("✅ Tables de codes-barres vérifiées/créées.")

    def add_product(self, barcode, name, category="", price=0.0, stock=0, is_internal_barcode=False):
        """Ajoute un nouveau produit à la base de données."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """INSERT INTO products 
                   (barcode, name, category, price, stock, is_internal_barcode, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (barcode, name, category, price, stock, 
                 1 if is_internal_barcode else 0, now, now)
            )
            self.conn.commit()
            print(f"✅ Produit ajouté : {name} ({barcode})")
            return True
        except sqlite3.IntegrityError:
            QMessageBox.warning(
                None, 
                "Erreur", 
                f"Le code-barres '{barcode}' existe déjà pour un autre produit."
            )
            return False
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Erreur BD", f"Erreur lors de l'ajout : {e}")
            return False

    def get_product(self, barcode):
        """Récupère un produit par son code-barres."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
        return cursor.fetchone()

    def get_product_by_id(self, product_id):
        """Récupère un produit par son ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        return cursor.fetchone()

    def update_stock(self, barcode, quantity_change):
        """
        Met à jour le stock d'un produit.
        
        Args:
            barcode: Code-barres du produit
            quantity_change: Changement de quantité (peut être négatif)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE products SET stock = stock + ?, updated_at = ? WHERE barcode=?",
                (quantity_change, datetime.now().isoformat(), barcode)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Erreur BD", f"Erreur mise à jour stock : {e}")
            return False

    def update_product_details(self, product_id, name, category, price, stock):
        """Met à jour les détails d'un produit."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """UPDATE products 
                   SET name=?, category=?, price=?, stock=?, updated_at=? 
                   WHERE id=?""",
                (name, category, price, stock, datetime.now().isoformat(), product_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Erreur BD", f"Erreur mise à jour : {e}")
            return False

    def delete_product(self, product_id):
        """Supprime un produit par son ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Erreur BD", f"Erreur suppression : {e}")
            return False

    def get_all_products(self):
        """Récupère tous les produits."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name ASC")
        return cursor.fetchall()

    def add_sale(self, customer_name, customer_contact, total_amount, cart_items):
        """Enregistre une nouvelle vente avec ses articles."""
        try:
            cursor = self.conn.cursor()
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            sale_date = datetime.now().isoformat()

            # Insérer la vente
            cursor.execute(
                """INSERT INTO sales 
                   (invoice_number, customer_name, customer_contact, total_amount, sale_date) 
                   VALUES (?, ?, ?, ?, ?)""",
                (invoice_number, customer_name, customer_contact, total_amount, sale_date)
            )
            sale_id = cursor.lastrowid

            # Insérer les articles de la vente
            for item in cart_items:
                cursor.execute(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, barcode, product_name, quantity, price_per_unit) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (sale_id, item['id'], item['barcode'], item['name'], 
                     item['quantity'], item['price'])
                )
                # Décrémenter le stock
                self.update_stock(item['barcode'], -item['quantity'])

            self.conn.commit()
            print(f"✅ Vente enregistrée : {invoice_number}")
            return invoice_number
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Erreur BD", f"Erreur vente : {e}")
            self.conn.rollback()
            return None

    def get_all_sales(self, start_date=None, end_date=None, customer_name_filter=None):
        """Récupère toutes les ventes avec filtres optionnels."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM sales"
        params = []
        conditions = []

        if start_date:
            conditions.append("sale_date >= ?")
            params.append(start_date.toPython().isoformat())
            
        if end_date:
            conditions.append("sale_date < ?")
            params.append((end_date.toPython() + timedelta(days=1)).isoformat())

        if customer_name_filter:
            conditions.append("customer_name LIKE ?")
            params.append(f"%{customer_name_filter}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY sale_date DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_sale_items(self, sale_id):
        """Récupère les articles d'une vente spécifique."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
        return cursor.fetchall()

    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
            print("✅ Connexion BD fermée.")


# --- 2. Tab: Gestion Produits et Codes-Barres ---
class ProductBarcodeManagementTab(QWidget):
    """
    Interface pour ajouter des produits (avec codes externes ou internes générés)
    et mettre à jour les produits existants via scan.
    """

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_barcode_for_print = None
        self.current_product_name_for_print = None

        self.setup_ui()
        self.setup_connections()
        self._create_barcodes_directory()

    def _create_barcodes_directory(self):
        """Crée le dossier pour les images de codes-barres."""
        config = get_config()
        self.barcodes_dir = config.base_dir / "barcodes"
        self.barcodes_dir.mkdir(exist_ok=True)
        print(f"✅ Dossier codes-barres : {self.barcodes_dir}")

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Section scan/recherche code-barres externe
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit par Code-Barres")
        scan_layout = QVBoxLayout(scan_group)

        # Champ de saisie + boutons
        scan_input_buttons_layout = QHBoxLayout()
        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText("Scan ou saisie d'un code-barres existant...")
        self.external_barcode_input.returnPressed.connect(self._handle_external_barcode_input)

        self.search_btn = QPushButton("Rechercher")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))
        self.search_btn.clicked.connect(self._handle_external_barcode_input)

        self.scan_btn = QPushButton("Scanner")
        self.scan_btn.setIcon(QIcon.fromTheme("camera-web"))
        self.scan_btn.setStyleSheet("background-color: #2196F3;")
        self.scan_btn.clicked.connect(self._simulate_scan_and_handle)

        scan_input_buttons_layout.addWidget(self.external_barcode_input)
        scan_input_buttons_layout.addWidget(self.search_btn)
        scan_input_buttons_layout.addWidget(self.scan_btn)

        self.scan_product_status = QLabel(
            "Utilisez le champ ci-dessus pour saisir un code-barres et rechercher, "
            "ou cliquez sur 'Scanner' pour simuler un scan."
        )
        self.scan_product_status.setWordWrap(True)

        scan_layout.addLayout(scan_input_buttons_layout)
        scan_layout.addWidget(self.scan_product_status)

        # Formulaire détails produit
        self.product_form_layout = QFormLayout()

        self.product_id_hidden = QLabel("")
        self.product_id_hidden.setVisible(False)

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nom complet du produit")

        self.product_category_combo = QComboBox()
        self.product_category_combo.addItems([
            "Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"
        ])

        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText("0.00")
        self.product_price_input.setValidator(QDoubleValidator(0, 99999.99, 2))

        self.product_stock_input = QLineEdit()
        self.product_stock_input.setPlaceholderText("0")
        self.product_stock_input.setValidator(QIntValidator(0, 999999))

        self.product_form_layout.addRow("Nom:", self.product_name_input)
        self.product_form_layout.addRow("Catégorie:", self.product_category_combo)
        self.product_form_layout.addRow("Prix unitaire:", self.product_price_input)
        self.product_form_layout.addRow("Quantité en stock:", self.product_stock_input)

        self.save_product_btn = QPushButton("Ajouter Produit (avec code scanné/saisi)")
        self.save_product_btn.setStyleSheet("background-color: #28a745;")
        self.save_product_btn.clicked.connect(self._save_scanned_or_new_product)

        scan_layout.addLayout(self.product_form_layout)
        scan_layout.addWidget(self.save_product_btn)

        # Section génération code-barres interne
        gen_group = QGroupBox("Générer un Code-Barre Interne (produits sans code)")
        gen_layout = QVBoxLayout(gen_group)

        self.generate_internal_btn = QPushButton("Générer & Enregistrer Code Interne")
        self.generate_internal_btn.setIcon(QIcon.fromTheme("document-new"))
        self.generate_internal_btn.clicked.connect(self._generate_internal_barcode)

        self.barcode_preview = QLabel()
        self.barcode_preview.setAlignment(Qt.AlignCenter)
        self.barcode_preview.setMinimumHeight(120)
        self.barcode_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.barcode_value_display = QLabel("<i>Code-barres généré affiché ici</i>")
        self.barcode_value_display.setAlignment(Qt.AlignCenter)
        self.barcode_value_display.setFont(QFont("Courier New", 12))

        self.print_internal_btn = QPushButton("Imprimer l'Étiquette Interne")
        self.print_internal_btn.setObjectName("printButton")
        self.print_internal_btn.setIcon(QIcon.fromTheme("document-print"))
        self.print_internal_btn.setEnabled(False)
        self.print_internal_btn.clicked.connect(self._print_generated_barcode)

        gen_layout.addWidget(self.generate_internal_btn)
        gen_layout.addSpacing(15)
        gen_layout.addWidget(self.barcode_preview)
        gen_layout.addWidget(self.barcode_value_display)
        gen_layout.addSpacing(15)
        gen_layout.addWidget(self.print_internal_btn)

        main_layout.addWidget(scan_group)
        main_layout.addWidget(gen_group)
        main_layout.addStretch()

        self._clear_product_form()

    def setup_connections(self):
        pass

    def _simulate_scan_and_handle(self):
        """Simule un scan de code-barres (génère un code aléatoire)."""
        simulated_barcode = f"{random.randint(1000000000000, 9999999999999)}"
        self.external_barcode_input.setText(simulated_barcode)
        self._handle_external_barcode_input()

    def _handle_external_barcode_input(self):
        """Traite le code-barres externe saisi/scanné."""
        barcode_value = self.external_barcode_input.text().strip()
        if not barcode_value:
            self.scan_product_status.setText(
                "<span style='color: red;'>Veuillez entrer un code-barres pour rechercher.</span>"
            )
            self._clear_product_form(clear_input_field=False)
            return

        product = self.db.get_product(barcode_value)
        if product:
            # Produit trouvé - mode édition
            self.product_id_hidden.setText(str(product['id']))
            self.product_name_input.setText(product['name'])
            self.product_category_combo.setCurrentText(product['category'] or "Divers")
            self.product_price_input.setText(str(product['price']))
            self.product_stock_input.setText(str(product['stock']))
            self.scan_product_status.setText(
                f"Produit trouvé: <b>{product['name']}</b>. "
                f"Modifiez les détails si nécessaire."
            )
            self.save_product_btn.setText("Mettre à jour Produit")
        else:
            # Produit non trouvé - mode ajout
            self.product_id_hidden.setText("")
            self.scan_product_status.setText(
                f"Code-barres <b>{barcode_value}</b> non trouvé. "
                f"Remplissez les détails pour ajouter ce nouveau produit."
            )
            self.save_product_btn.setText("Ajouter Nouveau Produit")

    def _save_scanned_or_new_product(self):
        """Sauvegarde ou met à jour un produit avec le code-barres scanné."""
        barcode_value = self.external_barcode_input.text().strip()
        if not barcode_value:
            QMessageBox.warning(
                self, "Erreur",
                "Le code-barres est manquant. Scannez/saisissez un code d'abord."
            )
            return

        name = self.product_name_input.text().strip()
        category = self.product_category_combo.currentText()

        try:
            price = float(self.product_price_input.text().strip() or "0")
            stock = int(self.product_stock_input.text().strip() or "0")
        except ValueError:
            QMessageBox.warning(
                self, "Erreur",
                "Le prix et le stock doivent être des nombres valides."
            )
            return

        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire.")
            return

        product_id = self.product_id_hidden.text()
        if product_id:
            # Mise à jour
            if self.db.update_product_details(int(product_id), name, category, price, stock):
                QMessageBox.information(self, "Succès", f"Produit '{name}' mis à jour.")
            else:
                QMessageBox.warning(self, "Erreur", f"Échec mise à jour '{name}'.")
        else:
            # Ajout
            if self.db.add_product(barcode_value, name, category, price, stock, False):
                QMessageBox.information(
                    self, "Succès",
                    f"Produit '{name}' ajouté avec code: {barcode_value}"
                )
            else:
                QMessageBox.warning(self, "Erreur", f"Échec ajout '{name}'.")

        self._clear_product_form(clear_input_field=True)
        self.scan_product_status.setText("Prêt pour un nouveau scan ou ajout.")
        self.save_product_btn.setText("Ajouter Produit (avec code scanné/saisi)")

    def _generate_internal_barcode(self):
        """Génère un code-barres interne pour un nouveau produit."""
        name = self.product_name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Erreur",
                "Veuillez entrer un nom de produit pour générer un code interne."
            )
            return

        try:
            price = float(self.product_price_input.text().strip() or "0")
            stock = int(self.product_stock_input.text().strip() or "0")
        except ValueError:
            QMessageBox.warning(
                self, "Erreur",
                "Valeurs numériques invalides pour prix et/ou stock."
            )
            return

        category = self.product_category_combo.currentText()

        # Générer code unique (préfixe LIB)
        new_barcode = f"LIB{random.randint(100000, 999999)}"
        while self.db.get_product(new_barcode):
            new_barcode = f"LIB{random.randint(100000, 999999)}"

        # Enregistrer le produit
        if self.db.add_product(new_barcode, name, category, price, stock, True):
            try:
                # Générer l'image du code-barres
                ean = barcode.get('code128', new_barcode, writer=ImageWriter())
                filename = self.barcodes_dir / new_barcode
                ean.save(str(filename))

                # Afficher l'aperçu
                pixmap = QPixmap(str(filename) + ".png")
                self.barcode_preview.setPixmap(
                    pixmap.scaledToWidth(300, Qt.SmoothTransformation)
                )
                self.barcode_value_display.setText(new_barcode)
                self.current_barcode_for_print = new_barcode
                self.current_product_name_for_print = name
                self.print_internal_btn.setEnabled(True)

                QMessageBox.information(
                    self, "Succès",
                    f"Produit '{name}' enregistré avec code interne:\n{new_barcode}"
                )
                self._clear_product_form(clear_input_field=True)
            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur",
                    f"Erreur lors de la génération de l'image: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self, "Erreur",
                "Impossible d'enregistrer ce produit."
            )

    def _print_generated_barcode(self):
        """Simule l'impression de l'étiquette code-barres."""
        if self.current_barcode_for_print and self.current_product_name_for_print:
            QMessageBox.information(
                self, "Impression d'Étiquette",
                f"Simulation d'impression pour:\n"
                f"Nom: {self.current_product_name_for_print}\n"
                f"Code: {self.current_barcode_for_print}\n"
                f"Vérifiez le dossier 'barcodes' pour l'image."
            )
        else:
            QMessageBox.warning(
                self, "Rien à Imprimer",
                "Aucun code-barres interne généré récemment."
            )

    def _clear_product_form(self, clear_input_field=True):
        """Réinitialise le formulaire produit."""
        if clear_input_field:
            self.external_barcode_input.clear()
            self.scan_product_status.setText(
                "Utilisez le champ ci-dessus pour scanner ou saisir un code-barres."
            )
            self.save_product_btn.setText("Ajouter Produit (avec code scanné/saisi)")

        self.product_id_hidden.setText("")
        self.product_name_input.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_price_input.clear()
        self.product_stock_input.clear()
        self.barcode_preview.clear()
        self.barcode_value_display.setText("<i>Code-barres généré affiché ici</i>")
        self.print_internal_btn.setEnabled(False)
        self.current_barcode_for_print = None
        self.current_product_name_for_print = None


# --- 3. Tab: Audit et Gestion des Codes-Barres ---
class AuditBarcodeTab(QWidget):
    """Interface pour lister, visualiser et éditer les détails des produits."""

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.setup_connections()
        self.load_products()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Code-Barres", "Nom", "Catégorie", "Prix", "Stock", "Interne"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Actualiser la Liste")
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.edit_btn = QPushButton("Éditer le Produit Sélectionné")
        self.edit_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.delete_btn = QPushButton("Supprimer le Produit Sélectionné")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))

        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()

        main_layout.addWidget(self.table)
        main_layout.addLayout(btn_layout)

    def setup_connections(self):
        self.refresh_btn.clicked.connect(self.load_products)
        self.edit_btn.clicked.connect(self.edit_selected_product)
        self.delete_btn.clicked.connect(self.delete_selected_product)

    def load_products(self):
        """Charge tous les produits dans le tableau."""
        products = self.db.get_all_products()
        self.table.setRowCount(len(products))
        
        for row_idx, product in enumerate(products):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(product['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(product['barcode']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(product['name']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(product['category']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{product['price']:.2f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(product['stock'])))
            self.table.setItem(row_idx, 6, QTableWidgetItem("Oui" if product['is_internal_barcode'] else "Non"))

        # Ajouter 10 produits factices si la BD est vide
        if not products:
            print("Base de données vide, ajout de produits factices...")
            dummy_products_data = [
                ("LIVRE001", "Le Seigneur des Anneaux", "Livres", 25.50, 10, False),
                ("LIVRE002", "Orgueil et Préjugés", "Livres", 15.00, 20, False),
                ("LIB0001", "Cahier A4 100 pages", "Papeterie", 3.00, 150, True),
                ("LIB0002", "Stylo Bic Bleu", "Fournitures", 1.20, 300, True),
                ("PCBL0003", "Règle 30cm", "Fournitures", 0.75, 200, False),
                ("LIB0004", "Trousse Scolaire Rouge", "Fournitures", 8.50, 50, True),
                ("LIVRE003", "1984 par George Orwell", "Livres", 12.75, 40, False),
                ("LIB0005", "Marqueur Noir Permanent", "Papeterie", 2.10, 80, True),
                ("LIB0006", "Carnet de Notes A5", "Papeterie", 5.20, 120, True),
                ("LIB0007", "Écharpe en Laine", "Vêtements", 18.00, 25, True),
            ]
            for barcode, name, category, price, stock, is_internal in dummy_products_data:
                if not self.db.get_product(barcode):
                    self.db.add_product(barcode, name, category, price, stock, is_internal)
            self.load_products()
            print("Produits factices ajoutés et tableau rechargé.")

        print("Produits chargés dans le tableau d'audit.")

    def edit_selected_product(self):
        """Ouvre une boîte de dialogue pour éditer le produit sélectionné."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à éditer.")
            return

        row = selected_rows[0].row()
        product_id = int(self.table.item(row, 0).text())

        product_data = self.db.get_product_by_id(product_id)
        if not product_data:
            QMessageBox.critical(self, "Erreur", "Produit introuvable en base de données.")
            return

        dialog = ProductEditDialog(product_data, self)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            if self.db.update_product_details(
                    product_id,
                    updated_data['name'],
                    updated_data['category'],
                    updated_data['price'],
                    updated_data['stock']
            ):
                QMessageBox.information(self, "Succès", "Produit mis à jour.")
                self.load_products()
            else:
                QMessageBox.warning(self, "Échec", "Erreur lors de la mise à jour du produit.")

    def delete_selected_product(self):
        """Supprime le produit sélectionné."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner un produit à supprimer.")
            return

        row = selected_rows[0].row()
        product_id = int(self.table.item(row, 0).text())
        product_name = self.table.item(row, 2).text()

        reply = QMessageBox.question(
            self, "Confirmer Suppression",
            f"Voulez-vous vraiment supprimer le produit '{product_name}' (ID: {product_id})?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self, "Succès", "Produit supprimé.")
                self.load_products()
            else:
                QMessageBox.warning(self, "Échec", "Erreur lors de la suppression du produit.")


class ProductEditDialog(QDialog):
    """Dialogue pour éditer les détails d'un produit."""

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Éditer Produit: {product_data['name']}")
        self.setMinimumWidth(400)

        self.product_data = product_data

        layout = QFormLayout(self)

        self.name_input = QLineEdit(product_data['name'])
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"])
        self.category_combo.setCurrentText(product_data['category'] or "Divers")
        self.price_input = QLineEdit(f"{product_data['price']:.2f}")
        self.price_input.setValidator(QDoubleValidator(0, 99999.99, 2))
        self.stock_input = QLineEdit(str(product_data['stock']))
        self.stock_input.setValidator(QIntValidator(0, 999999))

        layout.addRow("Nom:", self.name_input)
        layout.addRow("Catégorie:", self.category_combo)
        layout.addRow("Prix:", self.price_input)
        layout.addRow("Stock:", self.stock_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'price': float(self.price_input.text()),
            'stock': int(self.stock_input.text())
        }


# --- 4. Tab: Caisse ---
class CashierTab(QWidget):
    """Interface de point de vente pour scanner articles et gérer le panier."""

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.cart_items = []
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Section saisie code-barres
        scan_layout = QHBoxLayout()
        barcode_label = QLabel("Code-barres du produit:")
        self.barcode_scan_input = QLineEdit()
        self.barcode_scan_input.setPlaceholderText("Scannez ou saisissez un code-barres...")
        self.barcode_scan_input.returnPressed.connect(self.add_product_to_cart_from_scan)

        scan_layout.addWidget(barcode_label)
        scan_layout.addWidget(self.barcode_scan_input)
        main_layout.addLayout(scan_layout)

        # Tableau du panier
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Article", "Quantité", "Prix Unitaire", "Sous-total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.cart_table)

        # Total et boutons d'action
        bottom_layout = QVBoxLayout()

        self.total_label = QLabel("<b>Total: 0.00 EUR</b>")
        self.total_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        bottom_layout.addWidget(self.total_label)

        btn_layout = QHBoxLayout()
        self.clear_cart_btn = QPushButton("Vider le Panier")
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        self.checkout_btn = QPushButton("Facturer")
        self.checkout_btn.setObjectName("checkoutButton")
        self.checkout_btn.setStyleSheet("background-color: #4CAF50;")
        self.checkout_btn.clicked.connect(self.initiate_checkout)

        btn_layout.addStretch()
        btn_layout.addWidget(self.clear_cart_btn)
        btn_layout.addWidget(self.checkout_btn)
        bottom_layout.addLayout(btn_layout)

        main_layout.addLayout(bottom_layout)

        self.update_cart_display()

    def setup_connections(self):
        pass

    def add_product_to_cart_from_scan(self):
        """Ajoute un produit au panier via scan code-barres."""
        barcode_value = self.barcode_scan_input.text().strip()
        self.barcode_scan_input.clear()

        if not barcode_value:
            return

        product = self.db.get_product(barcode_value)
        if product:
            if product['stock'] > 0:
                found_in_cart = False
                for item in self.cart_items:
                    if item['barcode'] == barcode_value:
                        item['quantity'] += 1
                        found_in_cart = True
                        break

                if not found_in_cart:
                    self.cart_items.append({
                        'id': product['id'],
                        'barcode': product['barcode'],
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': 1
                    })

                QMessageBox.information(self, "Produit Ajouté", f"'{product['name']}' ajouté au panier.")
                self.update_cart_display()
            else:
                QMessageBox.warning(self, "Stock Insuffisant",
                                    f"Le produit '{product['name']}' est en rupture de stock.")
        else:
            QMessageBox.warning(self, "Produit Inconnu", f"Aucun produit trouvé pour le code-barres: {barcode_value}.")

    def update_cart_display(self):
        """Met à jour le tableau du panier et le total."""
        self.cart_table.setRowCount(len(self.cart_items))
        total = 0.0
        for row_idx, item in enumerate(self.cart_items):
            subtotal = item['quantity'] * item['price']
            total += subtotal
            self.cart_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row_idx, 1, QTableWidgetItem(str(item['quantity'])))
            self.cart_table.setItem(row_idx, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.cart_table.setItem(row_idx, 3, QTableWidgetItem(f"{subtotal:.2f}"))

        self.total_label.setText(f"<b>Total: {total:.2f} EUR</b>")

    def clear_cart(self):
        """Vide le panier actuel."""
        if QMessageBox.question(self, "Vider le Panier", "Voulez-vous vraiment vider le panier ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_display()
            QMessageBox.information(self, "Panier Vidé", "Le panier a été vidé.")

    def initiate_checkout(self):
        """Démarre le processus de facturation."""
        if not self.cart_items:
            QMessageBox.warning(self, "Panier Vide", "Le panier est vide. Impossible de facturer.")
            return

        total_amount = sum(item['quantity'] * item['price'] for item in self.cart_items)
        dialog = InvoiceDialog(total_amount, self)
        if dialog.exec() == QDialog.Accepted:
            customer_data = dialog.get_customer_data()
            invoice_number = self.db.add_sale(
                customer_data['name'],
                customer_data['contact'],
                total_amount,
                self.cart_items
            )
            if invoice_number:
                QMessageBox.information(self, "Facture Générée",
                                        f"Vente enregistrée ! Numéro de facture: {invoice_number}")
                self.cart_items = []
                self.update_cart_display()
                if hasattr(self.parent(), 'sales_audit_tab'):
                    self.parent().sales_audit_tab.load_sales()
            else:
                QMessageBox.critical(self, "Erreur de Facturation", "Erreur lors de l'enregistrement de la vente.")


class InvoiceDialog(QDialog):
    """Dialogue pour saisir les informations client lors de la facturation."""

    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Détails de la Facture")
        self.setMinimumWidth(350)

        layout = QFormLayout(self)

        self.total_label = QLabel(f"<b>Montant Total: {total_amount:.2f} EUR</b>")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addRow(self.total_label)

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Nom du client (optionnel)")
        layout.addRow("Nom du client:", self.customer_name_input)

        self.customer_contact_input = QLineEdit()
        self.customer_contact_input.setPlaceholderText("Contact (téléphone, email - optionnel)")
        layout.addRow("Contact:", self.customer_contact_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_customer_data(self):
        return {
            'name': self.customer_name_input.text().strip(),
            'contact': self.customer_contact_input.text().strip()
        }


# --- 5. Tab: Audit des Ventes ---
class SalesAuditTab(QWidget):
    """Interface pour visualiser l'historique des ventes/factures avec filtres."""

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.setup_connections()
        self.load_sales()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Filtres de date et nom client
        filter_group = QGroupBox("Filtrer les ventes")
        filter_layout = QFormLayout(filter_group)

        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Du:"))
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(self.start_date_edit)

        date_filter_layout.addWidget(QLabel("Au:"))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(self.end_date_edit)
        date_filter_layout.addStretch()

        filter_layout.addRow("Période:", date_filter_layout)

        self.customer_name_filter_input = QLineEdit()
        self.customer_name_filter_input.setPlaceholderText("Nom du client")
        self.customer_name_filter_input.returnPressed.connect(self.load_sales)
        filter_layout.addRow("Nom du client:", self.customer_name_filter_input)

        self_refresh_btn = QPushButton("Appliquer les Filtres")
        self_refresh_btn.clicked.connect(self.load_sales)
        filter_layout.addRow(self_refresh_btn)

        main_layout.addWidget(filter_group)

        # Tableau des ventes
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            "Num Facture", "Client", "Contact", "Montant Total", "Date"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.sales_table)

        # Boutons d'action
        bottom_btn_layout = QHBoxLayout()
        self.view_details_btn = QPushButton("Voir Détails Vente")
        self.view_details_btn.clicked.connect(self.view_sale_details)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.view_details_btn)

        main_layout.addLayout(bottom_btn_layout)

    def setup_connections(self):
        pass

    def load_sales(self):
        """Charge les ventes dans le tableau avec filtres."""
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        customer_name_filter = self.customer_name_filter_input.text().strip()

        sales = self.db.get_all_sales(
            start_date=start_date,
            end_date=end_date,
            customer_name_filter=customer_name_filter if customer_name_filter else None
        )

        self.sales_table.setRowCount(len(sales))
        for row_idx, sale in enumerate(sales):
            self.sales_table.setItem(row_idx, 0, QTableWidgetItem(sale['invoice_number']))
            self.sales_table.setItem(row_idx, 1, QTableWidgetItem(sale['customer_name'] or "N/A"))
            self.sales_table.setItem(row_idx, 2, QTableWidgetItem(sale['customer_contact'] or "N/A"))
            self.sales_table.setItem(row_idx, 3, QTableWidgetItem(f"{sale['total_amount']:.2f}"))

            sale_dt = datetime.fromisoformat(sale['sale_date'])
            self.sales_table.setItem(row_idx, 4, QTableWidgetItem(sale_dt.strftime("%d/%m/%Y %H:%M")))

            self.sales_table.item(row_idx, 0).setData(Qt.UserRole, sale['id'])
        print(f"Ventes chargées pour la période: {start_date.toString('dd/MM/yyyy')} - {end_date.toString('dd/MM/yyyy')}")

    def view_sale_details(self):
        """Ouvre une boîte de dialogue pour afficher les détails d'une vente."""
        selected_rows = self.sales_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner une vente pour voir les détails.")
            return

        row = selected_rows[0].row()
        sale_id = self.sales_table.item(row, 0).data(Qt.UserRole)
        invoice_number = self.sales_table.item(row, 0).text()

        sale_items = self.db.get_sale_items(sale_id)
        if sale_items:
            dialog = SaleDetailsDialog(invoice_number, sale_items, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Aucun Détail", "Aucun article trouvé pour cette vente.")


class SaleDetailsDialog(QDialog):
    """Dialogue pour afficher les articles d'une vente spécifique."""

    def __init__(self, invoice_number, items_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Détails de la Facture: {invoice_number}")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Articles pour la facture {invoice_number}:</b>"))

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Article", "Quantité", "Prix Unitaire", "Sous-total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.items_table.setRowCount(len(items_data))
        for row_idx, item in enumerate(items_data):
            self.items_table.setItem(row_idx, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row_idx, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row_idx, 2, QTableWidgetItem(f"{item['price_per_unit']:.2f}"))
            self.items_table.setItem(row_idx, 3, QTableWidgetItem(f"{item['quantity'] * item['price_per_unit']:.2f}"))

        layout.addWidget(self.items_table)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok, self)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


# --- 6. Fenêtre Principale ---
class ModernBarcodeManager(QMainWindow):
    """Fenêtre principale de l'application avec navigation par onglets."""

    def __init__(self):
        super().__init__()
        self.version = "2.0"
        self.db = BarcodeDatabase()
        self.setWindowTitle("Application de Gestion de Librairie")
        self.setMinimumSize(900, 700)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Créer les onglets
        self.product_mgmt_tab = ProductBarcodeManagementTab(self.db)
        self.audit_barcode_tab = AuditBarcodeTab(self.db)
        self.cashier_tab = CashierTab(self.db)
        self.sales_audit_tab = SalesAuditTab(self.db)

        self.tab_widget.addTab(self.product_mgmt_tab, "Ajouter/Gérer Codes-Barres")
        self.tab_widget.addTab(self.audit_barcode_tab, "Audit & Édition Produits")
        self.tab_widget.addTab(self.cashier_tab, "Caisse (Point de Vente)")
        self.tab_widget.addTab(self.sales_audit_tab, "Audit des Ventes")

        # Appliquer les styles
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                margin-top: 20px;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-top: 1px solid #ccc;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 1 #FAFAFA);
                border: 1px solid #C4C4C3;
                border-bottom-color: #C2C2C2;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                padding: 8px 15px;
                color: #333;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #e0d0c0, stop: 1 #c0a080);
                border-color: #9B9B9B;
                border-bottom-color: #e0d0c0;
                color: #000;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #F0F0F0;
            }
        """)

    def closeEvent(self, event):
        """Surcharge de la fermeture pour fermer la connexion BD."""
        print("Fermeture de l'application...")
        self.db.close()
        event.accept()

    def get_ui(self):
        return self

    def refresh(self):
        pass