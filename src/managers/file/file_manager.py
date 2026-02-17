"""
Gestionnaire des opérations sur les fichiers.
Import/Export CSV réels + Sauvegarde/Restauration base de données.
Emplacement: src/managers/file/file_manager.py
"""

import csv
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox


class FileManager(QObject):
    """Gère toutes les opérations fichier de l'application."""

    version = "1.0.0"

    # Colonnes CSV attendues pour l'import stock
    STOCK_CSV_COLUMNS = ['nom', 'description', 'prix', 'quantite', 'categorie']
    STOCK_CSV_COLUMNS_FR = ['Nom', 'Description', 'Prix', 'Quantité', 'Catégorie']

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.view = None

        # Récupérer le DatabaseManager du parent
        if hasattr(parent, 'db'):
            self.db = parent.db
        else:
            from src.database.manager import DatabaseManager
            self.db = DatabaseManager()

        # Chemin de la base de données
        if hasattr(self.db, 'db') and hasattr(self.db.db, 'db_name'):
            self.db_path = Path(self.db.db.db_name)
        else:
            self.db_path = Path("librairie.db")

        # Dossier des sauvegardes
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        print(f"[FileManager v{self.version}] Initialisé - BDD: {self.db_path}")

    def get_ui(self):
        """Retourne la vue (lazy loading)."""
        if self.view is None:
            from src.ui.views.file_view import FileView
            self.view = FileView(self.parent_window)
            self._connect_signals()
            self._refresh_backups_list()
            print("[FileManager] Vue créée")
        return self.view

    def _connect_signals(self):
        self.view.import_csv_requested.connect(self.import_stock_csv)
        self.view.export_csv_requested.connect(self.export_stock_csv)
        self.view.create_backup_requested.connect(self.create_backup)
        self.view.restore_backup_requested.connect(self.restore_backup)
        self.view.delete_backup_requested.connect(self.delete_backup)
        self.view.refresh_backups_requested.connect(self._refresh_backups_list)

    def _refresh_backups_list(self):
        """Rafraîchit la liste des sauvegardes dans la vue."""
        if not self.view:
            return
        backups = self._get_backups_list()
        self.view.update_backups_list(backups)

    def _get_backups_list(self) -> list:
        """Retourne la liste des sauvegardes disponibles."""
        backups = []
        for f in sorted(self.backup_dir.glob("*.db"), reverse=True):
            size_kb = f.stat().st_size / 1024
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            backups.append({
                'name': f.name,
                'path': str(f),
                'size': f"{size_kb:.1f} KB",
                'date': mtime.strftime("%d/%m/%Y %H:%M:%S"),
            })
        return backups

    # ========== IMPORT CSV ==========

    @Slot(str)
    def import_stock_csv(self, file_path: str):
        """Importe les produits depuis un fichier CSV."""
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"Le fichier n'existe pas:\n{file_path}")
                return

            imported = 0
            errors = []

            with open(path, 'r', encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)

                # Vérifier les colonnes
                if not reader.fieldnames:
                    QMessageBox.warning(self.view, "CSV vide", "Le fichier CSV est vide ou mal formaté.")
                    return

                headers_lower = [h.strip().lower() for h in reader.fieldnames]

                # Mapper les colonnes (accepte français et anglais)
                col_map = {}
                for col in self.STOCK_CSV_COLUMNS:
                    for h in reader.fieldnames:
                        if h.strip().lower() in (col, col.replace('e', 'é'),
                                                  col.capitalize(),
                                                  col.replace('quantite', 'quantité'),
                                                  col.replace('categorie', 'catégorie')):
                            col_map[col] = h.strip()
                            break

                # Colonnes obligatoires
                required = ['nom', 'prix', 'quantite']
                missing = [c for c in required if c not in col_map]
                if missing:
                    QMessageBox.warning(
                        self.view, "Colonnes manquantes",
                        f"Colonnes obligatoires manquantes:\n{', '.join(missing)}\n\n"
                        f"Colonnes trouvées:\n{', '.join(reader.fieldnames)}\n\n"
                        f"Colonnes attendues:\n{', '.join(self.STOCK_CSV_COLUMNS_FR)}"
                    )
                    return

                cursor = self.db.db.get_cursor()

                for row_num, row in enumerate(reader, start=2):
                    try:
                        nom = row.get(col_map.get('nom', ''), '').strip()
                        prix_str = row.get(col_map.get('prix', ''), '0').strip().replace(',', '.')
                        qty_str = row.get(col_map.get('quantite', ''), '0').strip()
                        description = row.get(col_map.get('description', ''), '').strip()
                        categorie = row.get(col_map.get('categorie', ''), 'Général').strip()

                        if not nom:
                            errors.append(f"Ligne {row_num}: nom manquant")
                            continue

                        try:
                            prix = float(prix_str)
                        except ValueError:
                            errors.append(f"Ligne {row_num}: prix invalide '{prix_str}'")
                            continue

                        try:
                            quantite = int(qty_str)
                        except ValueError:
                            errors.append(f"Ligne {row_num}: quantité invalide '{qty_str}'")
                            continue

                        # Insérer ou mettre à jour
                        cursor.execute(
                            "SELECT id FROM products WHERE name = ?", (nom,)
                        )
                        existing = cursor.fetchone()

                        if existing:
                            cursor.execute(
                                "UPDATE products SET description=?, price=?, quantity=?, category=? WHERE name=?",
                                (description, prix, quantite, categorie, nom)
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO products (name, description, price, quantity, category) VALUES (?,?,?,?,?)",
                                (nom, description, prix, quantite, categorie)
                            )

                        imported += 1

                    except Exception as e:
                        errors.append(f"Ligne {row_num}: {str(e)}")

                self.db.db.commit()

            # Résultat
            msg = f"Import terminé.\n\n{imported} produit(s) importé(s) avec succès."
            if errors:
                msg += f"\n\n{len(errors)} erreur(s):\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    msg += f"\n... et {len(errors) - 10} autres erreurs."
                QMessageBox.warning(self.view, "Import partiel", msg)
            else:
                QMessageBox.information(self.view, "Import réussi", msg)

            print(f"[FileManager] Import CSV: {imported} produits, {len(errors)} erreurs")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'import", f"Erreur lors de l'import:\n{str(e)}")
            print(f"[FileManager] ERREUR import: {e}")

    # ========== EXPORT CSV ==========

    @Slot(str)
    def export_stock_csv(self, file_path: str):
        """Exporte les produits vers un fichier CSV."""
        try:
            cursor = self.db.db.get_cursor()

            # Récupérer tous les produits
            cursor.execute("""
                SELECT name, description, price, quantity, category
                FROM products
                ORDER BY name
            """)
            products = cursor.fetchall()

            if not products:
                QMessageBox.information(
                    self.view, "Stock vide",
                    "Il n'y a aucun produit à exporter dans la base de données."
                )
                return

            path = Path(file_path)
            # Ajouter .csv si pas d'extension
            if not path.suffix:
                path = path.with_suffix('.csv')

            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')

                # En-têtes
                writer.writerow(['Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'])

                # Données
                for product in products:
                    writer.writerow([
                        product[0] or '',
                        product[1] or '',
                        str(product[2]).replace('.', ',') if product[2] else '0',
                        product[3] or 0,
                        product[4] or 'Général',
                    ])

            size_kb = path.stat().st_size / 1024

            QMessageBox.information(
                self.view, "Export réussi",
                f"{len(products)} produit(s) exporté(s) avec succès.\n\n"
                f"Fichier: {path.name}\n"
                f"Taille: {size_kb:.1f} KB\n"
                f"Emplacement: {path.absolute()}"
            )

            print(f"[FileManager] Export CSV: {len(products)} produits → {path}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur d'export", f"Erreur lors de l'export:\n{str(e)}")
            print(f"[FileManager] ERREUR export: {e}")

    # ========== SAUVEGARDE ==========

    @Slot()
    def create_backup(self):
        """Crée une sauvegarde de la base de données."""
        try:
            if not self.db_path.exists():
                QMessageBox.warning(self.view, "Base introuvable", f"Fichier de base de données introuvable:\n{self.db_path}")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"sauvegarde_{timestamp}.db"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(str(self.db_path), str(backup_path))

            size_kb = backup_path.stat().st_size / 1024

            # Rafraîchir la liste
            self._refresh_backups_list()

            QMessageBox.information(
                self.view, "Sauvegarde créée",
                f"Sauvegarde créée avec succès.\n\n"
                f"Fichier: {backup_name}\n"
                f"Taille: {size_kb:.1f} KB\n"
                f"Dossier: {self.backup_dir.absolute()}"
            )

            print(f"[FileManager] Sauvegarde créée: {backup_path}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
            print(f"[FileManager] ERREUR sauvegarde: {e}")

    # ========== RESTAURATION ==========

    @Slot(str)
    def restore_backup(self, backup_path: str):
        """Restaure une sauvegarde."""
        try:
            path = Path(backup_path)
            if not path.exists():
                QMessageBox.warning(self.view, "Fichier introuvable", f"La sauvegarde n'existe pas:\n{backup_path}")
                return

            reply = QMessageBox.question(
                self.view, "Confirmer la restauration",
                f"ATTENTION : Cette action remplacera la base de données actuelle.\n\n"
                f"Sauvegarde à restaurer:\n{path.name}\n\n"
                f"Une sauvegarde automatique sera créée avant la restauration.\n\n"
                f"Continuer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            # Créer une sauvegarde automatique avant restauration
            auto_backup = self.backup_dir / f"avant_restauration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if self.db_path.exists():
                shutil.copy2(str(self.db_path), str(auto_backup))

            # Restaurer
            shutil.copy2(str(path), str(self.db_path))

            QMessageBox.information(
                self.view, "Restauration réussie",
                f"Base de données restaurée avec succès.\n\n"
                f"Depuis: {path.name}\n\n"
                f"Une sauvegarde de sécurité a été créée:\n{auto_backup.name}\n\n"
                f"Redémarrez l'application pour que les changements prennent effet."
            )

            print(f"[FileManager] Restauration: {path} → {self.db_path}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la restauration:\n{str(e)}")
            print(f"[FileManager] ERREUR restauration: {e}")

    # ========== SUPPRESSION SAUVEGARDE ==========

    @Slot(str)
    def delete_backup(self, backup_path: str):
        """Supprime une sauvegarde."""
        try:
            path = Path(backup_path)

            reply = QMessageBox.question(
                self.view, "Supprimer la sauvegarde",
                f"Supprimer définitivement:\n{path.name} ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply != QMessageBox.Yes:
                return

            path.unlink()
            self._refresh_backups_list()

            print(f"[FileManager] Sauvegarde supprimée: {path}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la suppression:\n{str(e)}")

    # ========== MODÈLE CSV ==========

    def generate_csv_template(self, file_path: str):
        """Génère un fichier CSV modèle pour l'import."""
        try:
            path = Path(file_path)
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(['Nom', 'Description', 'Prix', 'Quantité', 'Catégorie'])
                writer.writerow(['Stylo Bic', 'Stylo à bille bleu', '250', '100', 'Papeterie'])
                writer.writerow(['Cahier 100 pages', 'Cahier grand format', '800', '50', 'Cahiers'])
                writer.writerow(['Dictionnaire', 'Dictionnaire français', '5000', '20', 'Livres'])

            QMessageBox.information(
                self.view, "Modèle créé",
                f"Modèle CSV créé avec succès:\n{path.absolute()}\n\n"
                f"Ouvrez-le avec Excel ou un éditeur de texte pour l'adapter."
            )
            print(f"[FileManager] Modèle CSV créé: {path}")

        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur lors de la création du modèle:\n{str(e)}")