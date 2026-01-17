"""
Manager des ventes - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox
from data.dummy_data.data_dummy_sales import PRODUCTS


class SalesManager(QObject):
    """
    Manager des ventes - Logique métier.
    Sépare complètement la logique de la présentation.
    """
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # État actuel
        self.current_cart = []
        self.all_products = PRODUCTS
    
    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            # Import local pour éviter les imports circulaires
            from src.ui.views.sales_view import SalesView
            
            self.view = SalesView(self.parent)
            self._connect_view_signals()
            
            # Charger les produits initiaux
            self.load_products()
        
        return self.view
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.search_requested.connect(self.load_products)
        self.view.type_filter_changed.connect(self.on_type_filter_changed)
        self.view.add_to_cart_requested.connect(self.add_to_cart)
        self.view.remove_from_cart_requested.connect(self.remove_from_cart)
        self.view.clear_cart_requested.connect(self.clear_cart)
        self.view.checkout_requested.connect(self.process_sale)
    
    @Slot()
    def load_products(self):
        """Charge et filtre les produits selon les critères de recherche."""
        search_term = self.view.get_search_term()
        product_type = self.view.get_type_filter()
        
        filtered = []
        for product in self.all_products:
            type_match = product_type is None or product["type"] == product_type
            search_match = (
                search_term in product["name"].lower() or
                search_term in product["barcode_test"].lower()
            )
            
            if type_match and search_match:
                filtered.append(product)
        
        # Mettre à jour la vue
        self.view.update_products_table(filtered)
        print(f"[SalesManager] {len(filtered)} produits affichés")
    
    @Slot(str)
    def on_type_filter_changed(self, product_type):
        """Gère le changement de filtre de type."""
        print(f"[SalesManager] Filtre type changé: {product_type}")
        self.load_products()
    
    @Slot(int)
    def add_to_cart(self, product_id: int):
        """
        Ajoute un produit au panier.
        
        Args:
            product_id: ID du produit à ajouter
        """
        # Trouver le produit
        product = next((p for p in self.all_products if p["id"] == product_id), None)
        
        if not product:
            print(f"[SalesManager] Produit {product_id} introuvable")
            return
        
        # Vérifier le stock
        if product["stock"] <= 0:
            QMessageBox.warning(
                self.view,
                "Stock épuisé",
                f"{product['name']} n'est plus en stock"
            )
            return
        
        # Format d'affichage du type
        type_display = {
            "unitaire": "UNT",
            "paquet": "PQT",
            "carton": "CRT"
        }.get(product["type"], product["type"])
        
        # Vérifier si déjà dans le panier
        existing = next(
            (item for item in self.current_cart if item["product"]["id"] == product_id),
            None
        )
        
        if existing:
            existing["quantity"] += 1
            print(f"[SalesManager] Quantité augmentée: {product['name']} x{existing['quantity']}")
        else:
            self.current_cart.append({
                "product": product,
                "quantity": 1,
                "type_display": type_display
            })
            print(f"[SalesManager] Produit ajouté: {product['name']}")
        
        self.update_cart_display()
    
    @Slot(int)
    def remove_from_cart(self, product_id: int):
        """
        Retire un produit du panier.
        
        Args:
            product_id: ID du produit à retirer
        """
        for item in self.current_cart[:]:
            if item["product"]["id"] == product_id:
                if item["quantity"] > 1:
                    item["quantity"] -= 1
                    print(f"[SalesManager] Quantité réduite: {item['product']['name']} x{item['quantity']}")
                else:
                    self.current_cart.remove(item)
                    print(f"[SalesManager] Produit retiré: {item['product']['name']}")
                break
        
        self.update_cart_display()
    
    @Slot()
    def clear_cart(self):
        """Vide le panier."""
        self.current_cart = []
        print("[SalesManager] Panier vidé")
        self.update_cart_display()
    
    def update_cart_display(self):
        """Met à jour l'affichage du panier dans la vue."""
        total = sum(
            item["product"]["price"] * item["quantity"]
            for item in self.current_cart
        )
        
        self.view.update_cart_table(self.current_cart, total)
        print(f"[SalesManager] Panier mis à jour: {len(self.current_cart)} articles, Total: {total:.0f} FCFA")
    
    @Slot()
    def process_sale(self):
        """Traite la vente (paiement)."""
        if not self.current_cart:
            QMessageBox.warning(
                self.view,
                "Panier vide",
                "Aucun article dans le panier"
            )
            return
        
        # Vérification du stock
        for item in self.current_cart:
            product = next(p for p in self.all_products if p["id"] == item["product"]["id"])
            if item["quantity"] > product["stock"]:
                QMessageBox.critical(
                    self.view,
                    "Stock insuffisant",
                    f"Stock insuffisant pour {product['name']}\nDisponible: {product['stock']}"
                )
                return
        
        # Calculer le total
        total = sum(
            item["product"]["price"] * item["quantity"]
            for item in self.current_cart
        )
        
        # Confirmation
        reply = QMessageBox.question(
            self.view,
            "Confirmation",
            f"Confirmer la vente ?\n\nTotal: {total:.0f} FCFA\nArticles: {len(self.current_cart)}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Mise à jour du stock
            for item in self.current_cart:
                product = next(p for p in self.all_products if p["id"] == item["product"]["id"])
                product["stock"] -= item["quantity"]
                print(f"[SalesManager] Stock mis à jour: {product['name']} - Reste: {product['stock']}")
            
            QMessageBox.information(
                self.view,
                "Vente enregistrée",
                f"Vente finalisée avec succès\n\nTotal: {total:.0f} FCFA"
            )
            
            # Vider le panier et recharger les produits
            self.clear_cart()
            self.load_products()
            
            print(f"[SalesManager] Vente finalisée: {total:.0f} FCFA")
    
    def refresh(self):
        """Rafraîchit les données affichées."""
        if self.view:
            self.load_products()
            self.update_cart_display()
    
    def get_current_state(self) -> dict:
        """
        Retourne l'état actuel du manager.
        
        Returns:
            Dictionnaire avec l'état actuel
        """
        return {
            "cart": self.current_cart,
            "cart_count": len(self.current_cart),
            "total": sum(item["product"]["price"] * item["quantity"] for item in self.current_cart)
        }