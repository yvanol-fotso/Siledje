"""
Configuration de l'application
"""
import os
from pathlib import Path


class AppConfig:
    """Configuration globale de l'application"""
    
    def __init__(self):
        # Informations de base
        self.app_name = "Librairie-Papeterie"
        self.version = "1.0.0"
        self.organization = "VotreEntreprise"
        
        # Chemins
        self.base_dir = Path(__file__).parent.parent.parent
        self.assets_dir = self.base_dir / "assets"
        self.styles_dir = self.assets_dir / "styles"
        self.images_dir = self.assets_dir / "images"
        
        # Thème par défaut
        self.default_theme = "light"  # 'light' ou 'dark'
        
        # Base de données
        self.db_path = self.base_dir / "data" / "librairie.db"
        
        # Interface
        self.window_width = 1200
        self.window_height = 800
        
        # Login
        self.max_login_attempts = 5
        self.session_timeout = 3600  # secondes
        
        # Debug
        self.debug_mode = True
        
        print(f"[AppConfig] Configuration initialisée")
        print(f"[AppConfig] Nom: {self.app_name}")
        print(f"[AppConfig] Version: {self.version}")
        print(f"[AppConfig] Thème par défaut: {self.default_theme}")
        print(f"[AppConfig] Dossier base: {self.base_dir}")
    
    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """
        Retourne le chemin complet vers un asset
        
        Args:
            asset_type (str): Type d'asset ('images', 'styles', etc.)
            filename (str): Nom du fichier
            
        Returns:
            Path: Chemin complet
        """
        asset_dirs = {
            'images': self.images_dir,
            'styles': self.styles_dir,
        }
        
        base_dir = asset_dirs.get(asset_type, self.assets_dir)
        return base_dir / filename
    
    def validate_paths(self) -> bool:
        """
        Vérifie que tous les chemins nécessaires existent
        
        Returns:
            bool: True si tous les chemins sont valides
        """
        paths_to_check = [
            self.base_dir,
            self.assets_dir,
            self.styles_dir,
            self.images_dir,
        ]
        
        all_valid = True
        for path in paths_to_check:
            if not path.exists():
                print(f"[AppConfig] Chemin manquant: {path}")
                all_valid = False
            else:
                print(f"[AppConfig]  Chemin valide: {path}")
        
        return all_valid