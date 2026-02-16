"""
Gestionnaire des paramètres de base de données.
Gère l'optimisation, la vérification, les sauvegardes et les statistiques.
"""

from PySide6.QtCore import QObject, Slot, QSettings
from PySide6.QtWidgets import QMessageBox
import os
import shutil
from datetime import datetime
from pathlib import Path


class DatabaseSettingsManager(QObject):
    """Gestionnaire des paramètres et opérations de base de données."""
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Récupérer l'instance de DatabaseManager depuis parent
        if hasattr(parent, 'db'):
            self.db_manager = parent.db
        else:
            from src.database.manager import DatabaseManager
            self.db_manager = DatabaseManager()
        
        # Récupérer le chemin de la BDD
        if hasattr(self.db_manager.db, 'db_name'):
            self.db_path = self.db_manager.db.db_name
        else:
            self.db_path = "librairie.db"
        
        print(f"[DatabaseSettingsManager v{self.version}] Initialisé - BDD: {self.db_path}")
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.database_settings_view import DatabaseSettingsView
            
            self.view = DatabaseSettingsView(self.parent)
            self._connect_view_signals()
            self._update_stats()
            
            print("[DatabaseSettingsManager] Vue créée et initialisée")
        
        return self.view
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.optimize_requested.connect(self.optimize_database)
        self.view.check_integrity_requested.connect(self.check_integrity)
        self.view.backup_requested.connect(self.create_backup)
        self.view.refresh_stats_requested.connect(self._update_stats)
        print("[DatabaseSettingsManager] Signaux connectés")
    
    def _update_stats(self):
        """Met à jour les statistiques de la base de données."""
        try:
            stats = self.get_database_stats()
            if self.view:
                self.view.update_stats_display(stats)
        except Exception as e:
            print(f"[DatabaseSettingsManager] Erreur mise à jour stats: {e}")
    
    # ========== OPÉRATIONS BDD ==========
    
    @Slot()
    def optimize_database(self):
        """Optimise la base de données (VACUUM)."""
        try:
            reply = QMessageBox.question(
                self.view,
                "Optimiser la base de données",
                "L'optimisation va réorganiser la base de données pour améliorer les performances.\n\n"
                "Cette opération peut prendre quelques instants.\n\n"
                "Continuer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                cursor = self.db_manager.db.get_cursor()
                
                # VACUUM pour optimiser
                cursor.execute("VACUUM")
                
                # ANALYZE pour mettre à jour les statistiques
                cursor.execute("ANALYZE")
                
                self.db_manager.db.commit()
                
                # Mettre à jour les stats
                self._update_stats()
                
                QMessageBox.information(
                    self.view,
                    "Succès",
                    "La base de données a été optimisée avec succès."
                )
                
                print("[DatabaseSettingsManager] Optimisation réussie")
        
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de l'optimisation:\n{str(e)}"
            )
            print(f"[DatabaseSettingsManager] ERREUR optimisation: {e}")
    
    @Slot()
    def check_integrity(self):
        """Vérifie l'intégrité de la base de données."""
        try:
            cursor = self.db_manager.db.get_cursor()
            
            # PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] == 'ok':
                QMessageBox.information(
                    self.view,
                    "Vérification d'intégrité",
                    "La base de données est intègre.\n\n"
                    "Aucune erreur détectée."
                )
                print("[DatabaseSettingsManager] Intégrité OK")
            else:
                QMessageBox.warning(
                    self.view,
                    "Problème d'intégrité",
                    f"Problème détecté:\n{result[0] if result else 'Erreur inconnue'}"
                )
                print(f"[DatabaseSettingsManager] Problème d'intégrité: {result}")
        
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la vérification:\n{str(e)}"
            )
            print(f"[DatabaseSettingsManager] ERREUR vérification: {e}")
    
    @Slot()
    def create_backup(self):
        """Crée une sauvegarde de la base de données."""
        try:
            # Créer le dossier backups s'il n'existe pas
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            # Nom du fichier de sauvegarde avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"librairie_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename
            
            # Copier le fichier
            shutil.copy2(self.db_path, backup_path)
            
            # Obtenir la taille du fichier
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            QMessageBox.information(
                self.view,
                "Sauvegarde créée",
                f"Sauvegarde créée avec succès:\n\n"
                f"Fichier: {backup_filename}\n"
                f"Taille: {size_mb:.2f} MB\n"
                f"Emplacement: {backup_path.absolute()}"
            )
            
            print(f"[DatabaseSettingsManager] Sauvegarde créée: {backup_path}")
        
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la sauvegarde:\n{str(e)}"
            )
            print(f"[DatabaseSettingsManager] ERREUR sauvegarde: {e}")
    
    # ========== STATISTIQUES ==========
    
    def get_database_stats(self):
        """Récupère les statistiques de la base de données."""
        try:
            cursor = self.db_manager.db.get_cursor()
            
            stats = {
                'file_size': 0,
                'total_products': 0,
                'total_barcodes': 0,
                'total_sales': 0,
                'total_users': 0,
                'page_count': 0,
                'page_size': 0
            }
            
            # Taille du fichier
            if os.path.exists(self.db_path):
                stats['file_size'] = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
            
            # Compter les produits
            cursor.execute("SELECT COUNT(*) FROM products")
            result = cursor.fetchone()
            if result:
                stats['total_products'] = result[0]
            
            # Compter les codes-barres
            cursor.execute("SELECT COUNT(*) FROM barcodes")
            result = cursor.fetchone()
            if result:
                stats['total_barcodes'] = result[0]
            
            # Compter les ventes
            cursor.execute("SELECT COUNT(*) FROM sales")
            result = cursor.fetchone()
            if result:
                stats['total_sales'] = result[0]
            
            # Compter les utilisateurs
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            if result:
                stats['total_users'] = result[0]
            
            # Informations sur les pages
            cursor.execute("PRAGMA page_count")
            result = cursor.fetchone()
            if result:
                stats['page_count'] = result[0]
            
            cursor.execute("PRAGMA page_size")
            result = cursor.fetchone()
            if result:
                stats['page_size'] = result[0]
            
            return stats
        
        except Exception as e:
            print(f"[DatabaseSettingsManager] Erreur récupération stats: {e}")
            return {
                'file_size': 0,
                'total_products': 0,
                'total_barcodes': 0,
                'total_sales': 0,
                'total_users': 0,
                'page_count': 0,
                'page_size': 0
            }