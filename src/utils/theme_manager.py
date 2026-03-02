"""
Gestionnaire de thèmes pour l'application
Gère les thèmes clair et sombre
"""
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QSettings


class ThemeManager(QObject):
    """
    Gestionnaire de thèmes pour l'application
    Permet de basculer entre mode clair et sombre
    """
    
    theme_changed = Signal(str)  # Émet le nom du nouveau thème
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        
        # Chemins vers les fichiers de style
        self.styles_dir = Path(__file__).parent.parent.parent / "assets" / "styles"
        
        print(f"[ThemeManager] Initialisé")
        print(f"[ThemeManager] Dossier styles: {self.styles_dir}")
        
        # Charger le thème sauvegardé AVANT de définir le thème par défaut
        self._current_theme = self._load_saved_theme()
        
        print(f"[ThemeManager] Thème chargé: {self._current_theme}")
    
    def _load_saved_theme(self) -> str:
        """
        Charge le thème sauvegardé depuis QSettings
        
        Returns:
            str: Le thème sauvegardé ('light' ou 'dark'), 'light' par défaut
        """
        try:
            settings = QSettings("Siledje", "Siledje")
            saved_theme = settings.value("theme", "light", type=str)
            
            # Validation du thème
            if saved_theme not in ['light', 'dark']:
                print(f"[ThemeManager] ⚠ Thème invalide dans QSettings: {saved_theme}")
                saved_theme = "light"
            
            print(f"[ThemeManager] Thème chargé depuis QSettings: {saved_theme}")
            return saved_theme
            
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur chargement thème depuis QSettings: {e}")
            return "light"
    
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
            print(f"[ThemeManager] ⚠ Thème invalide: {theme}")
            return
        
        # Ne rien faire si le thème est déjà le même
        if theme == self._current_theme:
            print(f"[ThemeManager] Thème déjà actif: {theme}")
            return
        
        print(f"[ThemeManager] Changement de thème: {self._current_theme} → {theme}")
        
        self._current_theme = theme
        
        # Sauvegarder IMMÉDIATEMENT dans QSettings
        self._save_theme()
        
        # Appliquer le thème global à l'application
        self._apply_global_theme()
        
        # Émettre le signal de changement
        self.theme_changed.emit(theme)
        
        print(f"[ThemeManager] ✅ Thème appliqué et sauvegardé: {theme}")
    
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
                main_stylesheet = self.load_stylesheet('main_style')
                if main_stylesheet:
                    app.setStyleSheet(main_stylesheet)
                    print(f"[ThemeManager] Stylesheet global appliqué")
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur application thème global: {e}")
    
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
        """Sauvegarde le thème actuel dans QSettings"""
        try:
            settings = QSettings("Siledje", "Siledje")
            settings.setValue("theme", self._current_theme)
            settings.sync()  # Forcer la synchronisation immédiate
            print(f"[ThemeManager] ✅ Thème sauvegardé dans QSettings: {self._current_theme}")
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur sauvegarde thème: {e}")
    
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