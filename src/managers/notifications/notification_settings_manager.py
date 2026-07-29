"""
Gestionnaire des parametres de notifications.
"""

from PySide6.QtCore import QObject, Slot, QSettings
from PySide6.QtWidgets import QMessageBox

from src.ui.views.notification_settings.notification_config import NotificationConfig


class NotificationSettingsManager(QObject):
    """Gestionnaire des parametres de notifications."""
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # Configuration
        self.config = NotificationConfig()
        self.settings = QSettings("VotreEntreprise", "LibrairiePapeterie")
        
        # Charger la configuration sauvegardee
        self._load_config()
        
        print(f"[NotificationSettingsManager v{self.version}] Initialise - Notifications: {self.config.enabled}")
    
    def _load_config(self):
        """Charge la configuration depuis QSettings."""
        try:
            saved_config = self.settings.value("notification_config", {})
            if isinstance(saved_config, dict):
                self.config.from_dict(saved_config)
                print("[NotificationSettingsManager] Configuration chargee")
        except Exception as e:
            print(f"[NotificationSettingsManager] Erreur chargement config: {e}")
    
    def _save_config(self):
        """Sauvegarde la configuration dans QSettings."""
        try:
            self.settings.setValue("notification_config", self.config.to_dict())
            self.settings.sync()
            print("[NotificationSettingsManager] Configuration sauvegardee")
        except Exception as e:
            print(f"[NotificationSettingsManager] Erreur sauvegarde config: {e}")
    
    def get_ui(self):
        """Retourne la vue associee a ce manager."""
        if self.view is None:
            from src.ui.views.notification_settings.notification_settings_view import NotificationSettingsView
            
            self.view = NotificationSettingsView(self.parent)
            self._connect_view_signals()
            self._initialize_view()
            
            print("[NotificationSettingsManager] Vue creee et initialisee")
        
        return self.view
    
    def _initialize_view(self):
        """Initialise la vue avec les donnees."""
        self.view.update_config_display(self.config)
        print("[NotificationSettingsManager] Vue initialisee avec succes")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.save_requested.connect(self.save_config)
        self.view.test_requested.connect(self.test_notification)
        self.view.reset_requested.connect(self.reset_config)
        print("[NotificationSettingsManager] Signaux connectes")
    
    # ========== SLOTS ==========
    
    @Slot(dict)
    def save_config(self, config_dict):
        """Sauvegarde la configuration."""
        try:
            self.config.from_dict(config_dict)
            self._save_config()
            
            QMessageBox.information(
                self.view,
                "Succes",
                "Les parametres de notifications ont ete enregistres avec succes."
            )
            
            print("[NotificationSettingsManager] Configuration sauvegardee")
        
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
                "Notifications desactivees",
                "Les notifications sont actuellement desactivees.\n\n"
                "Activez-les pour voir ce test."
            )
            return
        
        QMessageBox.information(
            self.view,
            "Test de notification",
            "Ceci est une notification de test.\n\n"
            "Si vous voyez ce message, les notifications fonctionnent correctement."
        )
        
        print("[NotificationSettingsManager] Notification de test affichee")
    
    @Slot()
    def reset_config(self):
        """Reinitialise la configuration aux valeurs par defaut."""
        reply = QMessageBox.question(
            self.view,
            "Reinitialisation",
            "Voulez-vous vraiment reinitialiser tous les parametres de notifications?\n\n"
            "Cette action est irreversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config = NotificationConfig()
            self._save_config()
            self.view.update_config_display(self.config)
            
            QMessageBox.information(
                self.view,
                "Succes",
                "Les parametres de notifications ont ete reinitialises."
            )
            
            print("[NotificationSettingsManager] Configuration reinitialisee")
    
    # ========== METHODES PUBLIQUES ==========
    
    def is_enabled(self) -> bool:
        """Retourne True si les notifications sont activees."""
        return self.config.enabled
    
    def get_config(self) -> NotificationConfig:
        """Retourne la configuration actuelle."""
        return self.config
    
    def set_theme(self, is_dark: bool):
        """Change le theme de la vue"""
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[NotificationSettingsManager] Theme applique: {'dark' if is_dark else 'light'}")