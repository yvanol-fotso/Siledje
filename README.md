# 📚 SILEDJE — Gestion Librairie & Papeterie

Un système de gestion intuitif et complet pour les librairies et papeteries, conçu pour simplifier la gestion quotidienne des stocks, des ventes, des clients et des fournisseurs. Développé avec une interface utilisateur moderne et réactive grâce à **PySide6**.

---

##  Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Architecture](#-architecture-du-projet)
- [Base de données](#-base-de-données)
- [Configuration et sécurité](#-configuration-et-sécurité)
- [Installation](#-installation-et-lancement)
- [Compilation et distribution (.exe)](#-compilation-et-distribution-exe)
- [Déployer chez un nouveau client](#-déployer-chez-un-nouveau-client-sans-recompiler)
- [Licences](#-licences)
- [Chantiers en cours](#-chantiers-en-cours)

---

##  Fonctionnalités

| Module | Description |
|--------|-------------|
| **Authentification** | Comptes utilisateurs avec mots de passe hachés (bcrypt), rôles et permissions (admin / gérant / employé), verrouillage après tentatives échouées, journal d'audit complet |
| **Gestion des Utilisateurs** | Création, modification, désactivation de comptes et réinitialisation de mot de passe par un administrateur |
| **Système de Licence** | Activation hors-ligne par clé signée cryptographiquement (**Ed25519** : la clé publique vérifie dans l'application, la clé privée reste chez le vendeur), gestion des plans (Starter / Pro / Premium) |
| **Gestion des Stocks** | Ajout, modification, désactivation et recherche de produits (papeterie, fournitures, manuels scolaires). Catégories et fournisseurs réels, suivi des quantités, prix d'achat/vente distincts, seuils d'alerte de stock bas |
| **Codes-barres** | Génération et association de codes-barres internes ou externes (EAN, QR, ISBN) à un produit, relation many-to-one réelle |
| **Point de Vente** | Panier, checkout réel avec numéro de facture auto-généré, paiements par méthode configurable, déduction de stock tracée dans l'historique des mouvements, génération et impression de facture |
| **Gestion des Clients** | Création automatique à la vente (par téléphone), suivi des dépenses cumulées |
| **Gestion des Fournisseurs** | Enregistrement des coordonnées complètes, activation/désactivation |
| **Import / Export CSV** | Produits, fournisseurs et catégories importables/exportables en masse (avec modèles CSV téléchargeables), export utilisateurs en lecture seule |
| **Sauvegarde cloud complète** | Envoi périodique et automatique d'une sauvegarde intégrale de la base vers Supabase Storage, avec file d'attente locale et reprise automatique |
| **Synchronisation de données** | Synchronisation bidirectionnelle de catégories/fournisseurs/produits et des mouvements de stock avec Supabase. Le stock n'est jamais écrasé : il est reconstruit par fusion additive des mouvements |
| **Rapports et Statistiques** | Filtrage par période (jour/semaine/mois/année/personnalisé), export CSV, impression, calcul du produit le plus vendu |
| **Interface Graphique** | Basée sur **PySide6**, thèmes clair/sombre, zoom ajustable, design sobre à teinte d'accent unique |
| **Configuration par client** | Un fichier de configuration propre à chaque client (projet Supabase dédié), choisi au premier lancement : un seul installeur pour tous, aucune recompilation |

---

## 🛠 Technologies

| Technologie | Utilisation |
|-------------|-------------|
| **Python 3.12** | Langage principal |
| **PySide6** | Interface graphique (Qt pour Python) |
| **SQLite** | Base de données locale |
| **Supabase** | Synchronisation de données + stockage des sauvegardes (API REST), un projet par client |
| **bcrypt** | Hachage des mots de passe |
| **cryptography** | Signature et vérification des licences (Ed25519) |
| **python-dotenv** | Lecture de `app.env` (commun) et du `.env` du client |
| **psutil** | Statistiques système en barre de statut |
| **python-barcode + Pillow** | Génération des codes-barres |
| **python-dateutil** | Comparaison fiable des horodatages entre appareils |
| **urllib / socket** | Bibliothèque standard — aucune dépendance HTTP supplémentaire |
| **PyInstaller** | Génération de l'exécutable Windows (`Siledje.exe`) à partir de `Siledje.spec` |
| **Inno Setup** | Création de l'installeur Windows (`Siledje_Setup_x.y.z.exe`) |

---

##  Architecture du Projet

```
SILEDJE/
├── run.py                          # Point d'entrée pour PyInstaller (appelle src.main)
├── Siledje.spec                    # Configuration PyInstaller (versionné)
├── installer.iss                   # Script Inno Setup (création du Setup.exe)
├── config.json                     # Configuration centralisée
├── requirements.txt                # Dépendances Python
├── app.env                         # Variables communes à tous les clients, embarqué (NON versionné)
├── app.env.example                 # Modèle de app.env (versionné)
├── .env                            # Configuration locale de développement (NON versionné)
├── .env.example                    # Modèle de .env (versionné, sans valeurs)
├── clients/                        # Fichiers de configuration des clients (NON versionné, vendeur uniquement)
│   └── SIL-0001/
│       └── siledje-SIL-0001.env
├── siledje.db                      # Base SQLite (générée au 1er lancement, en développement)
├── README.md
│
├── scripts/                        # Outils réservés au vendeur/support
│   ├── generate_license_keypair.py # Crée la paire de clés de licence (UNE seule fois)
│   ├── generate_license_cli.py     # Génère la clé de licence d'un client
│   ├── make_client_env.py          # Génère le fichier de configuration d'un client
│   └── reset_password_cli.py
│
├── tools/                          # Scripts de maintenance et tests
│   ├── show_books.py
│   ├── fix_books_classes.py
│
├── assets/
│   ├── icons/                      # Icônes SVG
│   ├── images/                     # Images et logos (dont siledje.ico, icône de l'application)
│   └── styles/
│       ├── light.qss               # Thème clair
│       └── dark.qss                # Thème sombre
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Point d'entrée (python -m src.main) : configuration, licence, connexion
│   │
│   ├── Beans/                      # Modèles de données
│   │   ├── User.py
│   │   └── Role.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # Connexion SQLite (singleton)
│   │   ├── manager.py
│   │   ├── migrations/
│   │   │   ├── migration_manager.py
│   │   │   └── cloud_sync_migration.py
│   │   └── repositories/
│   │       ├── user_repository.py
│   │       ├── license_repository.py
│   │       ├── bug_report_repository.py
│   │       ├── catalog_repository.py
│   │       ├── sales_repository.py
│   │       ├── supplier_order_repository.py
│   │       ├── surveillance_repository.py
│   │       ├── school_repository.py
│   │       ├── sync_repository.py
│   │       ├── cloud_sync_repository.py
│   │       └── system_repository.py
│   │
│   ├── managers/                   # Logique métier
│   │   ├── __init__.py
│   │   ├── accueil/
│   │   │   └── accueil_manager.py
│   │   ├── auth/
│   │   │   └── auth_manager.py
│   │   ├── license/
│   │   │   └── license_manager.py
│   │   ├── admin/
│   │   │   └── admin_manager.py
│   │   ├── stock/
│   │   │   └── stock_manager.py
│   │   ├── sales/
│   │   │   └── sales_manager.py
│   │   ├── report/
│   │   │   └── report_manager.py
│   │   ├── barcode/
│   │   │   └── barcode_manager.py
│   │   ├── supplier/
│   │   │   └── supplier_manager.py
│   │   ├── file/
│   │   │   └── file_manager.py
│   │   ├── sync/
│   │   │   ├── __init__.py
│   │   │   ├── network_utils.py
│   │   │   ├── sync_manager.py
│   │   │   ├── cloud_data_sync_manager.py
│   │   │   └── supabase_rest_client.py
│   │   ├── security/
│   │   │   └── security_manager.py
│   │   ├── notifications/
│   │   │   └── notification_settings_manager.py
│   │   ├── database/
│   │   │   └── database_settings_manager.py
│   │   ├── help/
│   │   │   └── bug_report_manager.py
│   │   └── ai/
│   │       └── ai_manager.py
│   │
│   ├── ui/                         # Interface utilisateur
│   │   ├── windows/
│   │   │   ├── main_window.py
│   │   │   ├── login_window.py
│   │   │   └── license_window.py
│   │   ├── views/
│   │   │   ├── base/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_view.py
│   │   │   │   └── palette.py
│   │   │   ├── accueil/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── accueil_view.py
│   │   │   │   ├── accueil_table.py
│   │   │   │   └── accueil_chart.py
│   │   │   ├── stock/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stock_view.py
│   │   │   │   ├── stock_table.py
│   │   │   │   └── stock_form.py
│   │   │   ├── sales/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sales_view.py
│   │   │   │   ├── sales_table.py
│   │   │   │   └── sales_form.py
│   │   │   ├── admin/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin_view.py
│   │   │   │   ├── admin_table.py
│   │   │   │   └── admin_form.py
│   │   │   ├── security/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── security_view.py
│   │   │   │   ├── security_table.py
│   │   │   │   └── security_form.py
│   │   │   ├── report/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── report_view.py
│   │   │   │   └── report_table.py
│   │   │   ├── barcode/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── barcode_view.py
│   │   │   │   └── barcode_table.py
│   │   │   ├── supplier/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── supplier_view.py
│   │   │   │   ├── supplier_table.py
│   │   │   │   └── supplier_form.py
│   │   │   ├── file/
│   │   │   │   ├── __init__.py
│   │   │   │   └── file_view.py
│   │   │   ├── sync/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sync_view.py
│   │   │   │   ├── sync_status.py
│   │   │   │   └── sync_history.py
│   │   │   ├── notification_settings/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── notification_settings_view.py
│   │   │   │   └── notification_config.py
│   │   │   ├── database_settings/
│   │   │   │   ├── __init__.py
│   │   │   │   └── database_settings_view.py
│   │   │   ├── bug_report/
│   │   │   │   ├── __init__.py
│   │   │   │   └── bug_report_view.py
│   │   │   └── ai/
│   │   │       ├── __init__.py
│   │   │       ├── ai_view.py
│   │   │       └── ai_config.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── modal_form.py
│   │       ├── InfoDialog.py
│   │       ├── custom_button.py
│   │       └── theme_table.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── backup_service.py
│       ├── config.py               # Chemins : mode développement vs exécutable (voir Compilation)
│       ├── notifications.py
│       ├── theme_manager.py
│       ├── license_crypto.py       # Signature / vérification des licences (Ed25519)
│       ├── license_public_key.py   # Clé PUBLIQUE de vérification (non secrète, versionnée)
│       ├── helpers.py
│       └── compat.py
│
├── data/
│   ├── backups/                    # Sauvegardes locales
│   └── dummy_data/
│       └── data_home.py
│
├── build/                          # Généré par PyInstaller (NON versionné)
├── dist/                           # Généré par PyInstaller : dist/Siledje/Siledje.exe (NON versionné)
├── Output/                         # Généré par Inno Setup : le Setup.exe final (NON versionné)
│
└── docs/
    ├── docs_pdf/
    │   └── Siledje_bd_schema_source.pdf
    ├── architecture.md
    ├── user_manual.md
    └── dev_manual.md
```

---

## 🗄 Base de données

Le schéma complet (31 tables) est documenté dans `docs/docs_pdf/Siledje_bd_schema_source.pdf`. Chaque domaine métier possède son propre repository :

| Domaine | Tables | Repository |
|---------|--------|------------|
| Sécurité | `users`, `roles`, `audit_logs` | `user_repository.py` |
| Licence | `licenses` | `license_repository.py` |
| Produits et stock | `categories`, `suppliers`, `products`, `barcodes`, `product_components`, `stock_movements` | `catalog_repository.py` |
| Ventes | `clients`, `payment_methods`, `sales`, `sale_items`, `sale_payments`, `returns`, `return_items` | `sales_repository.py` |
| Manuels scolaires | `school_levels`, `school_systems`, `school_classes`, `books` | `school_repository.py` |
| Synchronisation | `sync_operations`, `sync_state` | `sync_repository.py`, `cloud_sync_repository.py` |
| Système | `sync_logs`, `settings` | `system_repository.py` |

---

## 🔐 Configuration et sécurité

### Principe : deux fichiers de configuration

| Fichier | Contenu | Où il se trouve | Versionné |
|---------|---------|-----------------|-----------|
| `app.env` | Variables **communes à tous les clients** (`SILEDJE_BUG_REPORT_URL`, `SILEDJE_BUG_REPORT_TOKEN`) | Embarqué dans l'exécutable (`_internal`) | Non (modèle : `app.env.example`) |
| `.env` du client | Variables **propres au client** : `SUPABASE_URL`, `SUPABASE_API_KEY`, `SILEDJE_CLOUD_SYNC_URL`, `SILEDJE_CLOUD_SYNC_TOKEN` | `%APPDATA%\Siledje\.env` (jamais embarqué) | Non |

Chaque client a **son propre projet Supabase** : les données de deux boutiques ne se mélangent jamais.

Le `.env` d'un client ressemble à ceci (il est généré par `scripts/make_client_env.py`) :

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_API_KEY=votre_cle_supabase
SILEDJE_CLOUD_SYNC_URL=https://xxxxxxxx.supabase.co/storage/v1/object/backups
SILEDJE_CLOUD_SYNC_TOKEN=votre_cle_supabase
```

### Premier lancement chez un client

Si `%APPDATA%\Siledje\.env` n'existe pas, Siledje affiche une fenêtre de configuration :

- **Choisir le fichier** : le client sélectionne le fichier remis par Siledje (par exemple `siledje-SIL-0001.env`). Il est vérifié (`SUPABASE_URL` et `SUPABASE_API_KEY` obligatoires), puis copié dans `%APPDATA%\Siledje\.env`.
- **Continuer sans cloud** : le logiciel fonctionne hors ligne (utile pour l'essai gratuit). Un `.env` vide est créé.
- **Quitter** : ferme l'application.

Pour redemander la configuration plus tard : lancer `Siledje.exe --reconfigure`.

En développement (non compilé), `app.env` et `.env` sont lus à la racine du projet.

### Licences : signature asymétrique Ed25519

| Élément | Où | Rôle |
|---------|----|------|
| **Clé publique** | `src/utils/license_public_key.py` (versionnée, embarquée) | Vérifie les licences dans l'application. Non secrète. |
| **Clé privée** | `%USERPROFILE%\.siledje_vendor\license_private.pem` (PC du vendeur uniquement) | Signe les licences. Jamais dans Git, jamais dans l'exécutable. |

Un client qui lit tous les fichiers de l'application **ne peut pas fabriquer de licence**.

Création de la paire de clés (**une seule fois**) :

```bash
pip install cryptography
python scripts/generate_license_keypair.py
```

> ⚠️ **Sauvegardez la clé privée** (clé USB, coffre-fort de mots de passe). Si elle est perdue, plus aucune licence ne peut être émise pour les applications déjà livrées : il faudrait recompiler avec une nouvelle clé publique. Régénérer la paire invalide toutes les licences existantes.

Génération de la licence d'un client :

```bash
python scripts/generate_license_cli.py "Nom Client" pro 3 365
python scripts/generate_license_cli.py "Nom Client" premium 5 --illimitee
```

La clé produite fait environ 230 caractères : à transmettre par copier-coller (WhatsApp, e-mail), le bouton « Coller » de l'écran d'activation retire les espaces.

### Compte administrateur par défaut

```
Nom d'utilisateur : admin
Mot de passe       : admin123
```
 À changer immédiatement après la première connexion, **avant de livrer chez un client**.

### Réinitialisation d'urgence

```bash
python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>
```

### ⚠️ Points de sécurité à connaître

| Sujet | Situation | Recommandation |
|-------|-----------|----------------|
| **Clé Supabase chez le client** | Le `.env` du client contient la clé `secret` de **son** projet : elle ignore le RLS et donne un accès complet à ce projet | Acceptable pour la démo et les premiers clients, car l'isolation par projet limite l'impact à ses propres données. À terme : clé `publishable` + connexion d'un compte dédié, comme l'application mobile |
| **Clé `service_role`** | Donne tous les droits sur le projet | Jamais dans une application ni un fichier remis à un client |
| **Jetons de `app.env`** | `app.env` est lisible dans `_internal` | N'y mettre aucun secret fort. Pour les rapports de bugs, utiliser un jeton à droits limités |
| **Fichiers du dossier `clients/`** | Contiennent les clés de chaque client | Jamais dans Git, jamais partagés, accès restreint à l'équipe |
| **Clé privée de licence** | Permet d'émettre des licences | PC du vendeur uniquement, sauvegardée, jamais dans le dépôt |
| **Inscription libre Supabase** | Activée par défaut | La désactiver sur chaque projet client (Authentication, *Allow new users to sign up*) |
| **Clés exposées** | Toute clé collée dans un chat, un e-mail ou un dépôt est compromise | La régénérer immédiatement dans Supabase et mettre à jour le fichier du client |

### Fichiers à ne jamais versionner

Voir « Fichiers à ignorer dans Git » plus bas. **`license_public_key.py` est, lui, versionné** (clé publique, non secrète) : sans lui, l'application ne démarre pas.

---

## Installation et Lancement

** Ce projet ne fonctionne qu'avec Python 3.12.**

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/siledje.git
cd siledje

# Créer l'environnement virtuel
py -3.12 -m venv venv

# Activer l'environnement
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Configurer le développement
copy app.env.example app.env     # puis remplir si nécessaire
copy .env.example .env           # puis renseigner un projet Supabase de test

# Première fois uniquement (vendeur) : créer la paire de clés de licence
python scripts/generate_license_keypair.py

# Lancer l'application
python -m src.main
```

** Ne pas faire :** `python src/main.py` (problèmes d'imports internes)

Si l'application s'arrête avec `Clé publique de licence absente`, exécuter `python scripts/generate_license_keypair.py` (ou récupérer `src/utils/license_public_key.py` du dépôt).

---

## 📦 Compilation et distribution (.exe)

Cette section explique comment transformer le projet en `Siledje.exe`, puis en un installeur `Setup.exe` à remettre aux clients. Deux étapes : **PyInstaller** génère l'exécutable, **Inno Setup** l'emballe dans un installeur.

> **À retenir :** on compile **une seule fois** pour **tous** les clients. Ce que l'on remet à un client : `Output\Siledje_Setup_x.y.z.exe`, **son fichier de configuration** `.env` et **sa clé de licence** (voir « Déployer chez un nouveau client »). Ne jamais envoyer `Siledje.exe` seul.

### Principe : deux dossiers distincts

Une application installée dans `C:\Program Files` n'a pas le droit d'y écrire. `src/utils/config.py` sépare donc deux emplacements :

| Variable | En développement | Dans l'exécutable | Contenu |
|----------|------------------|-------------------|---------|
| `resource_dir` | racine du projet | dossier interne de PyInstaller (`_internal`) | `assets/`, `config.json` d'origine, `app.env` (lecture seule) |
| `base_dir` | racine du projet | `%APPDATA%\Siledje` | `siledje.db`, `backups/`, `config.json` actif, `.env` du client (écriture) |

Règles à respecter dans le code :

- tout fichier **lu** et embarqué (icône, `.qss`, image) passe par `config.resource_dir` ou `config.get_asset_path(...)` ;
- tout fichier **écrit** (base de données, sauvegardes, exports) passe par `config.base_dir`, `config.db_path` ou `config.backup_dir` ;
- ne jamais construire un chemin avec `__file__` ou un chemin relatif en dur (`"data/..."`) dans les managers et repositories.

Pour repérer les chemins à corriger (PowerShell) :

```powershell
Get-ChildItem src -Recurse -Filter *.py | Select-String -Pattern "__file__","data/","backups"
```

### Prérequis

- Windows 10/11, Python 3.12 et le venv du projet activé
- PyInstaller : `pip install pyinstaller`
- `cryptography` (licences) : `pip install cryptography`
- Inno Setup (voir « Installer Inno Setup » ci-dessous)
- Une icône `assets/images/siledje.ico` (multi-tailles : 256, 128, 64, 48, 32, 16 px)
- Un fichier `app.env` à la racine (copie de `app.env.example`) : il est embarqué dans l'exécutable
- La paire de clés de licence créée (`src/utils/license_public_key.py` non vide)

### Étape 1 — Point d'entrée `run.py`

PyInstaller n'aime pas `python -m src.main`. Un fichier `run.py` à la racine suffit :

```python
from src.main import main

if __name__ == "__main__":
    main()
```

### Étape 2 — Générer l'exécutable avec `Siledje.spec`

La compilation passe maintenant par le fichier `Siledje.spec` (versionné), à la racine du projet. **Le `.env` n'y est plus embarqué** : seul `app.env` (variables communes) l'est.

```python
# -*- mode: python ; coding: utf-8 -*-
# Compilation : pyinstaller Siledje.spec --clean --noconfirm
#
# app.env  : commun a tous les clients (rapports de bugs), embarque.
# .env     : NON embarque. Chaque client a le sien dans %APPDATA%\Siledje\.env
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets'), ('config.json', '.'), ('app.env', '.')]
binaries = []
hiddenimports = ['bcrypt', 'dateutil']
tmp_ret = collect_all('barcode')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Siledje',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/images/siledje.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Siledje',
)
```

Depuis la racine du projet, venv activé :

```powershell
pyinstaller Siledje.spec --clean --noconfirm
```

> **Important :** quand on compile depuis un `.spec`, les options `--add-data`, `--icon`, `--hidden-import`, etc. de la ligne de commande sont **ignorées**. Toute modification (modules, fichiers embarqués, icône) se fait dans `Siledje.spec`.

| Élément du spec | Rôle |
|-----------------|------|
| `datas` | Fichiers embarqués : `assets`, `config.json`, `app.env`. **Pas de `.env`.** |
| `hiddenimports` | Modules que PyInstaller ne détecte pas seul (`bcrypt`, `dateutil`). Ajouter `cryptography` si `ModuleNotFoundError` |
| `collect_all('barcode')` | Inclut tout le paquet `python-barcode` |
| `console=False` | Pas de fenêtre noire au lancement (équivalent de `--noconsole`) |
| `exclude_binaries=True` + `COLLECT` | Mode `--onedir` : un dossier au lieu d'un fichier unique, démarrage plus rapide, moins de faux positifs antivirus |
| `icon` | Icône du fichier `.exe` |

Durée : 1 à 10 minutes selon la machine (l'analyse de PySide6 est longue). **Ne pas interrompre** (pas de Ctrl+C, pas de clic dans le terminal) : la fin est signalée par `Build complete!`. Résultat : `dist\Siledje\` contenant `Siledje.exe` **et** le dossier `_internal`.

Avec `--onedir`, `Siledje.exe` n'est qu'un petit lanceur (environ 5,5 Mo). Python, PySide6, `python312.dll`, les assets et `app.env` sont dans `_internal`. L'exe et `_internal` doivent toujours rester côte à côte.

Teste toujours cet exécutable depuis `dist\Siledje` avant de créer l'installeur :

1. Supprimer `%APPDATA%\Siledje\.env` : la fenêtre de configuration doit apparaître.
2. Choisir un fichier généré par `make_client_env.py`, activer une licence, se connecter, faire une vente, vérifier la sauvegarde cloud.
3. Tester aussi « Continuer sans cloud ».

### Icône de la fenêtre et de la barre des tâches

L'icône `icon=[...]` du spec ne règle que l'icône du fichier `.exe`. L'icône de la fenêtre et de la barre des tâches est définie dans `src/main.py` (identifiant d'application Windows + `setWindowIcon`). Si une fenêtre garde une ancienne icône, chercher les autres appels :

```powershell
Get-ChildItem src -Recurse -Filter *.py | Select-String "setWindowIcon"
```

### Étape 3 — Créer l'installeur avec Inno Setup

L'installeur est **identique pour tous les clients** : il n'embarque aucune configuration propre à un client.

#### 3.1 Installer Inno Setup (une seule fois, sur le PC de développement)

1. Télécharger Inno Setup sur https://jrsoftware.org/isdl.php (version 6.x ou 7.x ; la version 7 64 bits est recommandée).
2. Lancer l'installeur et accepter les options par défaut.
3. Alternative en ligne de commande : `winget install --id JRSoftware.InnoSetup -e -s winget -i`

> **Licence :** Inno Setup est gratuit, mais l'éditeur demande l'achat d'une licence pour un usage commercial (licence perpétuelle, paiement unique). Le bandeau « Using Inno Setup commercially? » dans l'application le rappelle. Siledje étant vendu, prévoir cette licence.

#### 3.2 Créer le script `installer.iss`

Créer le fichier `installer.iss` **à la racine du projet** (au même niveau que `run.py` et le dossier `dist`), avec ce contenu :

```ini
[Setup]
AppName=Siledje
AppVersion=1.0.0
AppPublisher=Siledje
DefaultDirName={autopf}\Siledje
DefaultGroupName=Siledje
OutputBaseFilename=Siledje_Setup_1.0.0
SetupIconFile=assets\images\siledje.ico
UninstallDisplayIcon={app}\Siledje.exe
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "dist\Siledje\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Siledje"; Filename: "{app}\Siledje.exe"
Name: "{autodesktop}\Siledje"; Filename: "{app}\Siledje.exe"

[Run]
Filename: "{app}\Siledje.exe"; Description: "Lancer Siledje"; Flags: nowait postinstall
```

La ligne `Source: "dist\Siledje\*"` emballe tout le dossier généré par PyInstaller (l'exe **et** `_internal`). Le chemin est relatif à l'emplacement de `installer.iss`.

#### 3.3 Compiler l'installeur

1. Ouvrir Inno Setup. Dans la fenêtre « Welcome », choisir **Open an existing script file** puis **More files...** (ou **Cancel**, puis **File > Open** / `Ctrl+O`) et sélectionner `installer.iss`.
2. Lancer la compilation avec **Build > Compile** ou `Ctrl+F9`.
3. Attendre la fin sans toucher à rien : la dernière ligne de la zone de messages doit indiquer `Successful compile`.
4. Récupérer l'installeur dans `Output\Siledje_Setup_1.0.0.exe` (environ 48 Mo à cause de PySide6).

> **Ne pas utiliser le bouton Run (▶ / `F9`).** Il tente de lancer l'installeur en mode debug et affiche `Cannot debug. Debugger version ($00000000) does not match Setup version`, puis `Setup exit code: 2`. Ce n'est pas une erreur de compilation : l'installeur dans `Output` est correct. Pour le tester, double-cliquer simplement sur le `.exe` généré.

#### 3.4 Tester l'installeur

1. Double-cliquer sur `Output\Siledje_Setup_1.0.0.exe` et installer l'application.
2. Lancer Siledje depuis le raccourci du bureau.
3. La fenêtre de configuration cloud s'affiche (si aucun `.env` dans `%APPDATA%\Siledje`), puis l'écran d'activation de licence : l'installeur fonctionne.

La base de données, les sauvegardes et le `.env` du client restent dans `%APPDATA%\Siledje` : ils survivent aux mises à jour et à la désinstallation.

---

## 🚀 Déployer chez un nouveau client (sans recompiler)

Un client = **un e-mail dédié** + **un projet Supabase dédié** + **un fichier de configuration** + **une clé de licence**. Aucune recompilation n'est nécessaire.

### Étapes (vendeur)

1. **Créer le client dans le registre** (fiche client, identifiant `SIL-000X`, e-mail dédié `client-x@siledje.com`).
2. **Créer son projet Supabase** (nom `siledje-client-x`), exécuter les scripts SQL (tables, RLS), désactiver l'inscription libre, noter l'URL et la clé.
3. **Générer le fichier de configuration** :

   ```bash
   python scripts/make_client_env.py SIL-0001 https://xxxxxxxx.supabase.co sb_secret_xxx
   ```

   Résultat : `clients/SIL-0001/siledje-SIL-0001.env` (option `--force` pour écraser un fichier existant).
4. **Générer la clé de licence** :

   ```bash
   python scripts/generate_license_cli.py "Librairie Exemple" pro 3 365
   ```
5. **Remettre au client** les trois éléments : l'installeur `Siledje_Setup_x.y.z.exe`, le fichier `siledje-SIL-0001.env` et la clé de licence.
6. **Mettre à jour le registre** : version livrée, date, fin de licence, statut.

### Chez le client

1. Installer avec `Siledje_Setup_x.y.z.exe`.
2. Au premier lancement, cliquer sur **Choisir le fichier** et sélectionner `siledje-SIL-0001.env`.
3. Coller la clé de licence dans l'écran d'activation (fonctionne hors ligne).
4. Se connecter avec le compte administrateur et **changer le mot de passe par défaut**.

### Ce qu'il faut remettre au client

| Élément | Fichier | Remarque |
|---------|---------|----------|
| **Installeur** | `Output\Siledje_Setup_x.y.z.exe` | Identique pour tous les clients ✅ |
| **Configuration** | `clients\SIL-000X\siledje-SIL-000X.env` | Propre au client, à transmettre de façon privée |
| **Licence** | Clé générée par `generate_license_cli.py` | Propre au client |
| Archive ZIP | Le dossier **complet** `dist\Siledje` (exe + `_internal`) zippé | Dépannage uniquement |
| `Siledje.exe` seul | — | ❌ Ne fonctionne jamais |

Si `Siledje.exe` est copié sans `_internal`, Windows affiche : `Failed to load Python DLL ... \_internal\python312.dll. LoadLibrary: Le module spécifié est introuvable.`

Ne pas commiter le Setup.exe dans Git (trop volumineux) : le transmettre par WhatsApp, Drive, WeTransfer, etc. Avant d'envoyer un ZIP, l'extraire dans un autre dossier et vérifier qu'il se lance.

### Publier une nouvelle version

1. Mettre à jour la version dans `config.json` et dans `QCoreApplication.setApplicationVersion(...)` (`src/main.py`).
2. Mettre à jour `AppVersion` et `OutputBaseFilename` dans `installer.iss`.
3. Recompiler avec PyInstaller : `pyinstaller Siledje.spec --clean --noconfirm`, tester `dist\Siledje\Siledje.exe`.
4. Recompiler l'installeur avec `Ctrl+F9` (étape 3.3) : l'installeur n'est **pas** mis à jour automatiquement après un nouveau build PyInstaller.
5. Tester l'installeur, puis l'envoyer aux clients. Leur `.env` et leur base dans `%APPDATA%\Siledje` sont conservés : ils n'ont pas à reconfigurer.

### Résolution de problèmes

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| `Aborted by user request` | Compilation interrompue | Relancer sans toucher au terminal |
| `Icon input file ... not found` | `siledje.ico` absent | Placer le fichier dans `assets\images\` ou retirer `icon` du spec (et `SetupIconFile` dans `installer.iss`) |
| `app.env` introuvable à la compilation | `app.env` absent de la racine | Copier `app.env.example` en `app.env` |
| L'exe se ferme sans message | Erreur au démarrage masquée par `console=False` | Passer `console=True` dans `Siledje.spec`, recompiler et lire l'erreur |
| `ModuleNotFoundError` | Module non détecté | Ajouter le module à `hiddenimports` dans `Siledje.spec` (pour `cryptography` : `'cryptography'`) |
| `Clé publique de licence absente` | `license_public_key.py` vide | `python scripts/generate_license_keypair.py` (ou récupérer le fichier du dépôt), puis recompiler |
| `Clé privée introuvable` | Génération de licence sur un PC sans la clé privée | Utiliser le PC du vendeur ou restaurer la sauvegarde de `license_private.pem` |
| « Clé invalide ou expirée » après changement de clés | Licence émise avec une ancienne paire de clés | Régénérer la licence avec `generate_license_cli.py` |
| « Fichier invalide » à la configuration | Le fichier ne contient pas `SUPABASE_URL` et `SUPABASE_API_KEY` | Vérifier que c'est bien le fichier `.env` du client (généré par `make_client_env.py`) |
| Mauvaise configuration chez un client | Mauvais fichier choisi au premier lancement | `Siledje.exe --reconfigure` et choisir le bon fichier |
| Données d'un autre client visibles | Mauvais `.env` | Comparer avec la fiche client, relancer avec `--reconfigure` |
| `FileNotFoundError` / base introuvable | Chemin en dur, non converti | Utiliser `config.resource_dir` (lecture) ou `config.base_dir` (écriture) |
| Erreur d'écriture / `PermissionError` | Écriture dans `Program Files` | Écrire dans `config.base_dir` (`%APPDATA%\Siledje`) |
| Ancienne icône dans l'Explorateur | Cache d'icônes de Windows | Vider le cache (voir ci-dessous) |
| Avertissement SmartScreen à l'installation | Exécutable non signé | Normal au début ; cliquer sur « Informations complémentaires » puis « Exécuter quand même » ; un certificat de signature de code le supprime |
| `Hidden import "_cffi_backend" not found` | Avertissement sans conséquence | À ignorer |
| `Failed to load Python DLL ... python312.dll` | `Siledje.exe` copié sans le dossier `_internal` | Envoyer l'installeur, ou zipper tout `dist\Siledje` |
| `Cannot debug. Debugger version ... does not match Setup version` | Bouton Run (`F9`) utilisé au lieu de la compilation | Ignorer ; compiler avec `Ctrl+F9` et lancer le `.exe` depuis `Output` |
| Inno Setup : `Unknown file ... French.isl` | Fichier de langue absent | Supprimer la section `[Languages]` du script |
| Inno Setup : `Icon file not found` | `siledje.ico` absent | Placer le fichier dans `assets\images\` ou retirer `SetupIconFile` |
| Inno Setup : `No files found matching dist\Siledje\*` | `installer.iss` hors de la racine du projet | Le placer au même niveau que le dossier `dist` |

Vider le cache d'icônes de Windows :

```powershell
Stop-Process -Name explorer -Force
Remove-Item "$env:LOCALAPPDATA\IconCache.db" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*" -Force -ErrorAction SilentlyContinue
Start-Process explorer
```

### Fichiers à ignorer dans Git

Ajouter au `.gitignore` (`installer.iss`, `Siledje.spec` et `src/utils/license_public_key.py`, eux, **doivent** être versionnés) :

```
build/
dist/
Output/
.env
app.env
clients/
*.db
```

---

##  Licences

| Composant | Licence |
|-----------|---------|
| PySide6 | LGPL v3.0 |
| Python | PSF License |
| psutil | BSD License |
| python-barcode | MIT License |
| Pillow | HPND License |
| python-dateutil | BSD License |
| bcrypt | Apache 2.0 |
| cryptography | Apache 2.0 / BSD (double licence) |
| PyInstaller | GPL v2 avec exception (les exécutables générés ne sont pas soumis à la GPL) |
| Inno Setup | Licence Inno Setup (gratuit ; licence commerciale à acheter en cas d'usage commercial) |

Le projet **SILEDJE** est distribué sous licence **MIT**. Voir `LICENSE`.

---

##  Chantiers en cours

- [ ] Numérotation/affichage des ID produits
- [ ] Formulaire de création produit : ordre des champs à revoir
- [ ] Extension des adaptateurs de synchronisation à `barcodes` et `product_components`
- [ ] Activation du RLS + policies Supabase pour l'application mobile
- [ ] Bouton de purge de l'historique de synchronisation
- [ ] Desktop : remplacer la clé Supabase `secret` du client par la clé `publishable` + un compte dédié
- [ ] Mobile : écran de premier lancement avec QR de configuration (URL + clé `anon`), pour supprimer la recompilation côté Android
- [ ] Aligner les noms des plans entre le logiciel (Starter / Pro / Premium) et le site (Starter / Scale / Enterprise)
- [ ] Écran d'activation : format de clé affiché à adapter aux clés Ed25519 (plus longues)
- [ ] Signature de code de l'exécutable (suppression de l'avertissement SmartScreen)
- [ ] Achat de la licence commerciale Inno Setup
- [x] Passage de la signature de licence HMAC à une signature asymétrique (Ed25519)
- [x] Configuration par client sans recompilation (`app.env` embarqué + `.env` du client dans `%APPDATA%`)

---

## Contribution

1. Forkez le dépôt
2. `git checkout -b feature/nom-de-votre-fonctionnalite`
3. `git commit -m "feat: Ajout de la fonctionnalité X"`
4. `git push origin feature/nom-de-votre-fonctionnalite`
5. Ouvrez une Pull Request

---

## Contact

**Support technique :** support@siledje.cm
**Téléphone :** +237 694 122 436
**Site web :** www.siledje.cm

---

*© 2025 Siledje – Tous droits réservés*
