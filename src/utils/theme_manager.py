"""
Gestionnaire de thèmes pour l'application
Gère les thèmes clair et sombre
"""
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QSettings


class ThemeManager(QObject):
    """Charge light_style.qss OU dark_style.qss — jamais les deux mélangés."""

    theme_changed = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.styles_dir = Path(__file__).parent.parent.parent / "assets" / "styles"
        self.icons_dir = self.styles_dir.parent / "icons"

        print(f"[ThemeManager] Initialisé")
        print(f"[ThemeManager] Dossier styles: {self.styles_dir}")
        print(f"[ThemeManager] Dossier icons: {self.icons_dir}")

        self._current_theme = self._load_saved_theme()
        print(f"[ThemeManager] Thème chargé: {self._current_theme}")

    def _load_saved_theme(self) -> str:
        try:
            settings = QSettings("Siledje", "Siledje")
            saved = settings.value("theme", "light", type=str)
            if saved not in ("light", "dark"):
                saved = "light"
            return saved
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur QSettings: {e}")
            return "light"

    def get_current_theme(self) -> str:
        return self._current_theme

    def set_theme(self, theme: str, force: bool = False):
        if theme not in ("light", "dark"):
            print(f"[ThemeManager] ⚠ Thème invalide: {theme}")
            return

        if theme == self._current_theme and not force:
            print(f"[ThemeManager] Thème déjà actif: {theme}")
            return

        print(f"[ThemeManager] {self._current_theme} → {theme}")
        self._current_theme = theme
        self._save_theme()
        self._apply_global_theme()
        self.theme_changed.emit(theme)
        print(f"[ThemeManager] ✅ Thème appliqué: {theme}")

    def toggle_theme(self):
        self.set_theme("dark" if self._current_theme == "light" else "light")

    def _apply_global_theme(self):
        """Charge UNIQUEMENT light_style.qss ou dark_style.qss."""
        try:
            app = QApplication.instance()
            if not app:
                return

            # ✅ Un fichier = un thème. Plus de mélange.
            filename = "dark_style" if self._current_theme == "dark" else "light_style"
            css = self.load_stylesheet(filename) or ""
            app.setStyleSheet(css)
            print(f"[ThemeManager] Stylesheet appliqué: {filename}.qss ({len(css)} car.)")
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur stylesheet: {e}")

    def load_stylesheet(self, name: str) -> str:
        """
        name sans extension : 'light_style', 'dark_style', 'login', 'main_style'...
        Les chemins relatifs 'assets/icons/...' du QSS sont convertis en chemins
        absolus (compatibles mode dev ET mode exe PyInstaller) avant application.
        """
        qss_path = self.styles_dir / f"{name}.qss"
        try:
            if qss_path.exists():
                with open(qss_path, "r", encoding="utf-8") as f:
                    content = f.read()
                content = self._resolve_asset_paths(content)
                print(f"[ThemeManager] Chargé: {name}.qss ({len(content)} car.)")
                return content
            print(f"[ThemeManager] ⚠ Introuvable: {qss_path}")
            return ""
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur lecture {name}.qss: {e}")
            return ""

    def _resolve_asset_paths(self, css: str) -> str:
        """Remplace 'url(assets/icons/...)' par le chemin absolu reel du dossier icons."""
        icons_dir_posix = self.icons_dir.as_posix()
        return css.replace("url(assets/icons/", f"url({icons_dir_posix}/")

    def _save_theme(self):
        try:
            settings = QSettings("Siledje", "Siledje")
            settings.setValue("theme", self._current_theme)
            settings.sync()
        except Exception as e:
            print(f"[ThemeManager] ⚠ Erreur sauvegarde: {e}")

    def get_color(self, color_name: str) -> str:
        colors = {
            "light": {
                "primary": "#3498db", "secondary": "#2980b9",
                "success": "#27ae60", "danger": "#e74c3c",
                "warning": "#f39c12", "info": "#3498db",
                "background": "#f5f5f5", "surface": "#ffffff",
                "text": "#2c3e50", "text_secondary": "#7f8c8d",
            },
            "dark": {
                "primary": "#1abc9c", "secondary": "#16a085",
                "success": "#27ae60", "danger": "#e74c3c",
                "warning": "#f39c12", "info": "#1abc9c",
                "background": "#1e2a38", "surface": "#2c3e50",
                "text": "#ecf0f1", "text_secondary": "#95a5a6",
            },
        }
        return colors[self._current_theme].get(color_name, "#000000")

    def apply_to_widget(self, widget, stylesheet_name: str = None):
        if stylesheet_name:
            css = self.load_stylesheet(stylesheet_name)
            if css:
                widget.setStyleSheet(css)
        widget.setProperty("theme", self._current_theme)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()