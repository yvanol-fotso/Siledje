# Gestion Librairie & Papeterie — SILEDJE

Un système de gestion intuitif et complet pour les librairies et papeteries, conçu pour simplifier la gestion quotidienne des stocks, des ventes, des clients et des fournisseurs. Développé avec une interface utilisateur moderne et réactive grâce à **PySide6**.

---

## Fonctionnalités

* **Authentification sécurisée :** Comptes utilisateurs avec mots de passe hachés (bcrypt), rôles et permissions (admin / gérant / employé), verrouillage après tentatives échouées, journal d'audit complet.
* **Gestion des Utilisateurs :** Création, modification, désactivation de comptes et réinitialisation de mot de passe par un administrateur, depuis l'interface.
* **Système de Licence :** Activation hors-ligne par clé signée cryptographiquement (HMAC-SHA256), gestion des plans (Starter / Pro / Premium) et de leur date d'expiration. Activation directement depuis l'interface (module Fichier → onglet Licence).
* **Gestion des Stocks :** Ajout, modification, désactivation et recherche de produits (papeterie, fournitures, manuels scolaires). Catégories et fournisseurs réels, suivi des quantités, prix d'achat/vente distincts, seuils d'alerte de stock bas, emplacements physiques.
* **Codes-barres :** Génération et association de codes-barres internes ou externes (EAN, QR, ISBN) à un produit, relation many-to-one réelle (un produit peut avoir plusieurs codes-barres).
* **Transactions de Vente :** Panier, checkout réel avec numéro de facture auto-généré, paiements par méthode configurable, déduction de stock tracée dans l'historique des mouvements, génération et impression de facture.
* **Gestion des Clients :** Création automatique à la vente (par téléphone), suivi des dépenses cumulées.
* **Gestion des Fournisseurs :** Enregistrement des coordonnées complètes, activation/désactivation.
* **Import / Export CSV :** Produits, fournisseurs et catégories importables/exportables en masse (avec modèles CSV téléchargeables), export utilisateurs en lecture seule (jamais de mot de passe), le tout selon les permissions du rôle connecté.
* **Sauvegarde cloud complète :** Envoi périodique et automatique d'une sauvegarde intégrale de la base vers un espace de stockage cloud (compatible Supabase Storage), avec file d'attente locale — toute tentative échouée (pas de connexion, erreur serveur) est rejouée automatiquement au cycle suivant, sans perte.
* **Synchronisation de données (multi-appareils) :** Synchronisation bidirectionnelle de catégories/fournisseurs/produits et des mouvements de stock avec Supabase, pensée pour une future application mobile compagnon. Le stock n'est jamais écrasé par une simple valeur "la plus récente" : il est reconstruit par fusion additive des mouvements.
* **Rapports et Statistiques :** Filtrage par période (jour/semaine/mois/année/personnalisé), export CSV, impression, calcul du produit le plus vendu.
* **Interface Utilisateur Graphique (GUI) :** Basée sur **PySide6**, thèmes clair/sombre, zoom ajustable, design sobre à teinte d'accent unique.

---

## Technologies Utilisées

* **Python 3.12**
* **PySide6** (interface graphique)
* **SQLite** (base de données locale)
* **Supabase** (synchronisation de données + stockage des sauvegardes, via API REST)
* **bcrypt** (hachage des mots de passe)
* **python-dotenv** (gestion des secrets via `.env`)
* **psutil** (statistiques système en barre de statut)
* **python-barcode** + **Pillow** (génération des codes-barres)
* **python-dateutil** (comparaison fiable des horodatages entre appareils lors de la synchro)
* **urllib** / **socket** (bibliothèque standard — aucune dépendance HTTP supplémentaire pour la synchronisation cloud)

---

## Architecture de la base de données

Le schéma complet (31 tables) est documenté dans `docs/docs_pdf/Siledje_bd_schema_source.pdf`. Chaque domaine métier possède son propre repository, responsable de créer et faire évoluer son propre schéma indépendamment des autres :

| Domaine | Tables | Repository |
|---|---|---|
| Sécurité et accès | `users`, `roles`, `audit_logs` | `user_repository.py` |
| Licences | `licenses` | `license_repository.py` |
| Produits et stock | `categories`, `suppliers`, `products`, `barcodes`, `product_components`, `stock_movements` | `catalog_repository.py` |
| Ventes et caisse | `clients`, `payment_methods`, `sales`, `sale_items`, `sale_payments`, `returns`, `return_items` | `sales_repository.py` |
| Fournisseurs (commandes) | `supplier_orders`, `supplier_order_items` | `supplier_order_repository.py` |
| Vidéosurveillance/IA | `cameras`, `camera_events`, `alerts` | `surveillance_repository.py` |
| Manuels scolaires | `school_levels`, `school_systems`, `school_classes`, `books` | `school_repository.py` |
| Sauvegarde cloud (file d'attente) | `sync_operations` | `sync_repository.py` |
| Synchronisation de données | `sync_state` + colonnes `sync_uuid`/`updated_at` sur les tables catalogue | `cloud_sync_repository.py` |
| Système | `sync_logs`, `settings` | `system_repository.py` |

`src/database/connection.py` gère uniquement la connexion physique (singleton, clés étrangères, ouverture/fermeture) — il ne définit aucune table métier. Ajouter un nouveau domaine ne nécessite jamais de modifier ce fichier.

### Migrations de schéma

`src/database/migrations/migration_manager.py` détecte automatiquement tout fichier `.py` du dossier exposant `upgrade(conn)` (et optionnellement `downgrade(conn)`), l'applique une seule fois, et trace son exécution dans la table `migrations` :

```python
from src.database.migrations.migration_manager import run_migrations
run_migrations()
```

| Fichier | Rôle |
|---|---|
| `cloud_sync_migration.py` | Ajoute `sync_uuid` + `updated_at` aux tables catalogue, crée `sync_state` — prérequis à la synchronisation de données multi-appareils |

---

## Architecture du Projet

```
SILEDJE/
├── config.json                  # Configuration centralisée
├── requirements.txt             # Dépendances Python
├── .env                         # Secrets locaux (NON versionné — voir Sécurité)
├── .env.example                 # Modèle de .env (versionné, sans vraies valeurs)
├── librairie.db                 # Base de données SQLite (générée au 1er lancement)
├── README.md
│
├── scripts/                     # Outils réservés au vendeur/support (jamais livrés au client)
│   ├── generate_license_cli.py
│   └── reset_password_cli.py
│
├── assets/
│   ├── icons/
│   ├── images/
│   └── styles/
│       ├── light.qss
│       └── dark.qss
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # Point d'entrée réel (python -m src.main)
│   │
│   ├── Beans/
│   │   ├── User.py
│   │   └── Role.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py             # Connexion SQLite (singleton, aucun schéma métier)
│   │   ├── manager.py
│   │   ├── migrations/
│   │   │   ├── migration_manager.py
│   │   │   └── cloud_sync_migration.py
│   │   └── repositories/
│   │       ├── user_repository.py
│   │       ├── license_repository.py
│   │       ├── catalog_repository.py
│   │       ├── sales_repository.py
│   │       ├── supplier_order_repository.py
│   │       ├── surveillance_repository.py
│   │       ├── school_repository.py
│   │       ├── sync_repository.py          # File d'attente de sauvegarde cloud
│   │       ├── cloud_sync_repository.py    # Curseurs de synchro de données
│   │       └── system_repository.py
│   │
│   ├── managers/
│   │   ├── accueil_manage.py
│   │   ├── auth/auth_manager.py
│   │   ├── license/license_manager.py
│   │   ├── admin/admin_manager.py
│   │   ├── stock/stock_manager.py
│   │   ├── sales/sales_manager.py
│   │   ├── report/report_manager.py
│   │   ├── barcode/barcode_manager.py
│   │   ├── supplier/supplier_manager.py
│   │   ├── file/file_manager.py            # Import/Export CSV, Sauvegarde, Licence
│   │   ├── sync/
│   │   │   ├── __init__.py
│   │   │   ├── network_utils.py            # Test de connectivité partagé (évite les imports circulaires)
│   │   │   ├── sync_manager.py             # Sauvegarde cloud complète (fichier .db entier)
│   │   │   ├── cloud_data_sync_manager.py  # Synchro bidirectionnelle de données (Supabase)
│   │   │   └── supabase_rest_client.py     # Client REST générique (PostgREST)
│   │   ├── security/
│   │   └── ai/
│   │
│   ├── ui/
│   │   ├── windows/
│   │   │   ├── main_window.py
│   │   │   ├── login_window.py
│   │   │   └── license_window.py
│   │   ├── views/
│   │   │   ├── file_view.py                # Onglets Produits/Fournisseurs/Catégories/Utilisateurs/Sauvegarde/Licence
│   │   │   └── sync_view.py                # Statut, historique, paramètres d'automatisation
│   │   └── widgets/
│   │       └── ModalView.py
│   │
│   └── utils/
│       ├── config.py
│       ├── notifications.py
│       ├── theme_manager.py
│       ├── license_crypto.py
│       └── helpers.py
│
├── data/
│   ├── backups/
│   └── dummy_data/
│       └── data_home.py              # Encore utilisé par AccueilManager (migration à venir)
│
└── docs/
    ├── docs_pdf/
    │   └── Siledje_bd_schema_source.pdf
    ├── architecture.md
    ├── user_manual.md
    └── dev_manual.md
```

> **Note sur le dummy data** : `StockManager`, `SalesManager` et `ReportManager` sont connectés aux vraies tables SQLite. `AccueilManager` (module Manuels Scolaires côté accueil) utilise encore `data/dummy_data/data_home.py` ; sa migration vers `school_repository.py` (déjà créé) est en cours d'investigation (voir Chantiers en cours).

---

## Sécurité et Configuration requise

### Fichier `.env` (obligatoire, jamais commité)

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
```
SILEDJE_LICENSE_SECRET=votre_cle_generee_ici
```

⚠️ **`.env` ne doit jamais être suivi par Git.** Vérifie que `.gitignore` contient bien une ligne `.env`. S'il a déjà été commité par erreur, retire-le du suivi (`git rm --cached .env`) et régénère toutes les clés qu'il contenait — une clé qui a transité par un commit, même supprimé ensuite, doit être considérée comme potentiellement exposée.

### Variables optionnelles — synchronisation cloud

```
# Sauvegarde cloud complète (fichier .db entier)
SILEDJE_CLOUD_SYNC_URL=https://votre-projet.supabase.co/storage/v1/object/backups
SILEDJE_CLOUD_SYNC_TOKEN=votre_cle_secrete_supabase

# Synchronisation de données multi-appareils (Supabase REST)
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_API_KEY=votre_cle_secrete_supabase
```

⚠️ Utilisez la clé **secrète** (`service_role` / `sb_secret_...`), jamais la clé publique (`anon` / `sb_publishable_...`) — cette dernière est réservée à un futur client mobile authentifié, une fois le RLS configuré côté Supabase.

### Compte administrateur par défaut

```
Nom d'utilisateur : admin
Mot de passe       : admin123
```
⚠️ À changer immédiatement après la première connexion.

### Réinitialisation d'urgence

```bash
python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>
```

---

## Permissions et rôles

| Action | Permission requise |
|---|---|
| Importer produits / fournisseurs / catégories | `can_manage_stock` |
| Exporter les utilisateurs | `can_manage_users` |
| Activer une licence | `can_configure_system` |
| Restaurer / supprimer une sauvegarde | `can_configure_system` |
| Configurer ou lancer une synchronisation (sauvegarde ou données) | `can_configure_system` |

Chaque action sensible est revérifiée côté manager, jamais seulement côté bouton désactivé à l'écran.

---

## Installation et Lancement (Windows)

**ATTENTION : Ce projet ne fonctionne qu'avec Python 3.12.**

```bash
py -3.12 -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Configurez `.env` (voir ci-dessus), puis :

```bash
python -m src.main
```

**Ne faites PAS** : `python src/main.py` (problèmes d'imports internes)

---

## Génération de licences (réservé au vendeur)

```bash
python scripts/generate_license_cli.py "Nom du Client" pro 3 365
```

---

## Import / Export et Sauvegarde (module Fichier)

* **Produits / Fournisseurs / Catégories** : import/export CSV (`;`, UTF-8), modèle téléchargeable. Catégories et fournisseurs référencés par nom sont créés automatiquement.
* **Utilisateurs** : export lecture seule, jamais de mot de passe.
* **Sauvegarde** : création manuelle, historique local, restauration avec sauvegarde de sécurité automatique.
* **Licence** : statut de la licence active, activation par collage ou fichier `.txt`/`.lic`.

## Synchronisation cloud

Deux mécanismes distincts, complémentaires, tous deux pilotables depuis la même vue **Synchronisation Cloud** :

* **Sauvegarde complète** (`SyncManager`) : envoie périodiquement le fichier `.db` entier vers un espace de stockage. File d'attente locale, reprise automatique en cas d'échec.
* **Synchronisation de données** (`CloudDataSyncManager`) : catégories/fournisseurs/produits en "dernière écriture gagne" (`updated_at`) ; mouvements de stock fusionnés de façon additive — jamais écrasés, pour ne jamais perdre une vente enregistrée simultanément sur deux appareils hors-ligne.

---

## Chantiers en cours

* Numérotation/affichage des ID produits (revue à prévoir avec `catalog_repository.py`)
* Formulaire de création produit : ordre des champs (catégorie / cases à cocher) à revoir dans `StockManager`/vue associée
* Tableau des manuels scolaires vide côté Accueil : `AccueilManager`/`AccueilView` à examiner avec `SchoolRepository.get_books_for_class()`
* Extension des adaptateurs de synchronisation de données à `barcodes` et `product_components` (même patron que `ProductAdapter`)
* Activation du RLS + policies Supabase avant tout branchement d'une application mobile
* Bouton de purge de l'historique de synchronisation

---

## Tests de la Base de Données

```bash
python -m tests.test_database
```

---

## Documentation et ressources

- [Schéma complet de la base de données (PDF)](docs/docs_pdf/Siledje_bd_schema_source.pdf)
- [Documentation version 1 (PDF)](docs/docs_pdf/Librairie_Papetierie-V1.pdf)

---

## Comment Contribuer

1. Forkez ce dépôt.
2. `git checkout -b feature/nom-de-votre-fonctionnalite`
3. `git commit -m 'feat: Ajout de la fonctionnalité X'`
4. Poussez et ouvrez une Pull Request.

---

## Licence

Ce projet est distribué sous la licence **MIT License**. Voir le fichier `LICENSE` à la racine du dépôt.