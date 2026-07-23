# Gestion Librairie & Papeterie — SILEDJE

Un système de gestion intuitif et complet pour les librairies et papeteries, conçu pour simplifier la gestion quotidienne des stocks, des ventes, des clients et des fournisseurs. Développé avec une interface utilisateur moderne et réactive grâce à **PySide6**.

---

## Fonctionnalités

* **Authentification sécurisée :** Comptes utilisateurs avec mots de passe hachés (bcrypt), rôles et permissions (admin / gérant / employé), verrouillage après tentatives échouées, journal d'audit complet.
* **Gestion des Utilisateurs :** Création, modification, désactivation de comptes et réinitialisation de mot de passe par un administrateur, depuis l'interface.
* **Système de Licence :** Activation hors-ligne par clé signée cryptographiquement (HMAC-SHA256), gestion des plans (Starter / Pro / Premium) et de leur date d'expiration.
* **Gestion des Stocks :** Ajout, modification, désactivation et recherche de produits (papeterie, fournitures, manuels scolaires). Catégories et fournisseurs réels, suivi des quantités, prix d'achat/vente distincts, seuils d'alerte de stock bas, emplacements physiques.
* **Codes-barres :** Génération et association de codes-barres internes ou externes (EAN, QR, ISBN) à un produit, avec relation many-to-one réelle (un produit peut avoir plusieurs codes-barres).
* **Transactions de Vente :** Panier, checkout réel avec numéro de facture auto-généré, paiements par méthode configurable, déduction de stock tracée dans l'historique des mouvements, génération et impression de facture.
* **Gestion des Clients :** Création automatique à la vente (par téléphone), suivi des dépenses cumulées.
* **Gestion des Fournisseurs :** Enregistrement des coordonnées complètes, activation/désactivation.
* **Rapports et Statistiques :** Filtrage par période (jour/semaine/mois/année/personnalisé), export CSV, impression, calcul du produit le plus vendu.
* **Synchronisation Cloud (Supabase) :** Synchronisation des données locales SQLite vers Supabase via son API REST, avec journalisation des synchronisations (`sync_logs`), suivi de l'état (succès/échec) et vue dédiée dans l'interface pour déclencher et superviser la synchronisation.
* **Interface Utilisateur Graphique (GUI) :** Basée sur **PySide6**, thèmes clair/sombre, zoom ajustable.

---

## Technologies Utilisées

* **Python 3.12**
* **PySide6** (interface graphique)
* **SQLite** (base de données locale)
* **Supabase** (synchronisation et sauvegarde cloud via API REST)
* **requests** (client HTTP pour l'API REST Supabase)
* **bcrypt** (hachage des mots de passe)
* **python-dotenv** (gestion des secrets via `.env`)
* **psutil** (statistiques système en barre de statut)
* **python-barcode** + **Pillow** (génération des codes-barres)

---

## Architecture de la base de données

Le schéma complet (31 tables) est documenté dans `docs/docs_pdf/Siledje_bd_schema_source.pdf`. Chaque domaine métier possède son propre repository, responsable de créer et faire évoluer son propre schéma indépendamment des autres :

| Domaine | Tables | Repository |
|---|---|---|
| Sécurité et accès | `users`, `roles`, `audit_logs` | `user_repository.py` |
| Licences | `licenses` | `license_repository.py` |
| Produits et stock | `categories`, `suppliers`, `products`, `barcodes`, `product_components`, `stock_movements` | `catalog_repository.py` |
| Ventes et caisse | `clients`, `payment_methods`, `sales`, `sale_items`, `sale_payments`, `returns`, `return_items` | `sales_repository.py` |
| Fournisseurs | `supplier_orders`, `supplier_order_items` | `supplier_order_repository.py` |
| Vidéosurveillance/IA | `cameras`, `camera_events`, `alerts` | `surveillance_repository.py` |
| Manuels scolaires | `school_levels`, `school_systems`, `school_classes`, `books` | `school_repository.py` |
| Système / Synchronisation | `sync_logs`, `settings` | `system_repository.py`, `sync_repository.py`, `cloud_sync_repository.py` |

`src/database/connection.py` gère uniquement la connexion physique (singleton, clés étrangères, ouverture/fermeture) — il ne définit aucune table métier. Ajouter un nouveau domaine ne nécessite jamais de modifier ce fichier.

La table `sync_logs` trace chaque opération de synchronisation (horodatage, statut, domaine concerné), et la migration dédiée (`src/database/migrations/cloud_sync_migration.py`) prépare le schéma local nécessaire à la synchronisation cloud.

---

## Architecture du Projet

```
SILEDJE/
├── config.json                  # Configuration centralisée
├── requirements.txt             # Dépendances Python
├── .env                         # Secrets locaux (NON versionné, voir Sécurité)
├── .env.example                 # Modèle de .env (versionné, sans vraies valeurs)
├── librairie.db                 # Base de données SQLite (générée au 1er lancement)
├── README.md
│
├── scripts/                     # Outils réservés au vendeur/support (jamais livrés au client)
│   ├── generate_license_cli.py  # Génération de clés de licence
│   └── reset_password_cli.py    # Réinitialisation de mot de passe en urgence
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
│   ├── Beans/                        # Objets métier (entités applicatives)
│   │   ├── User.py                   # Utilisateur authentifié
│   │   └── Role.py                   # Rôle et permissions
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py             # Connexion SQLite (singleton, aucun schéma métier)
│   │   ├── manager.py
│   │   ├── migrations/
│   │   │   └── cloud_sync_migration.py   # Migration du schéma local pour la sync cloud
│   │   └── repositories/             # Accès aux données, un fichier par domaine métier
│   │       ├── user_repository.py
│   │       ├── license_repository.py
│   │       ├── catalog_repository.py
│   │       ├── sales_repository.py
│   │       ├── supplier_order_repository.py
│   │       ├── surveillance_repository.py
│   │       ├── school_repository.py
│   │       ├── system_repository.py
│   │       ├── sync_repository.py        # Accès aux logs et à l'état de synchronisation
│   │       └── cloud_sync_repository.py  # Accès aux données destinées au push/pull cloud
│   │
│   ├── managers/                     # Logique métier (Contrôleur)
│   │   ├── accueil_manage.py
│   │   ├── auth/auth_manager.py      # Authentification, hachage, verrouillage
│   │   ├── license/license_manager.py
│   │   ├── admin/admin_manager.py    # Gestion des utilisateurs
│   │   ├── stock/stock_manager.py    # Connecté à catalog_repository
│   │   ├── sales/sales_manager.py    # Connecté à sales_repository + catalog_repository
│   │   ├── report/report_manager.py  # Connecté à sales_repository
│   │   ├── barcode/barcode_manager.py# Connecté à catalog_repository
│   │   ├── supplier/supplier_manager.py # Connecté à catalog_repository
│   │   ├── sync/                     # Synchronisation cloud (Supabase)
│   │   │   ├── __init__.py
│   │   │   ├── sync_manager.py             # Orchestration de la synchronisation
│   │   │   ├── cloud_data_sync_manager.py  # Logique de push/pull par domaine métier
│   │   │   └── supabase_rest_client.py     # Client HTTP pour l'API REST Supabase
│   │   ├── security/
│   │   └── ai/
│   │
│   ├── ui/
│   │   ├── windows/
│   │   │   ├── main_window.py        # Intègre désormais l'accès à la vue de synchronisation
│   │   │   ├── login_window.py
│   │   │   └── license_window.py
│   │   ├── views/
│   │   │   └── sync_view.py          # Vue de supervision/déclenchement de la sync cloud
│   │   └── widgets/
│   │       └── ModalView.py
│   │
│   └── utils/
│       ├── config.py
│       ├── notifications.py
│       ├── theme_manager.py
│       ├── license_crypto.py         # Signature/vérification HMAC des clés de licence
│       └── helpers.py
│
├── data/
│   ├── backups/
│   └── dummy_data/
│       └── data_home.py              # Encore utilisé par AccueilManager (migration à venir)
│
└── docs/
    ├── docs_pdf/
    │   └── Siledje_bd_schema_source.pdf   # Schéma complet des 31 tables
    ├── architecture.md
    ├── user_manual.md
    └── dev_manual.md
```

> **Note sur le dummy data** : `StockManager`, `SalesManager` et `ReportManager` sont désormais connectés aux vraies tables SQLite — plus aucune donnée factice n'est utilisée pour ces modules. `AccueilManager` (module Manuels Scolaires côté accueil) utilise encore `data/dummy_data/data_home.py` ; sa migration vers `school_repository.py` (déjà créé) est prévue mais pas encore branchée.

> **Note sur la synchronisation cloud** : le module `src/managers/cloud/cloud_manager.py` a été retiré et remplacé par le module `src/managers/sync/` (plus complet : `sync_manager.py`, `cloud_data_sync_manager.py`, `supabase_rest_client.py`), qui s'appuie sur les nouveaux repositories `sync_repository.py` et `cloud_sync_repository.py`.

---

## Sécurité et Configuration requise

### Fichier `.env` (obligatoire)

Le système de licence a besoin d'une clé secrète locale, **jamais committée sur Git**.

1. Copiez `.env.example` vers `.env`
2. Générez une clé secrète unique :
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Renseignez-la dans `.env` :
   ```
   SILEDJE_LICENSE_SECRET=votre_cle_generee_ici
   ```

⚠️ Sans ce fichier, l'application refuse de démarrer.

### Synchronisation Cloud (Supabase)

La synchronisation cloud s'appuie sur l'API REST de Supabase. Ajoutez également ces variables dans votre `.env` :

```
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre_cle_api_supabase
```

⚠️ Ces valeurs sont propres à votre projet Supabase et ne doivent jamais être committées. Sans elles, les fonctionnalités de synchronisation cloud restent désactivées, mais l'application fonctionne normalement en local.

### Compte administrateur par défaut

Au tout premier lancement, si aucun utilisateur n'existe en base :

```
Nom d'utilisateur : admin
Mot de passe       : admin123
```

⚠️ **À changer immédiatement** après la première connexion (Administration → Gestion des Utilisateurs).

### Réinitialisation d'urgence

Si le compte admin est bloqué (mot de passe perdu ou verrouillage après 5 tentatives) :

```bash
python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>
```

Réservé au support technique — ne jamais distribuer ce script au client final.

---

## Installation et Lancement (Windows)

**ATTENTION : Ce projet ne fonctionne qu'avec Python 3.12.**

### 1. Installation de Python 3.12

1. Téléchargez et installez Python 3.12 depuis le site officiel.
2. Cochez **"Add python.exe to PATH"** lors de l'installation.
3. Vérifiez :
   ```bash
   py -0
   ```

### 2. Configuration du Projet

```bash
git clone https://github.com/yvanol-fotso/librairie_papeterie.git
cd librairie_papeterie
```

### 3. Créer et Activer l'Environnement Virtuel

```bash
py -3.12 -m venv venv
.\venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configurer le fichier `.env`

Voir la section **Sécurité et Configuration requise** ci-dessus (clé de licence + identifiants Supabase).

---

## Lancement de l'Application

Depuis la racine du projet, environnement virtuel activé :

```bash
python -m src.main
```

**Ordre d'affichage au démarrage :**
1. Écran d'**activation de licence** (si aucune licence valide n'est enregistrée)
2. Écran de **connexion** (authentification)
3. Fenêtre principale de l'application

**Ne faites PAS** : `python src/main.py` (problèmes d'imports internes)

---

## Génération de licences (réservé au vendeur)

```bash
python scripts/generate_license_cli.py "Nom du Client" pro 3 365
```

Paramètres : nom du client, plan (`starter` / `pro` / `premium`), nombre max d'utilisateurs, durée de validité en jours (ou `--illimitee`).

⚠️ Ce script ne doit **jamais** être distribué avec l'application livrée au client.

---

## Workflow recommandé pour un nouveau produit

1. **Gestion de Stock** → créer le produit (nom, catégorie, fournisseur, prix, stock initial, code-barres optionnel)
2. **Gestion Barcode** → si le code-barres n'a pas été saisi à la création, y générer un code interne ou associer un code externe scanné
3. **Point de Vente** → le produit apparaît automatiquement dans la recherche dès qu'il est actif et en stock

---

## Synchronisation Cloud

Le module de synchronisation (`src/managers/sync/`) permet d'envoyer et récupérer les données entre la base SQLite locale et un projet Supabase distant, via `supabase_rest_client.py`.

1. Configurez `SUPABASE_URL` et `SUPABASE_KEY` dans `.env` (voir section **Sécurité et Configuration requise**)
2. Ouvrez la vue **Synchronisation** dans l'application (`sync_view.py`, accessible depuis la fenêtre principale)
3. Déclenchez la synchronisation manuellement ; chaque exécution est journalisée dans `sync_logs` (statut, horodatage) et consultable depuis cette même vue

---

## Tests de la Base de Données

```bash
python -m tests.test_database
```

---

## Documentation et ressources

### Documentation PDF

- [Schéma complet de la base de données (PDF)](docs/docs_pdf/Siledje_bd_schema_source.pdf)
- [Documentation version 1 (PDF)](docs/docs_pdf/Librairie_Papetierie-V1.pdf)

---

## Comment Contribuer

1. Forkez ce dépôt.
2. Créez une branche :
   ```bash
   git checkout -b feature/nom-de-votre-fonctionnalite
   ```
3. Commitez :
   ```bash
   git commit -m 'feat: Ajout de la fonctionnalité X'
   ```
4. Poussez et ouvrez une Pull Request.

---

## Licence

Ce projet est distribué sous la licence **MIT License**. Voir le fichier `LICENSE` à la racine du dépôt.