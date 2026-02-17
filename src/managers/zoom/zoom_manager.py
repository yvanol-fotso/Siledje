"""
Gestionnaire du zoom de l'application.
Gère le niveau de zoom en modifiant la taille de police globale.
Emplacement: src/managers/zoom/zoom_manager.py
"""

from PySide6.QtCore import QObject, Signal, QSettings
from PySide6.QtWidgets import QApplication


class ZoomManager(QObject):
    """
    Gère le zoom de l'application via la taille de police globale.
    Niveaux: 75%, 90%, 100%, 110%, 125%, 150%, 175%, 200%
    """

    version = "1.0.0"

    # Signal émis quand le zoom change (niveau en pourcentage)
    zoom_changed = Signal(int)

    # Niveaux de zoom disponibles
    ZOOM_LEVELS = [75, 90, 100, 110, 125, 150, 175, 200]

    # Taille de police de base en points
    BASE_FONT_SIZE = 10

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QSettings("VotreEntreprise", "LibrairiePapeterie")

        # Charger le niveau sauvegardé
        saved = self.settings.value("zoom_level", 100, type=int)
        if saved not in self.ZOOM_LEVELS:
            saved = 100

        self._current_level = saved

        print(f"[ZoomManager v{self.version}] Initialisé - Zoom: {self._current_level}%")

    # ========== PROPRIÉTÉS ==========

    @property
    def current_level(self) -> int:
        """Niveau de zoom actuel en pourcentage."""
        return self._current_level

    @property
    def current_index(self) -> int:
        """Index du niveau actuel dans ZOOM_LEVELS."""
        try:
            return self.ZOOM_LEVELS.index(self._current_level)
        except ValueError:
            return self.ZOOM_LEVELS.index(100)

    @property
    def can_zoom_in(self) -> bool:
        """True si on peut encore zoomer en avant."""
        return self.current_index < len(self.ZOOM_LEVELS) - 1

    @property
    def can_zoom_out(self) -> bool:
        """True si on peut encore zoomer en arrière."""
        return self.current_index > 0

    # ========== OPÉRATIONS ==========

    def zoom_in(self) -> bool:
        """Zoom avant vers le niveau suivant. Retourne True si appliqué."""
        if not self.can_zoom_in:
            print(f"[ZoomManager] Maximum atteint ({self._current_level}%)")
            return False
        self._apply_zoom(self.ZOOM_LEVELS[self.current_index + 1])
        return True

    def zoom_out(self) -> bool:
        """Zoom arrière vers le niveau précédent. Retourne True si appliqué."""
        if not self.can_zoom_out:
            print(f"[ZoomManager] Minimum atteint ({self._current_level}%)")
            return False
        self._apply_zoom(self.ZOOM_LEVELS[self.current_index - 1])
        return True

    def reset_zoom(self):
        """Réinitialise le zoom à 100%."""
        self._apply_zoom(100)

    def set_zoom(self, level: int):
        """Définit un niveau de zoom précis."""
        if level not in self.ZOOM_LEVELS:
            print(f"[ZoomManager] Niveau {level}% non disponible")
            return
        self._apply_zoom(level)

    def apply_saved_zoom(self):
        """Applique le zoom sauvegardé au démarrage de l'application."""
        if self._current_level != 100:
            self._apply_zoom(self._current_level)

    # ========== MÉTHODE PRIVÉE ==========

    def _apply_zoom(self, level: int):
        """Applique le niveau de zoom à l'application entière."""
        self._current_level = level

        # Calculer la nouvelle taille de police
        new_font_size = self.BASE_FONT_SIZE * (level / 100)

        # Appliquer à l'application
        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSizeF(new_font_size)
            app.setFont(font)

        # Sauvegarder
        self.settings.setValue("zoom_level", level)
        self.settings.sync()

        # Émettre le signal
        self.zoom_changed.emit(level)

        print(f"[ZoomManager] Zoom: {level}% - Police: {new_font_size:.1f}pt")