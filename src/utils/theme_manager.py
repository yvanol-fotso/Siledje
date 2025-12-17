"""
Gestionnaire de thèmes pour l'application
Gère les thèmes clair et sombre
"""
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal


class ThemeManager(QObject):
    """
    Gestionnaire de thèmes pour l'application
    Permet de basculer entre mode clair et sombre
    """
    
    theme_changed = Signal(str)  # Émet le nom du nouveau thème
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self._current_theme = "light"  # Thème par défaut
        
        # Chemins vers les fichiers de style
        self.styles_dir = Path(__file__).parent.parent.parent / "assets" / "styles"
        
        print(f"[ThemeManager] Initialisé")
        print(f"[ThemeManager] Dossier styles: {self.styles_dir}")
        print(f"[ThemeManager] Thème par défaut: {self._current_theme}")
        
        # Charger le thème sauvegardé (si disponible)
        self._load_saved_theme()
    
    def _load_saved_theme(self):
        """Charge le thème sauvegardé depuis la configuration"""
        try:
            # TODO: Charger depuis un fichier de config ou base de données
            # Pour l'instant, on utilise le thème par défaut
            saved_theme = getattr(self.config, 'default_theme', 'light')
            if saved_theme in ['light', 'dark']:
                self._current_theme = saved_theme
                print(f"[ThemeManager] Thème chargé: {self._current_theme}")
        except Exception as e:
            print(f"[ThemeManager] Erreur chargement thème: {e}")
    
    def get_current_theme(self) -> str:
        """Retourne le thème actuel ('light' ou 'dark')"""
        return self._current_theme
    
    def set_theme(self, theme: str):
        """
        Définit le thème de l'application
        
        Args:
            theme (str): 'light' ou 'dark'
        """
        if theme not in ['light', 'dark']:
            print(f"[ThemeManager] Thème invalide: {theme}")
            return
        
        print(f"[ThemeManager] Changement de thème: {self._current_theme} → {theme}")
        
        self._current_theme = theme
        
        # Appliquer le thème global à l'application
        self._apply_global_theme()
        
        # Émettre le signal de changement
        self.theme_changed.emit(theme)
        
        # Sauvegarder le thème
        self._save_theme()
        
        print(f"[ThemeManager] Thème appliqué: {theme}")
    
    def toggle_theme(self):
        """Bascule entre thème clair et sombre"""
        new_theme = 'dark' if self._current_theme == 'light' else 'light'
        self.set_theme(new_theme)
    
    def _apply_global_theme(self):
        """Applique le thème global à l'application Qt"""
        try:
            app = QApplication.instance()
            if app:
                # Charger le stylesheet principal (si existant)
                main_stylesheet = self.load_stylesheet('main')
                if main_stylesheet:
                    app.setStyleSheet(main_stylesheet)
                    print(f"[ThemeManager] Stylesheet global appliqué")
        except Exception as e:
            print(f"[ThemeManager] Erreur application thème global: {e}")
    
    def load_stylesheet(self, name: str) -> str:
        """
        Charge un fichier QSS
        
        Args:
            name (str): Nom du fichier (sans extension)
            
        Returns:
            str: Contenu du fichier QSS ou chaîne vide
        """
        qss_path = self.styles_dir / f"{name}.qss"
        
        try:
            if qss_path.exists():
                with open(qss_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"[ThemeManager] Stylesheet chargé: {name}.qss ({len(content)} caractères)")
                return content
            else:
                print(f"[ThemeManager] ⚠ Fichier non trouvé: {qss_path}")
                return ""
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur chargement {name}.qss: {e}")
            return ""
    
    def _save_theme(self):
        """Sauvegarde le thème actuel"""
        try:
            # TODO: Sauvegarder dans un fichier de config ou base de données
            # Pour l'instant, juste un log
            print(f"[ThemeManager] Thème sauvegardé: {self._current_theme}")
        except Exception as e:
            print(f"[ThemeManager] Erreur sauvegarde thème: {e}")
    
    def get_color(self, color_name: str) -> str:
        """
        Retourne une couleur selon le thème actuel
        
        Args:
            color_name (str): Nom de la couleur (primary, secondary, etc.)
            
        Returns:
            str: Code couleur hexadécimal
        """
        colors = {
            'light': {
                'primary': '#3498db',
                'secondary': '#2980b9',
                'success': '#27ae60',
                'danger': '#e74c3c',
                'warning': '#f39c12',
                'info': '#3498db',
                'background': '#f5f5f5',
                'surface': '#ffffff',
                'text': '#2c3e50',
                'text_secondary': '#7f8c8d',
            },
            'dark': {
                'primary': '#1abc9c',
                'secondary': '#16a085',
                'success': '#27ae60',
                'danger': '#e74c3c',
                'warning': '#f39c12',
                'info': '#1abc9c',
                'background': '#1e2a38',
                'surface': '#2c3e50',
                'text': '#ecf0f1',
                'text_secondary': '#95a5a6',
            }
        }
        
        return colors[self._current_theme].get(color_name, '#000000')
    
    def apply_to_widget(self, widget, stylesheet_name: str = None):
        """
        Applique le thème à un widget spécifique
        
        Args:
            widget: Widget Qt à thématiser
            stylesheet_name (str): Nom du stylesheet à charger (optionnel)
        """
        if stylesheet_name:
            stylesheet = self.load_stylesheet(stylesheet_name)
            if stylesheet:
                widget.setStyleSheet(stylesheet)
        
        # Définir la propriété theme pour le CSS
        widget.setProperty("theme", self._current_theme)
        
        # Forcer la mise à jour du style
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()