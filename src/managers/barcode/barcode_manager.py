"""
Manager des codes-barres - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
Architecture MVC pure.
"""

import random
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
from PySide6.QtGui import QDoubleValidator, QIntValidator

import barcode
from barcode.writer import ImageWriter

# ✅ UTILISER VOTRE DatabaseManager
from src.database.manager import DatabaseManager
from src.utils.config import get_config


class BarcodeManager(QObject):
    """
    Manager des codes-barres - Logique métier pure.
    Sépare complètement la logique de la présentation.
    """
    
    version = "2.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.db = DatabaseManager()  # ✅ Votre DatabaseManager
        
        # Configuration
        config = get_config()
        self.barcodes_dir = config.base_dir / "barcodes"
        self.barcodes_dir.mkdir(exist_ok=True)
        
        # État
        self.current_barcode_for_print = None
        self.current_product_name_for_print = None
        
        # Créer table products si nécessaire (adaptation à votre structure)
        self._init_barcode_tables()
        
        print(f"[BarcodeManager v{self.version}] Initialisé")
    
    def _init_barcode_tables(self):
        """Ajoute les colonnes nécessaires pour les codes-barres si elles n'existent pas."""
        try:
            cursor = self.db.db.get_cursor()
            
            # Vérifier si la colonne 'barcode' existe dans products
            cursor.execute("PRAGMA table_info(products)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'barcode' not in columns:
                # Ajouter la colonne barcode
                cursor.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
                print("✅ Colonne 'barcode' ajoutée à la table products")
            
            if 'is_internal_barcode' not in columns:
                # Ajouter la colonne is_internal_barcode
                cursor.execute("ALTER TABLE products ADD COLUMN is_internal_barcode INTEGER DEFAULT 0")
                print("✅ Colonne 'is_internal_barcode' ajoutée à la table products")
            
            self.db.db.commit()
            
        except Exception as e:
            print(f"⚠️ Erreur init tables barcode: {e}")
    
    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            from src.ui.views.barcode_view import BarcodeView
            
            self.view = BarcodeView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[BarcodeManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.load_products()
        print("[BarcodeManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_barcode_requested.connect(self.on_search_barcode)
        self.view.scan_barcode_requested.connect(self.on_scan_barcode)
        self.view.save_product_requested.connect(self.on_save_product)
        self.view.generate_internal_barcode_requested.connect(self.on_generate_internal_barcode)
        self.view.print_barcode_requested.connect(self.on_print_barcode)
        self.view.refresh_products_requested.connect(self.load_products)
        self.view.edit_product_requested.connect(self.on_edit_product)
        self.view.delete_product_requested.connect(self.on_delete_product)
        
        print("[BarcodeManager] Signaux connectés")
    
    # ========== SLOTS - GESTION DES PRODUITS ==========
    
    @Slot(str)
    def on_search_barcode(self, barcode_text: str):
        """Recherche un produit par code-barres."""
        if not barcode_text:
            self.view.set_status_message("Veuillez entrer un code-barres.", is_error=True)
            return
        
        # Rechercher le produit via barcode
        product = self.get_product_by_barcode(barcode_text)
        
        if product:
            # Produit trouvé
            product_data = {
                'id': product['id'],
                'barcode': barcode_text,
                'name': product['name'],
                'category': product.get('category', 'Divers'),
                'price': product['price'],
                'stock': product['stock_quantity']
            }
            self.view.update_product_form(product_data)
        else:
            # Produit non trouvé
            product_data = {
                'id': '',
                'barcode': barcode_text,
                'name': '',
                'category': 'Divers',
                'price': '0',
                'stock': '0'
            }
            self.view.update_product_form(product_data)
        
        print(f"[BarcodeManager] Recherche: {barcode_text} - {'Trouvé' if product else 'Non trouvé'}")
    
    @Slot()
    def on_scan_barcode(self):
        """Simule un scan de code-barres."""
        simulated_barcode = f"{random.randint(1000000000000, 9999999999999)}"
        self.on_search_barcode(simulated_barcode)
        print(f"[BarcodeManager] Scan simulé: {simulated_barcode}")
    
    @Slot(dict)
    def on_save_product(self, data: dict):
        """Sauvegarde ou met à jour un produit."""
        barcode = data.get('barcode', '').strip()
        name = data.get('name', '').strip()
        category = data.get('category', 'Divers')
        
        if not barcode:
            QMessageBox.warning(self.view, "Erreur", "Le code-barres est obligatoire.")
            return
        
        if not name:
            QMessageBox.warning(self.view, "Erreur", "Le nom du produit est obligatoire.")
            return
        
        try:
            price = float(data.get('price', '0') or '0')
            stock = int(data.get('stock', '0') or '0')
        except ValueError:
            QMessageBox.warning(self.view, "Erreur", "Prix et stock doivent être des nombres valides.")
            return
        
        product_id = data.get('id', '').strip()
        
        if product_id:
            # Mise à jour
            if self.update_product_with_barcode(int(product_id), name, category, price, stock, barcode):
                QMessageBox.information(self.view, "Succès", f"Produit '{name}' mis à jour.")
                self.view.clear_product_form()
                self.load_products()
            else:
                QMessageBox.warning(self.view, "Erreur", "Échec de la mise à jour.")
        else:
            # Ajout
            if self.add_product_with_barcode(barcode, name, category, price, stock, False):
                QMessageBox.information(self.view, "Succès", f"Produit '{name}' ajouté.")
                self.view.clear_product_form()
                self.load_products()
            else:
                QMessageBox.warning(self.view, "Erreur", "Échec de l'ajout.")
        
        print(f"[BarcodeManager] Produit sauvegardé: {name}")
    
    @Slot(dict)
    def on_generate_internal_barcode(self, data: dict):
        """Génère un code-barres interne."""
        name = data.get('name', '').strip()
        
        if not name:
            QMessageBox.warning(self.view, "Erreur", "Veuillez entrer un nom de produit.")
            return
        
        try:
            price = float(data.get('price', '0') or '0')
            stock = int(data.get('stock', '0') or '0')
        except ValueError:
            QMessageBox.warning(self.view, "Erreur", "Prix et stock invalides.")
            return
        
        category = data.get('category', 'Divers')
        
        # Générer code unique
        new_barcode = f"LIB{random.randint(100000, 999999)}"
        while self.get_product_by_barcode(new_barcode):
            new_barcode = f"LIB{random.randint(100000, 999999)}"
        
        # Enregistrer le produit
        if self.add_product_with_barcode(new_barcode, name, category, price, stock, True):
            try:
                # Générer l'image
                ean = barcode.get('code128', new_barcode, writer=ImageWriter())
                filename = self.barcodes_dir / new_barcode
                ean.save(str(filename))
                
                # Mettre à jour l'aperçu
                image_path = str(filename) + ".png"
                self.view.update_barcode_preview(new_barcode, image_path)
                
                self.current_barcode_for_print = new_barcode
                self.current_product_name_for_print = name
                
                QMessageBox.information(self.view, "Succès", f"Code interne généré:\n{new_barcode}")
                self.view.clear_product_form()
                self.load_products()
                
                print(f"[BarcodeManager] Code généré: {new_barcode}")
                
            except Exception as e:
                QMessageBox.critical(self.view, "Erreur", f"Erreur génération: {str(e)}")
        else:
            QMessageBox.warning(self.view, "Erreur", "Impossible d'enregistrer.")
    
    @Slot()
    def on_print_barcode(self):
        """Simule l'impression."""
        if self.current_barcode_for_print and self.current_product_name_for_print:
            QMessageBox.information(
                self.view,
                "Impression",
                f"Nom: {self.current_product_name_for_print}\n"
                f"Code: {self.current_barcode_for_print}\n"
                f"Vérifiez le dossier 'barcodes'"
            )
        else:
            QMessageBox.warning(self.view, "Erreur", "Aucun code-barres à imprimer.")
    
    @Slot(int)
    def on_edit_product(self, product_id: int):
        """Édite un produit."""
        product = self.db.get_product_by_id(product_id)
        
        if not product:
            QMessageBox.critical(self.view, "Erreur", "Produit introuvable.")
            return
        
        dialog = ProductEditDialog(product, self.view)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_data()
            cursor = self.db.db.get_cursor()
            cursor.execute(
                """UPDATE products 
                   SET name=?, category=?, price=?, stock_quantity=?, updated_at=CURRENT_TIMESTAMP 
                   WHERE id=?""",
                (updated_data['name'], updated_data['category'], 
                 updated_data['price'], updated_data['stock'], product_id)
            )
            self.db.db.commit()
            QMessageBox.information(self.view, "Succès", "Produit mis à jour.")
            self.load_products()
    
    @Slot(int)
    def on_delete_product(self, product_id: int):
        """Supprime un produit."""
        product = self.db.get_product_by_id(product_id)
        
        if not product:
            QMessageBox.critical(self.view, "Erreur", "Produit introuvable.")
            return
        
        reply = QMessageBox.question(
            self.view,
            "Confirmation",
            f"Supprimer '{product['name']}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_product(product_id):
                QMessageBox.information(self.view, "Succès", "Produit supprimé.")
                self.load_products()
    
    # ========== MÉTHODES UTILITAIRES ==========
    
    def get_product_by_barcode(self, barcode_text: str):
        """Récupère un produit par son code-barres."""
        try:
            cursor = self.db.db.get_cursor()
            cursor.execute("SELECT * FROM products WHERE barcode=?", (barcode_text,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"Erreur recherche barcode: {e}")
            return None
    
    def add_product_with_barcode(self, barcode, name, category, price, stock, is_internal):
        """Ajoute un produit avec code-barres."""
        try:
            cursor = self.db.db.get_cursor()
            cursor.execute(
                """INSERT INTO products 
                   (barcode, name, category, price, stock_quantity, is_internal_barcode) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (barcode, name, category, price, stock, 1 if is_internal else 0)
            )
            self.db.db.commit()
            return True
        except Exception as e:
            print(f"Erreur ajout produit: {e}")
            return False
    
    def update_product_with_barcode(self, product_id, name, category, price, stock, barcode):
        """Met à jour un produit."""
        try:
            cursor = self.db.db.get_cursor()
            cursor.execute(
                """UPDATE products 
                   SET name=?, category=?, price=?, stock_quantity=?, barcode=?, updated_at=CURRENT_TIMESTAMP 
                   WHERE id=?""",
                (name, category, price, stock, barcode, product_id)
            )
            self.db.db.commit()
            return True
        except Exception as e:
            print(f"Erreur mise à jour: {e}")
            return False
    
    def load_products(self):
        """Charge tous les produits."""
        try:
            cursor = self.db.db.get_cursor()
            cursor.execute("SELECT * FROM products ORDER BY name")
            rows = cursor.fetchall()
            
            products_list = []
            for row in rows:
                products_list.append({
                    'id': row['id'],
                    'barcode': row.get('barcode', ''),
                    'name': row['name'],
                    'category': row.get('category', ''),
                    'price': row['price'],
                    'stock': row['stock_quantity'],
                    'is_internal_barcode': row.get('is_internal_barcode', 0)
                })
            
            if self.view:
                self.view.update_products_table(products_list)
            
            print(f"[BarcodeManager] {len(products_list)} produits chargés")
        except Exception as e:
            print(f"Erreur chargement produits: {e}")
    
    def refresh(self):
        """Rafraîchit l'affichage."""
        self.load_products()


class ProductEditDialog(QDialog):
    """Dialogue pour éditer un produit."""
    
    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Éditer: {product_data['name']}")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(product_data['name'])
        self.name_input.setMinimumHeight(34)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Papeterie", "Fournitures", "Vêtements", "Livres", "Divers"])
        self.category_combo.setCurrentText(product_data.get('category', 'Divers'))
        self.category_combo.setMinimumHeight(34)
        
        self.price_input = QLineEdit(str(product_data['price']))
        self.price_input.setValidator(QDoubleValidator(0, 99999.99, 2))
        self.price_input.setMinimumHeight(34)
        
        self.stock_input = QLineEdit(str(product_data['stock_quantity']))
        self.stock_input.setValidator(QIntValidator(0, 999999))
        self.stock_input.setMinimumHeight(34)
        
        layout.addRow("Nom:", self.name_input)
        layout.addRow("Catégorie:", self.category_combo)
        layout.addRow("Prix:", self.price_input)
        layout.addRow("Stock:", self.stock_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText(),
            'price': float(self.price_input.text() or 0),
            'stock': int(self.stock_input.text() or 0)
        }