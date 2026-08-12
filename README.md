# 📚 SILEDJE — Gestion Librairie & Papeterie

Un système de gestion intuitif et complet pour les librairies et papeteries, conçu pour simplifier la gestion quotidienne des stocks, des ventes, des clients et des fournisseurs. Développé avec une interface utilisateur moderne et réactive grâce à **PySide6**.

---

##  Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Architecture](#-architecture-du-projet)
- [Base de données](#-base-de-données)
- [Sécurité](#-sécurité)
- [Installation](#-installation-et-lancement)
- [Licences](#-licences)
- [Chantiers en cours](#-chantiers-en-cours)

---

##  Fonctionnalités

| Module | Description |
|--------|-------------|
| **Authentification** | Comptes utilisateurs avec mots de passe hachés (bcrypt), rôles et permissions (admin / gérant / employé), verrouillage après tentatives échouées, journal d'audit complet |
| **Gestion des Utilisateurs** | Création, modification, désactivation de comptes et réinitialisation de mot de passe par un administrateur |
| **Système de Licence** | Activation hors-ligne par clé signée cryptographiquement (HMAC-SHA256), gestion des plans (Starter / Pro / Premium) |
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

---

## 🛠 Technologies

| Technologie | Utilisation |
|-------------|-------------|
| **Python 3.12** | Langage principal |
| **PySide6** | Interface graphique (Qt pour Python) |
| **SQLite** | Base de données locale |
| **Supabase** | Synchronisation de données + stockage des sauvegardes (API REST) |
| **bcrypt** | Hachage des mots de passe |
| **python-dotenv** | Gestion des secrets via `.env` |
| **psutil** | Statistiques système en barre de statut |
| **python-barcode + Pillow** | Génération des codes-barres |
| **python-dateutil** | Comparaison fiable des horodatages entre appareils |
| **urllib / socket** | Bibliothèque standard — aucune dépendance HTTP supplémentaire |

---

##  Architecture du Projet

```
SILEDJE/
├── config.json                     # Configuration centralisée
├── requirements.txt                # Dépendances Python
├── .env                            # Secrets locaux (NON versionné)
├── .env.example                    # Modèle de .env (versionné, sans valeurs)
├── siledje.db                    # Base SQLite (générée au 1er lancement)
├── README.md
│
├── scripts/                        # Outils réservés au vendeur/support
│   ├── generate_license_cli.py
│   ├── reset_password_cli.py
│ 
│
├── tools/                          # Scripts de maintenance et tests
│   ├── show_books.py
│   ├── fix_books_classes.py
│
├── assets/
│   ├── icons/                      # Icônes SVG
│   ├── images/                     # Images et logos
│   └── styles/
│       ├── light.qss               # Thème clair
│       └── dark.qss                # Thème sombre
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Point d'entrée (python -m src.main)
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
|   |       ├── catalog_repository.py
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
│   │   │   ├── license_manager.py
│   │   │   └── license_validator.py
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
|       |── backup_service.py
│       ├── config.py
│       ├── notifications.py
│       ├── theme_manager.py
│       ├── license_crypto.py
│       ├── helpers.py
│       └── compat.py
│
├── data/
│   ├── backups/                    # Sauvegardes locales
│   └── dummy_data/
│       └── data_home.py
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

## Sécurité

### Fichier `.env` (obligatoire, jamais commité)

```bash
# Génération de la clé secrète
python -c "import secrets; print(secrets.token_hex(32))"
```

```
SILEDJE_LICENSE_SECRET=votre_cle_generee_ici
```

 **`.env` ne doit jamais être suivi par Git.**

### Variables optionnelles — Synchronisation cloud

```
SILEDJE_CLOUD_SYNC_URL=https://votre-projet.supabase.co/storage/v1/object/backups
SILEDJE_CLOUD_SYNC_TOKEN=votre_cle_secrete_supabase
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_API_KEY=votre_cle_secrete_supabase
```

### Compte administrateur par défaut

```
Nom d'utilisateur : admin
Mot de passe       : admin123
```
 À changer immédiatement après la première connexion.

### Réinitialisation d'urgence

```bash
python scripts/reset_password_cli.py <username> <nouveau_mot_de_passe>
```

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

# Configurer .env (voir ci-dessus)

# Lancer l'application
python -m src.main
```

** Ne pas faire :** `python src/main.py` (problèmes d'imports internes)

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

Le projet **SILEDJE** est distribué sous licence **MIT**. Voir `LICENSE`.

---

##  Chantiers en cours

- [ ] Numérotation/affichage des ID produits
- [ ] Formulaire de création produit : ordre des champs à revoir
- [ ] Extension des adaptateurs de synchronisation à `barcodes` et `product_components`
- [ ] Activation du RLS + policies Supabase pour l'application mobile
- [ ] Bouton de purge de l'historique de synchronisation

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