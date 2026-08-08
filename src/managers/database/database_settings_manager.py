"""
Gestionnaire des parametres de base de donnees.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Slot

from src.database.connection import get_db_connection
from src.ui.widgets.InfoDialog import InfoDialog


class DatabaseSettingsManager(QObject):

    version = "2.1"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.db = get_db_connection()
        self.db_path = self.db.db_name

        print(f"[DatabaseSettingsManager v{self.version}] Initialise - BDD: {self.db_path}")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.database_settings.database_settings_view import DatabaseSettingsView
            self.view = DatabaseSettingsView(self.parent)
            self._connect_view_signals()
            self._update_stats()
        return self.view

    def _connect_view_signals(self):
        self.view.optimize_requested.connect(self.optimize_database)
        self.view.check_integrity_requested.connect(self.check_integrity)
        self.view.backup_requested.connect(self.create_backup)
        self.view.refresh_stats_requested.connect(self._update_stats)

    def _update_stats(self):
        stats = self.get_database_stats()
        if self.view:
            self.view.update_stats_display(stats)

    @Slot()
    def optimize_database(self):
        confirmed = InfoDialog.question(
            self.view, "Optimiser la base de donnees",
            "Cette operation peut prendre quelques instants. Continuer ?",
            ok_text="Oui", cancel_text="Non",
        )
        if confirmed:
            try:
                cursor = self.db.get_cursor()
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                self.db.commit()
                self._update_stats()
                InfoDialog.success(self.view, "Succes", "Base de donnees optimisee.")
            except Exception as e:
                InfoDialog.error(self.view, "Erreur", f"Erreur lors de l'optimisation:\n{e}")

    @Slot()
    def check_integrity(self):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result and result[0] == 'ok':
                InfoDialog.success(self.view, "Verification", "La base de donnees est integre.")
            else:
                InfoDialog.warning(self.view, "Probleme", f"{result[0] if result else 'Erreur inconnue'}")
        except Exception as e:
            InfoDialog.error(self.view, "Erreur", f"Erreur lors de la verification:\n{e}")

    @Slot()
    def create_backup(self):
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"librairie_backup_{timestamp}.db"
            shutil.copy2(self.db_path, backup_path)
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            InfoDialog.success(
                self.view, "Sauvegarde creee",
                f"Fichier: {backup_path.name}\nTaille: {size_mb:.2f} MB"
            )
        except Exception as e:
            InfoDialog.error(self.view, "Erreur", f"Erreur sauvegarde:\n{e}")

    def get_database_stats(self):
        stats = {
            'file_size': 0, 'total_products': 0, 'total_barcodes': 0,
            'total_sales': 0, 'total_users': 0, 'total_tables': 0
        }
        try:
            if os.path.exists(self.db_path):
                stats['file_size'] = os.path.getsize(self.db_path) / (1024 * 1024)

            cursor = self.db.get_cursor()
            for table, key in [
                ("products", "total_products"),
                ("barcodes", "total_barcodes"),
                ("sales", "total_sales"),
                ("users", "total_users")
            ]:
                if self.db.table_exists(table):
                    cursor.execute(f"SELECT COUNT(*) as c FROM {table}")
                    row = cursor.fetchone()
                    stats[key] = row["c"] if row else 0

            stats['total_tables'] = len(self.db.list_tables())
        except Exception as e:
            print(f"[DatabaseSettingsManager] Erreur stats: {e}")
        return stats

    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[DatabaseSettingsManager] Theme applique: {'dark' if is_dark else 'light'}")