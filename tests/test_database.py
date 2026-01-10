"""
Script de test pour vérifier la nouvelle architecture de la base de données.
"""

from src.database import DatabaseManager, get_db_connection
from src.models import Product, Barcode


def test_connection():
    """Test de connexion à la base de données."""
    print("\n" + "="*60)
    print("TEST 1 : Connexion à la base de données")
    print("="*60)
    
    try:
        db = get_db_connection()
        print("✅ Connexion réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False


def test_add_product():
    """Test d'ajout de produit."""
    print("\n" + "="*60)
    print("TEST 2 : Ajout d'un produit")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        
        # Créer un produit via la classe Product
        product = Product(
            name="Cahier Spirale A4",
            category="Papeterie",
            price=3.50,
            stock_quantity=50
        )
        
        print(f"Produit créé : {product}")
        
        # Ajouter à la BDD
        product_id = db_manager.add_product(
            product.name,
            product.category,
            product.price,
            product.stock_quantity
        )
        
        if product_id:
            print(f"✅ Produit ajouté avec ID: {product_id}")
            return product_id
        else:
            print("❌ Échec de l'ajout du produit")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout : {e}")
        return None


def test_get_product(product_id):
    """Test de récupération d'un produit."""
    print("\n" + "="*60)
    print("TEST 3 : Récupération d'un produit")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        product_data = db_manager.get_product_by_id(product_id)
        
        if product_data:
            product = Product.from_dict(product_data)
            print(f"✅ Produit récupéré : {product}")
            return product
        else:
            print("❌ Produit non trouvé")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")
        return None


def test_associate_barcode(product_id):
    """Test d'association d'un code-barres."""
    print("\n" + "="*60)
    print("TEST 4 : Association d'un code-barres")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        
        # Créer un code-barres
        barcode = Barcode(
            barcode_text="TEST123456789",
            product_id=product_id,
            type='internal'
        )
        
        print(f"Code-barres créé : {barcode}")
        
        # Associer à la BDD
        success = db_manager.associate_barcode_with_product(
            barcode.barcode_text,
            barcode.product_id,
            barcode.type
        )
        
        if success:
            print("✅ Code-barres associé avec succès")
            return True
        else:
            print("❌ Échec de l'association")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'association : {e}")
        return False


def test_get_product_by_barcode():
    """Test de récupération par code-barres."""
    print("\n" + "="*60)
    print("TEST 5 : Récupération par code-barres")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        product_data = db_manager.get_product_by_barcode("TEST123456789")
        
        if product_data:
            print(f"✅ Produit trouvé : {product_data['name']}")
            print(f"   Code-barres : {product_data['barcode_text']}")
            print(f"   Prix : {product_data['price']}€")
            print(f"   Stock : {product_data['stock_quantity']}")
            return True
        else:
            print("❌ Produit non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")
        return False


def test_update_stock(product_id):
    """Test de mise à jour du stock."""
    print("\n" + "="*60)
    print("TEST 6 : Mise à jour du stock")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        
        # Ajouter 10 unités
        success = db_manager.update_product_stock(product_id, 10)
        
        if success:
            # Vérifier le nouveau stock
            product_data = db_manager.get_product_by_id(product_id)
            print(f"✅ Stock mis à jour : {product_data['stock_quantity']} unités")
            return True
        else:
            print("❌ Échec de la mise à jour")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
        return False


def test_search_products():
    """Test de recherche de produits."""
    print("\n" + "="*60)
    print("TEST 7 : Recherche de produits")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        products = db_manager.search_products("Cahier")
        
        print(f"✅ {len(products)} produit(s) trouvé(s) contenant 'Cahier'")
        for product in products:
            print(f"   - {product['name']} ({product['category']}) - {product['price']}€")
        
        return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return False


def test_all_products():
    """Test de récupération de tous les produits."""
    print("\n" + "="*60)
    print("TEST 8 : Liste de tous les produits")
    print("="*60)
    
    try:
        db_manager = DatabaseManager()
        products = db_manager.get_all_products()
        
        print(f"✅ {len(products)} produit(s) total dans la BDD")
        for product in products:
            print(f"   - {product['name']} - Stock: {product['stock_quantity']}")
        
        return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")
        return False


def run_all_tests():
    """Exécute tous les tests."""
    print("\n" + "🚀 DÉBUT DES TESTS".center(60, "="))
    
    results = []
    product_id = None
    
    # Test 1 : Connexion
    results.append(("Connexion", test_connection()))
    
    # Test 2 : Ajout de produit
    product_id = test_add_product()
    results.append(("Ajout produit", product_id is not None))
    
    if product_id:
        # Test 3 : Récupération produit
        product = test_get_product(product_id)
        results.append(("Récupération produit", product is not None))
        
        # Test 4 : Association code-barres
        results.append(("Association code-barres", test_associate_barcode(product_id)))
        
        # Test 5 : Récupération par code-barres
        results.append(("Récupération par code-barres", test_get_product_by_barcode()))
        
        # Test 6 : Mise à jour stock
        results.append(("Mise à jour stock", test_update_stock(product_id)))
    
    # Test 7 : Recherche
    results.append(("Recherche produits", test_search_products()))
    
    # Test 8 : Liste complète
    results.append(("Liste tous produits", test_all_products()))
    
    # Afficher le résumé
    print("\n" + "📊 RÉSUMÉ DES TESTS".center(60, "="))
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Résultats : {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
    else:
        print(f"⚠️ {total - passed} test(s) ont échoué")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()