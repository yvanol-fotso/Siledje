"""
Gestionnaire des paramètres de notifications.
Gère l'activation, les types, les sons et l'affichage des notifications.
"""

from PySide6.QtCore import QObject, Slot, QSettings
from PySide6.QtWidgets import QMessageBox


class NotificationConfig:
    """Modèle de configuration des notifications."""
    def __init__(self):
        self.enabled = True
        self.show_desktop = True
        self.show_sound = True
        self.show_tray = True
        self.duration = 5  # secondes
        
        # Types de notifications
        self.stock_low = True
        self.sales_success = True
        self.errors = True
        self.warnings = True
        self.info = True
        
    def to_dict(self):
        return {
            'enabled': self.enabled,
            'show_desktop': self.show_desktop,
            'show_sound': self.show_sound,
            'show_tray': self.show_tray,
            'duration': self.duration,
            'stock_low': self.stock_low,
            'sales_success': self.sales_success,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }
    
    def from_dict(self, data):
        """Charge la configuration depuis un dictionnaire."""
        self.enabled = data.get('enabled', True)
        self.show_desktop = data.get('show_desktop', True)
        self.show_sound = data.get('show_sound', True)
        self.show_tray = data.get('show_tray', True)
        self.duration = data.get('duration', 5)
        self.stock_low = data.get('stock_low', True)
        self.sales_success = data.get('sales_success', True)
        self.errors = data.get('errors', True)
        self.warnings = data.get('warnings', True)
        self.info = data.get('info', True)


class NotificationSettingsManager(QObject):
    """Gestionnaire des paramètres de notifications."""
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Configuration
        self.config = NotificationConfig()
        self.settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        
        # Charger la configuration sauvegardée
        self._load_config()
        
        print(f"[NotificationSettingsManager v{self.version}] Initialisé - Notifications: {self.config.enabled}")
    
    def _load_config(self):
        """Charge la configuration depuis QSettings."""
        try:
            saved_config = self.settings.value("notification_config", {})
            if isinstance(saved_config, dict):
                self.config.from_dict(saved_config)
                print("[NotificationSettingsManager] Configuration chargée")
        except Exception as e:
            print(f"[NotificationSettingsManager] Erreur chargement config: {e}")
    
    def _save_config(self):
        """Sauvegarde la configuration dans QSettings."""
        try:
            self.settings.setValue("notification_config", self.config.to_dict())
            self.settings.sync()
            print("[NotificationSettingsManager] Configuration sauvegardée")
        except Exception as e:
            print(f"[NotificationSettingsManager] Erreur sauvegarde config: {e}")
    
    def get_ui(self):
        """Retourne la vue associée à ce manager."""
        if self.view is None:
            from src.ui.views.notification_settings_view import NotificationSettingsView
            
            self.view = NotificationSettingsView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[NotificationSettingsManager] Vue créée et initialisée")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les données."""
        self.view.update_config_display(self.config)
        print("[NotificationSettingsManager] Vue initialisée avec succès")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.save_requested.connect(self.save_config)
        self.view.test_requested.connect(self.test_notification)
        self.view.reset_requested.connect(self.reset_config)
        print("[NotificationSettingsManager] Signaux connectés")
    
    # ========== SLOTS ==========
    
    @Slot(dict)
    def save_config(self, config_dict):
        """Sauvegarde la configuration."""
        try:
            self.config.from_dict(config_dict)
            self._save_config()
            
            QMessageBox.information(
                self.view,
                "Succès",
                "Les paramètres de notifications ont été enregistrés avec succès."
            )
            
            print("[NotificationSettingsManager] Configuration sauvegardée")
        
        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors de la sauvegarde:\n{str(e)}"
            )
            print(f"[NotificationSettingsManager] ERREUR sauvegarde: {e}")
    
    @Slot()
    def test_notification(self):
        """Teste l'affichage d'une notification."""
        if not self.config.enabled:
            QMessageBox.warning(
                self.view,
                "Notifications désactivées",
                "Les notifications sont actuellement désactivées.\n\n"
                "Activez-les pour voir ce test."
            )
            return
        
        # Tester avec une notification d'information
        QMessageBox.information(
            self.view,
            "Test de notification",
            "Ceci est une notification de test.\n\n"
            "Si vous voyez ce message, les notifications fonctionnent correctement."
        )
        
        print("[NotificationSettingsManager] Notification de test affichée")
    
    @Slot()
    def reset_config(self):
        """Réinitialise la configuration aux valeurs par défaut."""
        reply = QMessageBox.question(
            self.view,
            "Réinitialisation",
            "Voulez-vous vraiment réinitialiser tous les paramètres de notifications?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Réinitialiser
            self.config = NotificationConfig()
            self._save_config()
            
            # Mettre à jour la vue
            self.view.update_config_display(self.config)
            
            QMessageBox.information(
                self.view,
                "Succès",
                "Les paramètres de notifications ont été réinitialisés."
            )
            
            print("[NotificationSettingsManager] Configuration réinitialisée")
    
    # ========== MÉTHODES PUBLIQUES ==========
    
    def is_enabled(self) -> bool:
        """Retourne True si les notifications sont activées."""
        return self.config.enabled
    
    def get_config(self) -> NotificationConfig:
        """Retourne la configuration actuelle."""
        return self.config