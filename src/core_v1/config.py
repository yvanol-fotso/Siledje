import json
from pathlib import Path
from typing import Any, Dict
from PySide6.QtCore import QObject, Signal


class AppConfig(QObject):
    config_changed = Signal(str, object)  # key, value

    def __init__(self, config_path: str = "config/settings.json"):
        super().__init__()
        self.config_path = Path(config_path)
        self._data = self._load_config()

    @property
    def app_name(self) -> str:
        return self._data.get("app_name", "Librairie-Papeterie")

    @property
    def version(self) -> str:
        return self._data.get("version", "1.0.0")

    @property
    def default_theme(self) -> str:
        return self._data.get("theme", "light_style.qss")

    @default_theme.setter
    def default_theme(self, value: str):
        self._data["theme"] = value
        self.config_changed.emit("theme", value)
        self.save_config()

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.config_path.exists():
                return self._create_default_config()

            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Crée une configuration par défaut"""
        default_config = {
            "app_name": "Librairie-Papeterie",
            "version": "1.0.0",
            "theme": "light_style.qss",
            "confirm_exit": True,
            "auto_backup": True,
            "backup_path": "backups/",
            "recent_files": []
        }
        self.save_config(default_config)
        return default_config

    def save_config(self, config: Dict[str, Any] = None):
        """Sauvegarde la configuration dans le fichier"""
        config = config or self._data
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Obtient une valeur de configuration"""
        return self._data.get(key, default)

    def set(self, key: str, value: Any, save: bool = True):
        """Définit une valeur de configuration"""
        self._data[key] = value
        self.config_changed.emit(key, value)
        if save:
            self.save_config()