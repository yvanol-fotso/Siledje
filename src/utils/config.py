"""
Gestion de la configuration de l'application.
Charge les paramètres depuis config.json et fournit un accès centralisé.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Any, Optional


class AppConfig:
    """
    Configuration globale de l'application (Singleton).

    - resource_dir : fichiers embarqués en lecture seule (assets, config.json d'origine)
    - base_dir     : fichiers modifiables (DB, backups, config.json actif)
      * en développement : racine du projet
      * dans l'exe PyInstaller : %APPDATA%\\Siledje
    """

    _instance: Optional['AppConfig'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Chemins de base
        if getattr(sys, "frozen", False):
            self.resource_dir = Path(sys._MEIPASS)
            self.base_dir = Path(os.environ.get("APPDATA", str(Path.home()))) / "Siledje"
            self.base_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.resource_dir = Path(__file__).parent.parent.parent
            self.base_dir = self.resource_dir

        self.config_file = self.base_dir / "config.json"

        # Première exécution de l'exe : copier le config.json embarqué
        if getattr(sys, "frozen", False) and not self.config_file.exists():
            bundled = self.resource_dir / "config.json"
            if bundled.exists():
                try:
                    shutil.copy2(bundled, self.config_file)
                except Exception as e:
                    print(f"❌ Copie de config.json impossible : {e}")

        self._load_config()
        self._setup_paths()
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

                self.app_name = config_data.get('app_name', 'Siledje')
                self.version = config_data.get('version', '1.0.0')

                # "siledje.db" tout court : le JSON prime sur ce défaut,
                # donc config.json doit contenir "siledje.db" et pas "data/siledje.db".
                db_config = config_data.get('database', {})
                self.db_name = db_config.get('name', 'siledje.db')
                self.auto_backup = db_config.get('auto_backup', True)
                self.backup_path = db_config.get('backup_path', 'backups/')

                ui_config = config_data.get('ui', {})
                self.theme = ui_config.get('theme', 'dark_style.qss')
                self.default_theme = ui_config.get('default_theme', 'dark_style.qss')
                self.auto_theme = ui_config.get('auto_theme', False)
                self.confirm_exit = ui_config.get('confirm_exit', True)

                stock_config = config_data.get('stock', {})
                self.low_stock_threshold = stock_config.get('low_stock_threshold', 10)
                self.alert_enabled = stock_config.get('alert_enabled', True)

                print(f"✅ Configuration chargée depuis {self.config_file}")

            else:
                self._set_default_config()
                self._save_config()
                print(f"⚠️ Fichier config.json non trouvé, configuration par défaut créée")

        except Exception as e:
            print(f"❌ Erreur lors du chargement de la configuration : {e}")
            self._set_default_config()

    def _set_default_config(self):
        """Définit les valeurs par défaut."""
        self.app_name = "Siledje"
        self.version = "2.0.0"

        self.db_name = "siledje.db"
        self.auto_backup = True
        self.backup_path = "backups/"

        self.theme = "dark_style.qss"
        self.default_theme = "dark_style.qss"
        self.auto_theme = False
        self.confirm_exit = True

        self.low_stock_threshold = 10
        self.alert_enabled = True

    def _setup_paths(self):
        """Configure tous les chemins nécessaires."""
        # Assets : lecture seule, embarqués -> resource_dir
        self.assets_dir = self.resource_dir / "assets"
        self.styles_dir = self.assets_dir / "styles"
        self.images_dir = self.assets_dir / "images"
        self.icons_dir = self.assets_dir / "icons"

        # DB et backups : écriture -> base_dir
        self.db_path = self.base_dir / self.db_name
        self.backup_dir = self.base_dir / self.backup_path

        # Interface
        self.window_width = 1200
        self.window_height = 800

        # Login
        self.max_login_attempts = 5
        self.session_timeout = 3600  # secondes

        # Debug
        self.debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'

    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """Retourne le chemin complet vers un asset ('images', 'styles', 'icons')."""
        asset_dirs = {
            'images': self.images_dir,
            'styles': self.styles_dir,
            'icons': self.icons_dir,
        }
        base_dir = asset_dirs.get(asset_type, self.assets_dir)
        return base_dir / filename

    def get_style_path(self, theme_name: Optional[str] = None) -> Path:
        """Retourne le chemin vers un fichier .qss (thème par défaut si None)."""
        theme = theme_name or self.theme
        return self.styles_dir / theme

    def validate_paths(self) -> bool:
        """Vérifie les chemins nécessaires et crée les dossiers manquants."""
        paths_to_check = [
            self.base_dir,
            self.assets_dir,
            self.styles_dir,
            self.images_dir,
            self.icons_dir,
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
        """Met à jour une valeur de configuration et sauvegarde."""
        try:
            if section in ('ui', 'database', 'stock'):
                if hasattr(self, key):
                    setattr(self, key, value)

            self._save_config()
            print(f"✅ Configuration mise à jour: {section}.{key} = {value}")

        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la configuration : {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration."""
        return getattr(self, key, default)

    def __repr__(self) -> str:
        return (f"AppConfig(app_name='{self.app_name}', version='{self.version}', "
                f"theme='{self.theme}')")


def get_config() -> AppConfig:
    """Retourne l'instance unique de la configuration."""
    return AppConfig()


# Alias pour rétrocompatibilité
config = get_config()