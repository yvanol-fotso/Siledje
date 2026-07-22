"""
Gestionnaire des paramètres de base de données — requêtes alignées sur le vrai schéma.
"""

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox
import os
import shutil
from datetime import datetime
from pathlib import Path

from src.database.connection import get_db_connection


class DatabaseSettingsManager(QObject):

    version = "2.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        self.db = get_db_connection()
        self.db_path = self.db.db_name

        print(f"[DatabaseSettingsManager v{self.version}] Initialisé - BDD: {self.db_path}")

    def get_ui(self):
        if self.view is None:
            from src.ui.views.database_settings_view import DatabaseSettingsView
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
        reply = QMessageBox.question(
            self.view, "Optimiser la base de données",
            "Cette opération peut prendre quelques instants. Continuer ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            cursor = self.db.get_cursor()
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            self.db.commit()
            self._update_stats()
            QMessageBox.information(self.view, "Succès", "Base de données optimisée.")

    @Slot()
    def check_integrity(self):
        cursor = self.db.get_cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result and result[0] == 'ok':
            QMessageBox.information(self.view, "Vérification", "La base de données est intègre.")
        else:
            QMessageBox.warning(self.view, "Problème", f"{result[0] if result else 'Erreur inconnue'}")

    @Slot()
    def create_backup(self):
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"librairie_backup_{timestamp}.db"
            shutil.copy2(self.db_path, backup_path)
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            QMessageBox.information(
                self.view, "Sauvegarde créée",
                f"Fichier: {backup_path.name}\nTaille: {size_mb:.2f} MB"
            )
        except Exception as e:
            QMessageBox.critical(self.view, "Erreur", f"Erreur sauvegarde:\n{e}")

    def get_database_stats(self):
        stats = {'file_size': 0, 'total_products': 0, 'total_barcodes': 0,
                 'total_sales': 0, 'total_users': 0, 'total_tables': 0}
        try:
            if os.path.exists(self.db_path):
                stats['file_size'] = os.path.getsize(self.db_path) / (1024 * 1024)

            cursor = self.db.get_cursor()
            for table, key in [("products", "total_products"), ("barcodes", "total_barcodes"),
                               ("sales", "total_sales"), ("users", "total_users")]:
                if self.db.table_exists(table):
                    cursor.execute(f"SELECT COUNT(*) as c FROM {table}")
                    stats[key] = cursor.fetchone()["c"]

            stats['total_tables'] = len(self.db.list_tables())
        except Exception as e:
            print(f"[DatabaseSettingsManager] Erreur stats: {e}")
        return stats