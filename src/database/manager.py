"""
Gestionnaire de base de données pour les opérations CRUD.
Gère les produits, codes-barres, ventes et utilisateurs.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from .connection import get_db_connection


class DatabaseManager:
    """
    Gère toutes les opérations CRUD de l'application.
    Utilise DatabaseConnection pour accéder à la base de données.
    """
    
    def __init__(self):
        """Initialise le gestionnaire avec la connexion à la BDD."""
        self.db = get_db_connection()
    
    # ==================== PRODUITS ====================
    
    def add_product(self, name: str, category: str, price: float, stock_quantity: int) -> Optional[int]:
        """
        Ajoute un nouveau produit dans la base de données.
        
        Args:
            name: Nom du produit
            category: Catégorie du produit
            price: Prix du produit
            stock_quantity: Quantité en stock
            
        Returns:
            ID du produit créé ou None en cas d'erreur
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                INSERT INTO products (name, category, price, stock_quantity) 
                VALUES (?, ?, ?, ?)
                """,
                (name, category, price, stock_quantity)
            )
            self.db.commit()
            product_id = cursor.lastrowid
            print(f"✅ Produit '{name}' ajouté avec ID: {product_id}")
            return product_id
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'ajout du produit : {e}")
            self.db.rollback()
            return None
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère un produit par son ID.
        
        Args:
            product_id: ID du produit
            
        Returns:
            Dictionnaire contenant les informations du produit ou None
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération du produit : {e}")
            return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un produit via son code-barres.
        
        Args:
            barcode: Code-barres à rechercher
            
        Returns:
            Dictionnaire avec les infos du produit et du code-barres ou None
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                SELECT p.*, b.barcode_text, b.type as barcode_type
                FROM products p
                JOIN barcodes b ON p.id = b.product_id
                WHERE b.barcode_text = ?
                """,
                (barcode,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération du produit par code-barres : {e}")
            return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les produits de la base de données.
        
        Returns:
            Liste de dictionnaires représentant les produits
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM products ORDER BY name")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération de tous les produits : {e}")
            return []
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """
        Met à jour un produit existant.
        
        Args:
            product_id: ID du produit à mettre à jour
            **kwargs: Champs à mettre à jour (name, category, price, stock_quantity)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            # Construire la requête dynamiquement
            allowed_fields = ['name', 'category', 'price', 'stock_quantity']
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key} = ?")
                    values.append(value)
            
            if not updates:
                print("⚠️ Aucun champ valide à mettre à jour")
                return False
            
            # Ajouter updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(product_id)
            
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            
            cursor = self.db.get_cursor()
            cursor.execute(query, values)
            self.db.commit()
            
            print(f"✅ Produit ID {product_id} mis à jour")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du produit : {e}")
            self.db.rollback()
            return False
    
    def update_product_stock(self, product_id: int, quantity_change: int) -> bool:
        """
        Met à jour le stock d'un produit (ajout ou retrait).
        
        Args:
            product_id: ID du produit
            quantity_change: Changement de quantité (positif = ajout, négatif = retrait)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                UPDATE products 
                SET stock_quantity = stock_quantity + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (quantity_change, product_id)
            )
            self.db.commit()
            print(f"✅ Stock du produit ID {product_id} mis à jour de {quantity_change}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la mise à jour du stock : {e}")
            self.db.rollback()
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """
        Supprime un produit de la base de données.
        
        Args:
            product_id: ID du produit à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.db.commit()
            print(f"✅ Produit ID {product_id} supprimé")
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du produit : {e}")
            self.db.rollback()
            return False
    
    # ==================== CODES-BARRES ====================
    
    def associate_barcode_with_product(
        self, 
        barcode: str, 
        product_id: int, 
        barcode_type: str = 'internal'
    ) -> bool:
        """
        Associe un code-barres à un produit.
        
        Args:
            barcode: Code-barres à associer
            product_id: ID du produit
            barcode_type: Type de code-barres ('internal' ou 'external')
            
        Returns:
            True si l'association a réussi, False sinon
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                INSERT INTO barcodes (barcode_text, product_id, type) 
                VALUES (?, ?, ?)
                """,
                (barcode, product_id, barcode_type)
            )
            self.db.commit()
            print(f"✅ Code-barres '{barcode}' associé au produit ID: {product_id}")
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️ Le code-barres '{barcode}' existe déjà")
            return False
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'association du code-barres : {e}")
            self.db.rollback()
            return False
    
    def get_barcode_by_text(self, barcode_text: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un code-barres par son texte.
        
        Args:
            barcode_text: Texte du code-barres
            
        Returns:
            Dictionnaire contenant les infos du code-barres ou None
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT * FROM barcodes WHERE barcode_text = ?",
                (barcode_text,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération du code-barres : {e}")
            return None
    
    def delete_barcode(self, barcode_text: str) -> bool:
        """
        Supprime un code-barres de la base de données.
        
        Args:
            barcode_text: Texte du code-barres à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM barcodes WHERE barcode_text = ?", (barcode_text,))
            self.db.commit()
            print(f"✅ Code-barres '{barcode_text}' supprimé")
            return True
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la suppression du code-barres : {e}")
            self.db.rollback()
            return False
    
    # ==================== VENTES ====================
    
    def add_sale(
        self, 
        product_id: int, 
        quantity: int, 
        unit_price: float
    ) -> Optional[int]:
        """
        Enregistre une vente et met à jour le stock.
        
        Args:
            product_id: ID du produit vendu
            quantity: Quantité vendue
            unit_price: Prix unitaire de vente
            
        Returns:
            ID de la vente ou None en cas d'erreur
        """
        try:
            total_price = quantity * unit_price
            
            cursor = self.db.get_cursor()
            
            # Enregistrer la vente
            cursor.execute(
                """
                INSERT INTO sales (product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, quantity, unit_price, total_price)
            )
            
            # Mettre à jour le stock
            cursor.execute(
                """
                UPDATE products 
                SET stock_quantity = stock_quantity - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (quantity, product_id)
            )
            
            self.db.commit()
            sale_id = cursor.lastrowid
            print(f"✅ Vente enregistrée (ID: {sale_id}) - {quantity} unités")
            return sale_id
            
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de l'enregistrement de la vente : {e}")
            self.db.rollback()
            return None
    
    def get_sales_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des ventes.
        
        Args:
            limit: Nombre maximum de ventes à récupérer
            
        Returns:
            Liste de dictionnaires représentant les ventes
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                SELECT s.*, p.name as product_name, p.category
                FROM sales s
                JOIN products p ON s.product_id = p.id
                ORDER BY s.sale_date DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération de l'historique des ventes : {e}")
            return []
    
    # ==================== RECHERCHE ====================
    
    def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Recherche des produits par nom ou catégorie.
        
        Args:
            search_term: Terme de recherche
            
        Returns:
            Liste de produits correspondants
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                SELECT * FROM products 
                WHERE name LIKE ? OR category LIKE ?
                ORDER BY name
                """,
                (f"%{search_term}%", f"%{search_term}%")
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la recherche de produits : {e}")
            return []
    
    # ==================== STATISTIQUES ====================
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les produits avec un stock faible.
        
        Args:
            threshold: Seuil de stock minimal
            
        Returns:
            Liste de produits avec stock faible
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                SELECT * FROM products 
                WHERE stock_quantity <= ?
                ORDER BY stock_quantity ASC
                """,
                (threshold,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"❌ Erreur lors de la récupération des produits en stock faible : {e}")
            return []
    
    def close(self):
        """Ferme la connexion à la base de données."""
        self.db.close()