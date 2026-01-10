"""
Gestion de la configuration de l'application.
Charge les paramètres depuis config.json et fournit un accès centralisé.
"""

import os
import json
from pathlib import Path
from typing import Any, Optional


class AppConfig:
    """
    Configuration globale de l'application.
    Singleton pour garantir une instance unique dans toute l'application.
    """
    
    _instance: Optional['AppConfig'] = None
    
    def __new__(cls):
        """Implémente le pattern Singleton."""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialise la configuration."""
        if self._initialized:
            return
        
        # Chemins de base
        self.base_dir = Path(__file__).parent.parent.parent  # Remonte à la racine
        self.config_file = self.base_dir / "config.json"
        
        # Charger la configuration depuis le fichier JSON
        self._load_config()
        
        # Définir les chemins des assets
        self._setup_paths()
        
        # Valider que tous les chemins existent
        self.validate_paths()
        
        self._initialized = True
        
        print(f"✅ [AppConfig] Configuration initialisée")
        print(f"   Nom: {self.app_name}")
        print(f"   Version: {self.version}")
        print(f"   Base dir: {self.base_dir}")
    
    def _load_config(self):
        """Charge la configuration depuis config.json."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Informations de base
                self.app_name = config_data.get('app_name', 'Librairie-Papeterie')
                self.version = config_data.get('version', '1.0.0')
                
                # Configuration de la base de données
                db_config = config_data.get('database', {})
                self.db_name = db_config.get('name', 'data/librairie.db')
                self.auto_backup = db_config.get('auto_backup', True)
                self.backup_path = db_config.get('backup_path', 'data/backups/')
                
                # Configuration de l'interface
                ui_config = config_data.get('ui', {})
                self.theme = ui_config.get('theme', 'dark_style.qss')
                self.default_theme = ui_config.get('default_theme', 'dark_style.qss')
                self.auto_theme = ui_config.get('auto_theme', False)
                self.confirm_exit = ui_config.get('confirm_exit', True)
                
                # Configuration du stock
                stock_config = config_data.get('stock', {})
                self.low_stock_threshold = stock_config.get('low_stock_threshold', 10)
                self.alert_enabled = stock_config.get('alert_enabled', True)
                
                print(f"✅ Configuration chargée depuis {self.config_file}")
                
            else:
                # Valeurs par défaut si le fichier n'existe pas
                self._set_default_config()
                self._save_config()
                print(f"⚠️ Fichier config.json non trouvé, configuration par défaut créée")
                
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la configuration : {e}")
            self._set_default_config()
    
    def _set_default_config(self):
        """Définit les valeurs par défaut."""
        # Informations de base
        self.app_name = "Librairie-Papeterie"
        self.version = "2.0.0"
        
        # Base de données
        self.db_name = "data/librairie.db"
        self.auto_backup = True
        self.backup_path = "data/backups/"
        
        # Interface
        self.theme = "dark_style.qss"
        self.default_theme = "dark_style.qss"
        self.auto_theme = False
        self.confirm_exit = True
        
        # Stock
        self.low_stock_threshold = 10
        self.alert_enabled = True
    
    def _setup_paths(self):
        """Configure tous les chemins nécessaires."""
        # Dossiers principaux
        self.assets_dir = self.base_dir / "assets"
        self.styles_dir = self.assets_dir / "styles"
        self.images_dir = self.assets_dir / "images"
        self.icons_dir = self.assets_dir / "icons"
        self.data_dir = self.base_dir / "data"
        
        # Chemin de la base de données
        self.db_path = self.base_dir / self.db_name
        
        # Chemin des backups
        self.backup_dir = self.base_dir / self.backup_path
        
        # Paramètres d'interface
        self.window_width = 1200
        self.window_height = 800
        
        # Login
        self.max_login_attempts = 5
        self.session_timeout = 3600  # secondes
        
        # Debug
        self.debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """
        Retourne le chemin complet vers un asset.
        
        Args:
            asset_type: Type d'asset ('images', 'styles', 'icons')
            filename: Nom du fichier
            
        Returns:
            Chemin complet vers l'asset
        """
        asset_dirs = {
            'images': self.images_dir,
            'styles': self.styles_dir,
            'icons': self.icons_dir,
        }
        
        base_dir = asset_dirs.get(asset_type, self.assets_dir)
        return base_dir / filename
    
    def get_style_path(self, theme_name: Optional[str] = None) -> Path:
        """
        Retourne le chemin vers un fichier de style.
        
        Args:
            theme_name: Nom du thème (None = thème par défaut)
            
        Returns:
            Chemin vers le fichier .qss
        """
        theme = theme_name or self.theme
        return self.styles_dir / theme
    
    def validate_paths(self) -> bool:
        """
        Vérifie que tous les chemins nécessaires existent.
        Crée les dossiers manquants si nécessaire.
        
        Returns:
            True si tous les chemins sont valides
        """
        paths_to_check = [
            self.base_dir,
            self.assets_dir,
            self.styles_dir,
            self.images_dir,
            self.icons_dir,
            self.data_dir,
        ]
        
        all_valid = True
        for path in paths_to_check:
            if not path.exists():
                print(f"⚠️ Chemin manquant: {path}")
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Dossier créé: {path}")
                except Exception as e:
                    print(f"❌ Impossible de créer {path}: {e}")
                    all_valid = False
            else:
                print(f"✅ Chemin valide: {path}")
        
        # Créer le dossier de backup s'il n'existe pas
        if not self.backup_dir.exists():
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Dossier backup créé: {self.backup_dir}")
            except Exception as e:
                print(f"❌ Impossible de créer le dossier backup: {e}")
        
        return all_valid
    
    def _save_config(self):
        """Sauvegarde la configuration actuelle dans config.json."""
        try:
            config_data = {
                "app_name": self.app_name,
                "version": self.version,
                "database": {
                    "name": self.db_name,
                    "auto_backup": self.auto_backup,
                    "backup_path": self.backup_path
                },
                "ui": {
                    "theme": self.theme,
                    "default_theme": self.default_theme,
                    "auto_theme": self.auto_theme,
                    "confirm_exit": self.confirm_exit
                },
                "stock": {
                    "low_stock_threshold": self.low_stock_threshold,
                    "alert_enabled": self.alert_enabled
                }
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Configuration sauvegardée dans {self.config_file}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de la configuration : {e}")
    
    def update_config(self, section: str, key: str, value: Any):
        """
        Met à jour une valeur de configuration et sauvegarde.
        
        Args:
            section: Section de config ('ui', 'database', 'stock')
            key: Clé à mettre à jour
            value: Nouvelle valeur
        """
        try:
            if section == 'ui':
                if hasattr(self, key):
                    setattr(self, key, value)
            elif section == 'database':
                if hasattr(self, key):
                    setattr(self, key, value)
            elif section == 'stock':
                if hasattr(self, key):
                    setattr(self, key, value)
            
            self._save_config()
            print(f"✅ Configuration mise à jour: {section}.{key} = {value}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la configuration : {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        return getattr(self, key, default)
    
    def __repr__(self) -> str:
        """Représentation de la configuration."""
        return (f"AppConfig(app_name='{self.app_name}', version='{self.version}', "
                f"theme='{self.theme}')")


# Instance globale pour faciliter l'import
def get_config() -> AppConfig:
    """
    Retourne l'instance unique de la configuration.
    
    Returns:
        Instance d'AppConfig
    """
    return AppConfig()


# Alias pour rétrocompatibilité
config = get_config()