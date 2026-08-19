# Architecture — Siledje

Ce document explique **comment le projet est organisé** et **pourquoi**, pour
qu'un développeur qui découvre le code puisse s'y retrouver rapidement.

---

## 1. Vue d'ensemble en une phrase

Siledje est une application desktop **PySide6** (Qt pour Python), avec une
base **SQLite locale** comme source de vérité, et une **synchronisation
optionnelle vers Supabase** (catalogue + historique de ventes) pensée pour
cohabiter avec une future application mobile.

---

## 2. Les trois couches (le motif répété partout)

Chaque domaine métier (stock, ventes, fournisseurs, sécurité, sync...) suit
**le même motif à trois couches** :

```
View  (PySide6, src/ui/views/<domaine>/)
  ↕ signaux Qt (Signal / Slot)
Manager (src/managers/<domaine>/)
  ↕ appels de méthodes Python
Repository (src/database/repositories/<domaine>_repository.py)
  ↕ requêtes SQL
Base SQLite (siledje.db)
```

### La View (`src/ui/views/.../xxx_view.py`)
- Contient **uniquement** l'affichage et les widgets Qt (`QWidget`,
  `QTableWidget`, `QComboBox`, etc.).
- Émet des **signaux** (`Signal`) quand l'utilisateur agit (clic sur un
  bouton, changement de date...). Exemple, dans `ReportView` :
  ```python
  period_changed = Signal(str)
  export_csv_requested = Signal()
  ```
- N'accède **jamais** directement à la base de données ni aux repositories.
- Expose des méthodes publiques du type `update_xxx(...)` que le Manager
  appelle pour rafraîchir l'affichage.

### Le Manager (`src/managers/.../xxx_manager.py`)
- Hérite de `QObject`, fait le lien entre la View et le Repository.
- Se connecte aux signaux de la View (`_connect_view_signals`) et réagit
  avec des méthodes marquées `@Slot`.
- Contient la logique métier (calculs, règles, orchestration), mais **pas**
  de SQL brut — ça, c'est le rôle du Repository.
- Crée sa View à la demande (`get_ui()`), en lazy loading, pour ne pas
  construire tous les écrans au démarrage.

### Le Repository (`src/database/repositories/xxx_repository.py`)
- Le **seul** endroit qui écrit du SQL pour un domaine donné.
- Expose des méthodes claires (`get_sales_between`, `create_sale`,
  `count_sales`...) qui retournent des `dict` ou des listes de `dict`
  (jamais des objets `sqlite3.Row` bruts exposés en dehors du repository).
- Peut créer son propre schéma via `_ensure_schema()` (idempotent,
  `CREATE TABLE IF NOT EXISTS`) — utile pour que l'app fonctionne dès le
  premier lancement sans script d'installation séparé.

**Pourquoi ce découpage ?** Pour qu'on puisse remplacer l'UI (PySide6) ou
la base (SQLite) sans toucher à la logique métier, et pour que chaque
fichier reste petit et testable indépendamment.

---

## 3. Fichiers de style (`assets/styles/*.qss`)

Le QSS est l'équivalent CSS pour Qt. Deux fichiers globaux :

- `assets/styles/light.qss` — thème clair
- `assets/styles/dark.qss` (`dark_style.qss` dans les logs) — thème sombre

Ils sont chargés par `src/utils/theme_manager.py` (`ThemeManager`), qui :
1. Lit le thème actif depuis `config.json` (clé `ui.theme`) ou les
   `QSettings`.
2. Charge le fichier `.qss` correspondant et l'applique globalement à
   l'application (`app.setStyleSheet(...)`).
3. Propage le changement de thème à chaque View ouverte via leur méthode
   `set_theme(is_dark: bool)`.

**Règle du projet** (voir `report_view.py` en commentaire) : *"pas de
styles locaux hardcodés"* — les couleurs viennent de `Palette`
(`src/ui/views/base/palette.py`), pas de couleurs écrites en dur dans
chaque View. `Palette.get_theme_colors(is_dark)` retourne un dict de
couleurs cohérent pour tout le projet. Un développeur qui ajoute un écran
doit utiliser `Palette`, jamais un code couleur `#xxxxxx` en dur dans une
View, pour que le thème clair/sombre reste cohérent partout.

---

## 4. Synchronisation cloud (Supabase)

Deux mécanismes **distincts**, à ne pas confondre :

### a) Sauvegarde complète (`sync_manager.py` → `CloudSyncClient`)
Copie le fichier `.db` entier et l'envoie vers Supabase Storage
(`SILEDJE_CLOUD_SYNC_URL`). C'est un filet de sécurité (reprise après
sinistre), pas une synchro fine.

### b) Synchronisation de données (`cloud_data_sync_manager.py`)
Synchronise **enregistrement par enregistrement** via l'API REST de
Supabase (`supabase_rest_client.py`, utilise `SUPABASE_URL` +
`SUPABASE_API_KEY`). Deux règles de fusion, selon la table :

| Type de table | Règle | Tables concernées |
|---|---|---|
| **LWW** (Last Write Wins) | La ligne avec `updated_at` le plus récent gagne, poussée et tirée dans les deux sens | `categories`, `suppliers`, `products` |
| **Append-only** | Chaque événement créé est rejoué sur l'autre appareil, jamais écrasé | `stock_movements` |
| **Push-only** | Poussé une seule fois vers Supabase, jamais retiré (`pull`) — le mobile consulte, ne crée jamais | `sales`, `sale_items`, `sale_payments` |

Chaque table synchronisée a une colonne `sync_uuid` (UUID stable,
identique en local et sur Supabase) qui sert de clé de correspondance —
les `id` SQLite locaux (`AUTOINCREMENT`) ne sont **jamais** envoyés au
cloud, car ils n'ont aucun sens en dehors de cette base locale précise.

`CloudSyncRepository` est **générique** : il ne connaît pas la liste des
tables à synchroniser (il prend un nom de table en paramètre). C'est
`CloudDataSyncManager` qui décide *quelles* tables synchroniser et
*comment* (adaptateurs `CategoryAdapter`, `SupplierAdapter`,
`ProductAdapter` pour le LWW, méthodes `_push_sales()` /
`_push_sale_items()` / `_push_sale_payments()` pour le push-only).

---

## 5. Migrations (`src/database/migrations/`)

Le schéma SQLite évolue au fil du temps sans réinstallation complète,
via un mini-système de migrations :

- **`migration_manager.py`** : le chef d'orchestre. Il maintient une table
  `migrations` (fichier + date d'application), scanne le dossier à chaque
  démarrage, et exécute uniquement les fichiers **jamais encore
  appliqués** (par nom de fichier exact).
- **Un fichier de migration** = un module Python exposant deux fonctions :
  ```python
  def upgrade(connection):  # obligatoire
      ...
  def downgrade(connection):  # optionnel, best-effort
      ...
  ```
- Convention de nommage : `NNN_description.py` (`001_add_sales_sync_columns.py`,
  `002_...`), **sauf** `cloud_sync_migration.py`, plus ancien, qui a gardé
  un nom descriptif sans numéro — laissé tel quel pour ne pas perturber
  la table `migrations` qui l'a déjà enregistré sous ce nom.
- **Chaque migration doit être idempotente** : vérifier avant d'agir
  (`PRAGMA table_info`, `IF NOT EXISTS`...), car elle peut en théorie être
  relancée sans dégât.
- **Limite SQLite à connaître** : `ALTER TABLE ... ADD COLUMN xxx UNIQUE`
  n'est **pas supporté**. Il faut ajouter la colonne sans contrainte,
  puis créer un `CREATE UNIQUE INDEX` séparé (voir
  `001_add_sales_sync_columns.py` pour un exemple concret).

Voir `docs/dev_manual.md` pour la marche à suivre pas à pas.

---

## 6. Système de licence

- `SILEDJE_LICENSE_SECRET` (dans `.env`) est la clé secrète utilisée pour
  signer/vérifier les licences en **HMAC-SHA256** (`src/utils/license_crypto.py`).
- `license_manager.py` gère l'activation côté application (lecture, état
  courant, plan actif : Starter / Pro / Premium).
- `license_validator.py` vérifie la signature d'une clé fournie contre
  `SILEDJE_LICENSE_SECRET`, hors-ligne (pas d'appel réseau nécessaire pour
  valider une licence déjà émise).
- `scripts/generate_license_cli.py` est l'outil réservé au vendeur/support
  pour **émettre** de nouvelles clés de licence signées — ce script doit
  tourner avec le **même** `SILEDJE_LICENSE_SECRET` que celui utilisé en
  production, sinon les clés générées seront rejetées par les instances
  clientes.

**Point de sécurité important** : `SILEDJE_LICENSE_SECRET` ne doit jamais
être commité, ni partagé en dehors de l'équipe qui émet les licences. Une
fuite de ce secret permettrait à n'importe qui de générer des licences
valides.

---

## 7. Où regarder en premier selon ce qu'on veut faire

| Je veux... | Je regarde... |
|---|---|
| Ajouter un nouvel écran | `src/ui/views/base/base_view.py` (classe de base commune), un module existant comme `report/` en modèle |
| Ajouter une table / requête SQL | Le repository du domaine concerné, ou en créer un nouveau sur le modèle de `sales_repository.py` |
| Faire évoluer le schéma existant | `src/database/migrations/`, voir `docs/dev_manual.md` |
| Comprendre la synchro cloud | `cloud_data_sync_manager.py` (contient un long commentaire d'en-tête qui documente les règles de fusion) |
| Générer une clé de licence | `scripts/generate_license_cli.py` |
| Changer le thème / une couleur | `assets/styles/*.qss`, `src/ui/views/base/palette.py`, jamais de couleur en dur ailleurs |