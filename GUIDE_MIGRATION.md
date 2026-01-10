# 📋 Guide de Migration - Restructuration du Projet

## 🎯 Objectif
Restructurer ton projet `librairie_papeterie` selon la nouvelle architecture modulaire pour améliorer la maintenabilité et l'organisation du code.

---

## 📁 Structure Cible

```
LIBRAIRIE_PAPETERIE/
├── main.py                    # À créer (point d'entrée)
├── config.json                # Configuration unique
├── requirements.txt
├── README.md                  # ✅ Déjà mis à jour
│
├── assets/                    # ✅ Déjà présent
│   ├── icons/
│   ├── images/
│   └── styles/
│
├── src/
│   ├── __init__.py
│   │
│   ├── models/               # 🆕 NOUVEAU
│   │   ├── __init__.py
│   │   ├── product.py        # ✅ Créé
│   │   └── barcode.py        # ✅ Créé
│   │
│   ├── database/             # 🔄 RESTRUCTURÉ
│   │   ├── __init__.py       # ✅ Créé
│   │   ├── connection.py     # ✅ Créé
│   │   └── manager.py        # ✅ Créé
│   │
│   ├── ui/                   # ✅ Déjà présent
│   │   ├── windows/
│   │   ├── views/
│   │   └── widgets/
│   │
│   ├── modules/              # ✅ Déjà présent
│   └── utils/                # ✅ Déjà présent
│
├── data/                     # ✅ Déjà présent
└── docs/                     # ✅ Déjà présent
```

---

## 🚀 Plan de Migration Étape par Étape

### ✅ Étape 1 : Fichiers Créés
Les fichiers suivants ont été créés et sont prêts à être intégrés :

1. **`src/database/connection.py`** ✅
   - Gère la connexion unique à SQLite (Singleton)
   - Crée les tables automatiquement
   - Support des transactions

2. **`src/database/manager.py`** ✅
   - Toutes les opérations CRUD
   - Gestion produits, codes-barres, ventes
   - Fonctions de recherche et statistiques

3. **`src/database/__init__.py`** ✅
   - Facilite les imports

4. **`src/models/product.py`** ✅
   - Classe Product avec validation
   - Méthodes utilitaires (is_low_stock, update_stock, etc.)

5. **`src/models/barcode.py`** ✅
   - Classe Barcode avec validation
   - Distinction internal/external

6. **`src/models/__init__.py`** ✅
   - Facilite les imports

---

### 📦 Étape 2 : Actions à Réaliser

#### 2.1 Créer les dossiers manquants

```bash
# À la racine de ton projet
mkdir -p src/database
mkdir -p src/models
```

#### 2.2 Copier les fichiers créés

**Pour le dossier `database/` :**
```bash
# Copier connection.py
cp connection.py src/database/

# Copier manager.py
cp manager.py src/database/

# Copier __init__.py
cp __init__.py src/database/
```

**Pour le dossier `models/` :**
```bash
# Copier product.py
cp product.py src/models/

# Copier barcode.py
cp barcode.py src/models/

# Copier models_init.py vers __init__.py
cp models_init.py src/models/__init__.py
```

#### 2.3 Supprimer les anciens fichiers

**À supprimer :**
- ❌ `config/settings.json` (à la racine)
- ❌ `src/config/settings.json` (garder un seul config.json à la racine)
- ❌ `src/data/database_manager.py` (remplacé par src/database/)
- ❌ `src/core/database.py` (si duplication)
- ❌ `src/db/` (fusionné dans src/database/)
- ❌ Dossier `Beans/` (remplacé par `models/`)

#### 2.4 Créer le config.json unique

```json
{
    "app_name": "Librairie-Papeterie",
    "version": "2.0.0",
    "database": {
        "name": "data/librairie.db",
        "auto_backup": true,
        "backup_path": "data/backups/"
    },
    "ui": {
        "theme": "dark_style.qss",
        "default_theme": "dark_style.qss",
        "auto_theme": false,
        "confirm_exit": true
    },
    "stock": {
        "low_stock_threshold": 10,
        "alert_enabled": true
    }
}
```

---

### 🔄 Étape 3 : Mettre à Jour les Imports

#### Ancien code (à remplacer) :
```python
from src.data.database_manager import DatabaseManager
from src.core.database import DatabaseManager
```

#### Nouveau code :
```python
from src.database import DatabaseManager, get_db_connection
from src.models import Product, Barcode
```

#### Exemples d'utilisation :

**Initialisation :**
```python
from src.database import DatabaseManager

# Créer une instance du manager
db_manager = DatabaseManager()
```

**Ajouter un produit :**
```python
from src.models import Product

# Créer un objet produit
product = Product(
    name="Cahier A4",
    category="Papeterie",
    price=2.50,
    stock_quantity=100
)

# Ajouter à la BDD
product_id = db_manager.add_product(
    product.name,
    product.category,
    product.price,
    product.stock_quantity
)
```

**Récupérer un produit par code-barres :**
```python
product_data = db_manager.get_product_by_barcode("1234567890")
if product_data:
    product = Product.from_dict(product_data)
    print(product)
```

---

### 🧪 Étape 4 : Tester la Migration

#### Test 1 : Connexion à la BDD
```python
from src.database import get_db_connection

db = get_db_connection()
print("✅ Connexion réussie")
```

#### Test 2 : Ajouter un produit
```python
from src.database import DatabaseManager

db = DatabaseManager()
product_id = db.add_product("Test", "Test", 10.0, 50)
print(f"✅ Produit créé avec ID: {product_id}")
```

#### Test 3 : Récupérer tous les produits
```python
from src.database import DatabaseManager

db = DatabaseManager()
products = db.get_all_products()
print(f"✅ {len(products)} produits trouvés")
```

---

## 🔧 Avantages de la Nouvelle Architecture

### ✅ Séparation des Responsabilités
- **`connection.py`** : Uniquement la connexion
- **`manager.py`** : Uniquement les opérations CRUD
- **`models/`** : Uniquement les classes métier

### ✅ Singleton Pattern
- Une seule connexion partagée dans toute l'app
- Évite les conflits de connexion multiples

### ✅ Validation des Données
- Classes Product et Barcode avec validation intégrée
- Évite les données invalides dans la BDD

### ✅ Testabilité
- Chaque module peut être testé indépendamment
- Plus facile à déboguer

### ✅ Évolutivité
- Facile d'ajouter de nouveaux modèles
- Structure claire pour les nouveaux développeurs

---

## 📝 Checklist de Migration

- [ ] Créer les dossiers `src/database/` et `src/models/`
- [ ] Copier les fichiers créés aux bons emplacements
- [ ] Créer le fichier `config.json` unique à la racine
- [ ] Supprimer les anciens fichiers dupliqués
- [ ] Mettre à jour tous les imports dans le code existant
- [ ] Tester la connexion à la BDD
- [ ] Tester les opérations CRUD
- [ ] Vérifier que l'application démarre correctement
- [ ] Faire un commit Git avec un message clair

---

## 🆘 En Cas de Problème

### Erreur d'import
```python
# Si tu vois : ModuleNotFoundError: No module named 'src.database'
# Solution : Vérifier que __init__.py existe dans src/database/
```

### Erreur de connexion BDD
```python
# Si la connexion échoue
# Vérifier que le dossier data/ existe
# Le fichier connection.py le crée automatiquement
```

### Erreur de migration
```python
# Si les anciennes données ne sont pas accessibles
# La structure des tables est compatible
# Aucune migration de données nécessaire
```

---

## 🎉 Après la Migration

Une fois la migration terminée, tu auras :
- ✅ Une architecture propre et modulaire
- ✅ Un code plus maintenable
- ✅ Une base solide pour ajouter de nouvelles fonctionnalités
- ✅ Une meilleure séparation des responsabilités

**Bon courage pour la migration ! 🚀**