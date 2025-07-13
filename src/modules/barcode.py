import sys
import os
import sqlite3
import random
from datetime import datetime, timedelta  # Add timedelta

import barcode
# Import PySide6 modules
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QGroupBox, QScrollArea,
    QSizePolicy, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QSize, QDate
from PySide6.QtGui import QPixmap, QIcon, QFont, QDoubleValidator, QIntValidator
from barcode.writer import ImageWriter


# --- 1. Database Refactoring (BarcodeDatabase) ---
class BarcodeDatabase:
    """
    Simplified SQLite database management for barcodes
    Problem solved: Centralization and persistence of all operational data.
    """

    def __init__(self, db_name="librairie_gestion.sqlite"):
        self.db_name = db_name
        self.conn = None
        self._connect()
        self._init_db()

    def _connect(self):
        """Establishes connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # To access columns by name
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Unable to connect to database: {e}")
            sys.exit(1)  # Exit application if connection fails

    def _init_db(self):
        """Creates tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                price REAL DEFAULT 0.0,
                stock INTEGER DEFAULT 0,
                is_internal_barcode BOOLEAN DEFAULT 0, -- 1 if generated, 0 if external
                created_at TEXT
            )
        """)
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
        print("Database tables checked/created.")

    def add_product(self, barcode, name, category="", price=0.0, stock=0, is_internal_barcode=False):
        """Adds a new product to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO products (barcode, name, category, price, stock, is_internal_barcode, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (barcode, name, category, price, stock, 1 if is_internal_barcode else 0, datetime.now().isoformat())
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", f"Barcode '{barcode}' already exists for another product.")
            return False
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Error adding product: {e}")
            return False

    def get_product(self, barcode):
        """Retrieves a product by its barcode."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
        return cursor.fetchone()  # Returns a Row object

    def get_product_by_id(self, product_id):
        """Retrieves a product by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        return cursor.fetchone()  # Returns a Row object

    def update_stock(self, barcode, quantity_change):
        """Updates the stock of a product. quantity_change can be positive or negative."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE products SET stock = stock + ? WHERE barcode=?",
                (quantity_change, barcode)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Error updating stock: {e}")
            return False

    def update_product_details(self, product_id, name, category, price, stock):
        """Updates product details by its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE products SET name=?, category=?, price=?, stock=? WHERE id=?",
                (name, category, price, stock, product_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Error updating product: {e}")
            return False

    def delete_product(self, product_id):
        """Deletes a product by its ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Error deleting product: {e}")
            return False

    def get_all_products(self):
        """Retrieves all products."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY name ASC")
        return cursor.fetchall()

    def add_sale(self, customer_name, customer_contact, total_amount, cart_items):
        """Adds a new sale and its associated items."""
        try:
            cursor = self.conn.cursor()
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            sale_date = datetime.now().isoformat()

            cursor.execute(
                "INSERT INTO sales (invoice_number, customer_name, customer_contact, total_amount, sale_date) "
                "VALUES (?, ?, ?, ?, ?)",
                (invoice_number, customer_name, customer_contact, total_amount, sale_date)
            )
            sale_id = cursor.lastrowid

            for item in cart_items:
                cursor.execute(
                    "INSERT INTO sale_items (sale_id, product_id, barcode, product_name, quantity, price_per_unit) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (sale_id, item['id'], item['barcode'], item['name'], item['quantity'], item['price'])
                )
                # Decrement stock after sale
                self.update_stock(item['barcode'], -item['quantity'])

            self.conn.commit()
            return invoice_number
        except sqlite3.Error as e:
            QMessageBox.critical(None, "DB Error", f"Error recording sale: {e}")
            self.conn.rollback()
            return None

    def get_all_sales(self, start_date=None, end_date=None, customer_name_filter=None):  # Added customer_name_filter
        """Retrieves all sales, with optional date and customer name filters."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM sales"
        params = []
        conditions = []

        if start_date:
            conditions.append("sale_date >= ?")
            # Convert QDate to Python date object then to ISO format
            params.append(start_date.toPython().isoformat())
        if end_date:
            conditions.append("sale_date < ?")  # Use < for exclusive end date (next day's start)
            # Add one day to the end date to include all sales on the selected day
            # Convert QDate to Python date object, add timedelta, then to ISO format
            params.append((end_date.toPython() + timedelta(days=1)).isoformat())

        if customer_name_filter:  # Added customer name filter
            conditions.append("customer_name LIKE ?")
            params.append(f"%{customer_name_filter}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY sale_date DESC"

        cursor.execute(query, params)
        return cursor.fetchall()

    def get_sale_items(self, sale_id):
        """Retrieves items for a specific sale."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sale_items WHERE sale_id=?", (sale_id,))
        return cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")


# --- 2. Tab: Barcode and Product Management (ProductBarcodeManagementTab) ---
class ProductBarcodeManagementTab(QWidget):
    """
    Interface for adding new products (with external or internally generated barcodes)
    and updating existing products via scan.
    Problem solved: Unified management of new product integration and initial updates.
    """

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_barcode_for_print = None  # Stores the last generated code for printing
        self.current_product_name_for_print = None

        self.setup_ui()
        self.setup_connections()
        self._create_barcodes_directory()

    def _create_barcodes_directory(self):
        """Creates the directory for barcode images if necessary."""
        os.makedirs("barcodes", exist_ok=True)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Section for scanning an external barcode and associating/updating it
        scan_group = QGroupBox("Rechercher ou Ajouter un Produit par Code-Barres")
        scan_layout = QVBoxLayout(scan_group)

        # Layout for input field and buttons
        scan_input_buttons_layout = QHBoxLayout()
        self.external_barcode_input = QLineEdit()
        self.external_barcode_input.setPlaceholderText("Scan ou saisie d'un code-barres existant...")
        self.external_barcode_input.returnPressed.connect(self._handle_external_barcode_input)

        # "Rechercher" button
        self.search_btn = QPushButton("Rechercher")
        self.search_btn.setIcon(QIcon.fromTheme("system-search"))  # Search icon
        self.search_btn.clicked.connect(self._handle_external_barcode_input)  # Connect to click

        # New "Scanner" button
        self.scan_btn = QPushButton("Scanner")
        self.scan_btn.setIcon(QIcon.fromTheme("camera-web"))  # Scan icon
        self.scan_btn.setStyleSheet("background-color: #2196F3;")  # Soft blue color
        self.scan_btn.clicked.connect(self._simulate_scan_and_handle)  # New method to simulate scan

        scan_input_buttons_layout.addWidget(self.external_barcode_input)
        scan_input_buttons_layout.addWidget(self.search_btn)
        scan_input_buttons_layout.addWidget(self.scan_btn)  # Add the new "Scanner" button

        self.scan_product_status = QLabel(
            "Utilisez le champ ci-dessus pour saisir un code-barres et rechercher, ou cliquez sur 'Scanner' pour simuler un scan.")
        self.scan_product_status.setWordWrap(True)

        scan_layout.addLayout(scan_input_buttons_layout)  # Add the layout with both buttons
        scan_layout.addWidget(self.scan_product_status)

        # Form for product details (used by both sections)
        self.product_form_layout = QFormLayout()

        self.product_id_hidden = QLabel("")  # To store the product ID if it exists (invisible)
        self.product_id_hidden.setVisible(False)

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Nom complet du produit")

        self.product_category_combo = QComboBox()
        self.product_category_combo.addItems(["Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"])

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

        # Internal Barcode Generation Section
        gen_group = QGroupBox("Générer un Code-Barre Interne (pour les nouveaux produits sans code)")
        gen_layout = QVBoxLayout(gen_group)

        self.generate_internal_btn = QPushButton("Générer & Enregistrer Code Interne")
        self.generate_internal_btn.setIcon(QIcon.fromTheme("document-new"))
        self.generate_internal_btn.clicked.connect(self._generate_internal_barcode)

        # Generated barcode display
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
        gen_layout.addSpacing(15)  # Ajout d'espace vertical
        gen_layout.addWidget(self.barcode_preview)
        gen_layout.addWidget(self.barcode_value_display)
        gen_layout.addSpacing(15)  # Ajout d'espace vertical
        gen_layout.addWidget(self.print_internal_btn)

        main_layout.addWidget(scan_group)
        main_layout.addWidget(gen_group)
        main_layout.addStretch()

        self._clear_product_form()  # Initialize empty fields

    def setup_connections(self):
        # Connections are made directly in setup_ui for buttons
        pass

    def _simulate_scan_and_handle(self):
        """
        Simulates a barcode scan (generates a random code)
        and calls the handling method to process it.
        """
        # Generate a random "external" barcode for simulation
        simulated_barcode = f"{random.randint(1000000000000, 9999999999999)}"
        self.external_barcode_input.setText(simulated_barcode)
        self._handle_external_barcode_input()  # Process the simulated code

    def _handle_external_barcode_input(self):
        """Processes the entered or scanned external barcode."""
        barcode_value = self.external_barcode_input.text().strip()
        if not barcode_value:
            self.scan_product_status.setText(
                "<span style='color: red;'>Veuillez entrer un code-barres pour rechercher.</span>")
            self._clear_product_form(clear_input_field=False)  # Do not clear input here
            return

        product = self.db.get_product(barcode_value)
        if product:
            self.product_id_hidden.setText(str(product['id']))  # Store product ID
            self.product_name_input.setText(product['name'])
            self.product_category_combo.setCurrentText(product['category'] or "Divers")
            self.product_price_input.setText(str(product['price']))
            self.product_stock_input.setText(str(product['stock']))
            self.scan_product_status.setText(
                f"Produit trouvé: <b>{product['name']}</b>. Modifiez les détails si nécessaire ou cliquez sur 'Mettre à jour Produit'.")
            self.save_product_btn.setText("Mettre à jour Produit")  # Update button text
        else:
            self.product_id_hidden.setText("")  # No ID for a new product
            # Keep the scanned barcode in the input for a new addition
            self.scan_product_status.setText(
                f"Code-barres <b>{barcode_value}</b> non trouvé. Remplissez les détails pour ajouter ce nouveau produit avec ce code.")
            self.save_product_btn.setText("Ajouter Nouveau Produit")  # Update button text

        # Here, external_barcode_input is not cleared, as the user might want to
        # add a new product with this code or modify it.

    def _save_scanned_or_new_product(self):
        """Saves product details with the scanned/entered barcode."""
        # For adding or updating, the barcode must be in the input
        barcode_value_to_save = self.external_barcode_input.text().strip()
        if not barcode_value_to_save:
            QMessageBox.warning(self, "Erreur",
                                "Le code-barres est manquant. Veuillez scanner/saisir un code-barres avant d'ajouter ou de mettre à jour.")
            return

        name = self.product_name_input.text().strip()
        category = self.product_category_combo.currentText()

        try:
            price = float(self.product_price_input.text().strip() or "0")
            stock = int(self.product_stock_input.text().strip() or "0")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le prix et le stock doivent être des nombres valides.")
            return

        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du produit est obligatoire.")
            return

        product_id = self.product_id_hidden.text()
        if product_id:  # Existing product, update
            if self.db.update_product_details(int(product_id), name, category, price, stock):
                QMessageBox.information(self, "Succès", f"Produit '{name}' mis à jour avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", f"Échec de la mise à jour du produit '{name}'.")
        else:  # New product
            # Use the barcode directly from the input for the new addition
            if self.db.add_product(barcode_value_to_save, name, category, price, stock, is_internal_barcode=False):
                QMessageBox.information(self, "Succès",
                                        f"Produit '{name}' ajouté avec le code-barres: {barcode_value_to_save}.")
            else:
                QMessageBox.warning(self, "Erreur",
                                    f"Impossible d'ajouter le produit '{name}' (le code-barres existe peut-être déjà).")

        self._clear_product_form(clear_input_field=True)  # Reset form completely after saving
        self.scan_product_status.setText("Prêt pour un nouveau scan ou ajout.")
        self.save_product_btn.setText("Ajouter Produit (avec code scanné/saisi)")  # Default button text

    def _generate_internal_barcode(self):
        """Generates an internal barcode for a new product."""
        name = self.product_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom de produit pour générer un code interne.")
            return

        try:
            price = float(self.product_price_input.text().strip() or "0")
            stock = int(self.product_stock_input.text().strip() or "0")
        except ValueError:
            QMessageBox.warning(self, "Erreur",
                                "Veuillez entrer des valeurs numériques valides pour le prix et le stock.")
            return

        category = self.product_category_combo.currentText()

        # Generate a unique code (LIB prefix for "Librairie")
        new_barcode = f"LIB{random.randint(100000, 999999)}"
        while self.db.get_product(new_barcode):  # Ensure uniqueness
            new_barcode = f"LIB{random.randint(100000, 999999)}"

        # Save the product with the generated internal code
        if self.db.add_product(new_barcode, name, category, price, stock, is_internal_barcode=True):
            try:
                # Generate Code128 barcode image
                ean = barcode.get('code128', new_barcode, writer=ImageWriter())
                filename = os.path.join("barcodes", new_barcode)
                ean.save(filename)

                # Display the barcode in the interface
                pixmap = QPixmap(f"{filename}.png")
                self.barcode_preview.setPixmap(pixmap.scaledToWidth(300, Qt.SmoothTransformation))
                self.barcode_value_display.setText(new_barcode)
                self.current_barcode_for_print = new_barcode
                self.current_product_name_for_print = name
                self.print_internal_btn.setEnabled(True)

                QMessageBox.information(
                    self, "Succès",
                    f"Produit '{name}' enregistré avec code interne:\n{new_barcode}"
                )
                self._clear_product_form(clear_input_field=True)  # Reset form after generation
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Génération",
                                     f"Erreur lors de la génération de l'image ou de l'enregistrement: {str(e)}")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible d'enregistrer ce produit avec le code interne généré.")

    def _print_generated_barcode(self):
        """Simulates printing the generated internal barcode."""
        if self.current_barcode_for_print and self.current_product_name_for_print:
            QMessageBox.information(
                self, "Impression d'Étiquette",
                f"Simulation d'impression pour:\n"
                f"Nom: {self.current_product_name_for_print}\n"
                f"Code: {self.current_barcode_for_print}\n"
                f"Vérifiez le dossier 'barcodes' pour l'image générée."
            )
        else:
            QMessageBox.warning(self, "Rien à Imprimer", "Aucun code-barres interne généré récemment.")

    def _clear_product_form(self, clear_input_field=True):
        """
        Resets product add/edit form fields.
        `clear_input_field`: If True, also clears the external barcode input field.
        """
        if clear_input_field:
            self.external_barcode_input.clear()
            self.scan_product_status.setText(
                "Utilisez le champ ci-dessus pour scanner ou saisir un code-barres et rechercher un produit.")
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


# --- 3. Tab: Barcode Audit and Management (AuditBarcodeTab) ---
class AuditBarcodeTab(QWidget):
    """
    Interface for listing, viewing, and editing product details.
    Problem solved: Global visibility of stock and product information, easy editing.
    """

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.setup_connections()
        self.load_products()  # Load products on startup

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(7)  # ID, Barcode, Name, Category, Price, Stock, Internal
        self.table.setHorizontalHeaderLabels([
            "ID", "Code-Barres", "Nom", "Catégorie", "Prix", "Stock", "Interne"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire row
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # Only one row at a time

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
        """Loads all products into the table."""
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

        # Add 10 dummy products if the database is empty
        if not products:
            print("Database is empty, adding initial dummy products...")
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
                # Check if barcode already exists before adding to avoid IntegrityError
                if not self.db.get_product(barcode):
                    self.db.add_product(barcode, name, category, price, stock, is_internal)
            # Reload products after adding dummies
            self.load_products()
            print("Dummy products added and table reloaded.")

        print("Products loaded in audit table.")

    def edit_selected_product(self):
        """Opens a dialog to edit the selected product."""
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
                self.load_products()  # Reload list
            else:
                QMessageBox.warning(self, "Échec", "Erreur lors de la mise à jour du produit.")

    def delete_selected_product(self):
        """Deletes the selected product."""
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
                self.load_products()  # Reload list
            else:
                QMessageBox.warning(self, "Échec", "Erreur lors de la suppression du produit.")


class ProductEditDialog(QDialog):
    """Dialog for editing product details."""

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


# --- 4. Tab: Cashier (CashierTab) ---
class CashierTab(QWidget):
    """
    Point of Sale interface for scanning items, managing the cart
    and finalizing sales.
    Problem solved: Automation of sales process, fast calculation and invoice generation.
    """

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.cart_items = []  # List of dictionaries {product_id, barcode, name, price, quantity}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Barcode input section
        scan_layout = QHBoxLayout()
        barcode_label = QLabel("Code-barres du produit:")
        self.barcode_scan_input = QLineEdit()
        self.barcode_scan_input.setPlaceholderText("Scannez ou saisissez un code-barres...")
        self.barcode_scan_input.returnPressed.connect(self.add_product_to_cart_from_scan)

        scan_layout.addWidget(barcode_label)
        scan_layout.addWidget(self.barcode_scan_input)
        main_layout.addLayout(scan_layout)

        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)  # Item, Qty, Unit Price, Subtotal
        self.cart_table.setHorizontalHeaderLabels(["Article", "Quantité", "Prix Unitaire", "Sous-total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Prevent direct editing
        main_layout.addWidget(self.cart_table)

        # Total and action buttons
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

        self.update_cart_display()  # Initialize display

    def setup_connections(self):
        pass  # Connections are made directly in setup_ui

    def add_product_to_cart_from_scan(self):
        """Adds a product to the cart via barcode scan."""
        barcode_value = self.barcode_scan_input.text().strip()
        self.barcode_scan_input.clear()  # Clear input after reading

        if not barcode_value:
            return

        product = self.db.get_product(barcode_value)
        if product:
            if product['stock'] > 0:
                # Check if item is already in cart
                found_in_cart = False
                for item in self.cart_items:
                    if item['barcode'] == barcode_value:
                        item['quantity'] += 1
                        found_in_cart = True
                        break

                if not found_in_cart:
                    # Add new item to cart
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
        """Updates the cart table and total."""
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
        """Clears the current cart."""
        if QMessageBox.question(self, "Vider le Panier", "Voulez-vous vraiment vider le panier ?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_display()
            QMessageBox.information(self, "Panier Vider", "Le panier a été vidé.")

    def initiate_checkout(self):
        """Starts the invoicing process."""
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
                self.cart_items = []  # Clear cart after sale
                self.update_cart_display()  # Update display
                # Emit a signal to refresh Sales Audit tab
                if hasattr(self.parent(), 'sales_audit_tab') and isinstance(self.parent().sales_audit_tab,
                                                                            SalesAuditTab):
                    self.parent().sales_audit_tab.load_sales()
            else:
                QMessageBox.critical(self, "Erreur de Facturation", "Erreur lors de l'enregistrement de la vente.")


class InvoiceDialog(QDialog):
    """Dialog for entering customer information during invoicing."""

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


# --- 5. Tab: Sales Audit (SalesAuditTab) ---
class SalesAuditTab(QWidget):
    """
    Interface for viewing sales/invoice history with filters.
    Problem solved: Overview of past transactions for analysis and audit.
    """

    def __init__(self, db: BarcodeDatabase, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        self.setup_connections()
        self.load_sales()  # Load sales on startup

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Date and customer name filters
        filter_group = QGroupBox("Filtrer les ventes")
        filter_layout = QFormLayout(filter_group)  # Use QFormLayout for better layout

        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Du:"))
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))  # Default: last month
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(self.start_date_edit)

        date_filter_layout.addWidget(QLabel("Au:"))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(self.end_date_edit)
        date_filter_layout.addStretch()

        filter_layout.addRow("Période:", date_filter_layout)  # Add date layout to form

        self.customer_name_filter_input = QLineEdit()
        self.customer_name_filter_input.setPlaceholderText("Nom du client")
        self.customer_name_filter_input.returnPressed.connect(self.load_sales)  # Apply filter on Enter
        filter_layout.addRow("Nom du client:", self.customer_name_filter_input)

        self_refresh_btn = QPushButton("Appliquer les Filtres")
        self_refresh_btn.clicked.connect(self.load_sales)
        filter_layout.addRow(self_refresh_btn)  # Add button to form

        main_layout.addWidget(filter_group)

        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)  # Invoice Number, Client, Contact, Total Amount, Date
        self.sales_table.setHorizontalHeaderLabels([
            "Num Facture", "Client", "Contact", "Montant Total", "Date"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setSelectionMode(QTableWidget.SingleSelection)
        main_layout.addWidget(self.sales_table)

        # Action buttons for sales
        bottom_btn_layout = QHBoxLayout()
        self.view_details_btn = QPushButton("Voir Détails Vente")
        self.view_details_btn.clicked.connect(self.view_sale_details)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.view_details_btn)

        main_layout.addLayout(bottom_btn_layout)

    def setup_connections(self):
        # Connection made in setup_ui
        pass

    def load_sales(self):
        """Loads sales into the table with date and customer name filters."""
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

            # Format date for better display
            sale_dt = datetime.fromisoformat(sale['sale_date'])
            self.sales_table.setItem(row_idx, 4, QTableWidgetItem(sale_dt.strftime("%d/%m/%Y %H:%M")))

            # Store sale ID in the item for easy access later
            self.sales_table.item(row_idx, 0).setData(Qt.UserRole, sale['id'])
        print(
            f"Ventes chargées pour la période: {start_date.toString('dd/MM/yyyy')} - {end_date.toString('dd/MM/yyyy')}")

    def view_sale_details(self):
        """Opens a dialog to display details of a selected sale."""
        selected_rows = self.sales_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Sélection Requise", "Veuillez sélectionner une vente pour voir les détails.")
            return

        row = selected_rows[0].row()
        sale_id = self.sales_table.item(row, 0).data(Qt.UserRole)  # Retrieve stored ID
        invoice_number = self.sales_table.item(row, 0).text()

        sale_items = self.db.get_sale_items(sale_id)
        if sale_items:
            dialog = SaleDetailsDialog(invoice_number, sale_items, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Aucun Détail", "Aucun article trouvé pour cette vente.")


class SaleDetailsDialog(QDialog):
    """Dialog for displaying items of a specific sale."""

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


# --- 6. Main Window (MainWindow) ---
class ModernBarcodeManager(QMainWindow):
    """
    Main application window with tabbed navigation.
    Problem solved: Organization of different functionalities in a coherent interface.
    """

    def __init__(self):
        super().__init__()
        self.version = "1.0"
        self.db = BarcodeDatabase()  # Initialize database once
        self.setWindowTitle("Application de Gestion de Librairie")
        self.setMinimumSize(900, 700)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create tabs
        self.product_mgmt_tab = ProductBarcodeManagementTab(self.db)
        self.audit_barcode_tab = AuditBarcodeTab(self.db)
        self.cashier_tab = CashierTab(self.db)
        self.sales_audit_tab = SalesAuditTab(self.db)  # Keep a reference for refresh

        self.tab_widget.addTab(self.product_mgmt_tab, "Ajouter/Gérer Codes-Barres")
        self.tab_widget.addTab(self.audit_barcode_tab, "Audit & Édition Produits")
        self.tab_widget.addTab(self.cashier_tab, "Caisse (Point de Vente)")
        self.tab_widget.addTab(self.sales_audit_tab, "Audit des Ventes")

        # Apply styles
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                margin-top: 20px; /* Espace vertical pour séparer du menu principal */
            }
            QTabWidget::pane { /* The tab widget frame */
                border: 1px solid #ccc;
                border-top: 1px solid #ccc;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QTabWidget::tab-bar {
                left: 5px; /* move to the right by 5px */
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 1 #FAFAFA);
                border: 1px solid #C4C4C3;
                border-bottom-color: #C2C2C2; /* same as pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 120px;
                padding: 8px 15px;
                color: #333; /* Rendre le texte des onglets visible */
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #e0d0c0, stop: 1 #c0a080); /* Teinte marron douce */
                border-color: #9B9B9B;
                border-bottom-color: #e0d0c0; /* make the selected tab look like it's connected to the pane */
                color: #000; /* Texte noir pour l'onglet actif */
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #F0F0F0;
            }
        """)

    def closeEvent(self, event):
        """Overrides application close to close DB connection."""
        print("Closing application...")
        self.db.close()
        event.accept()


    def get_ui(self):
        return self

    def refresh(self):
        pass






# # --- Application Entry Point ---
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # Create barcode folder if it doesn't exist
#     os.makedirs("barcodes", exist_ok=True)
#
#     main_win = MainWindow()
#     main_win.show()
#
#     sys.exit(app.exec())






