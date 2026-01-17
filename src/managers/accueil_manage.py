"""
Manager de l'accueil - Logique métier uniquement.
Gère les données et communique avec la vue via des signaux.
"""

from PySide6.QtCore import QObject, Slot
from data.dummy_data.data_home import classes_par_niveau, livres_par_classe


class AccueilManager(QObject):
    """
    Manager de l'accueil - Logique métier.
    Sépare complètement la logique de la présentation.
    """
    
    version = "1.0.0"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None
        
        # État actuel
        self.active_niveau = None
        self.active_langue = None
        self.active_classe = None
    
    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            # Import local pour éviter les imports circulaires
            from src.ui.views.accueil_view import AccueilView
            
            self.view = AccueilView(self.parent)
            self._connect_view_signals()
            
            # Initialiser avec des valeurs par défaut
            self._initialize_default_state()
        
        return self.view
    
    def _initialize_default_state(self):
        """
        Initialise l'état par défaut au démarrage.
        Sélectionne automatiquement Maternelle + Anglophone.
        """
        print("[AccueilManager] Initialisation de l'état par défaut...")
        
        # Sélectionner Maternelle par défaut
        self.view.radio_maternelle.setChecked(True)
        
        # Sélectionner Anglophone par défaut
        self.view.checkbox_anglo.setChecked(True)
        
        print("[AccueilManager] État initial: Maternelle + Anglophone")
    
    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.niveau_changed.connect(self.on_niveau_changed)
        self.view.langue_changed.connect(self.on_langue_changed)
        self.view.classe_changed.connect(self.on_classe_changed)
    
    @Slot(str)
    def on_niveau_changed(self, niveau: str):
        """
        Gère le changement de niveau (Maternelle, Primaire, Secondaire).
        
        Args:
            niveau: Le nouveau niveau sélectionné
        """
        print(f"[AccueilManager] Niveau changé: {niveau}")
        self.active_niveau = niveau
        self.active_langue = None
        self.active_classe = None
        
        # Réinitialiser la vue
        self.view.combo_classes.clear()
        self.view.clear_table()
    
    @Slot(str)
    def on_langue_changed(self, langue: str):
        """
        Gère le changement de langue (Anglophone, Francophone).
        
        Args:
            langue: La nouvelle langue sélectionnée
        """
        print(f"[AccueilManager] Langue changée: {langue}")
        self.active_langue = langue
        self.active_classe = None
        
        # Mettre à jour les classes disponibles
        self._update_available_classes()
    
    @Slot(str)
    def on_classe_changed(self, classe: str):
        """
        Gère le changement de classe.
        
        Args:
            classe: La nouvelle classe sélectionnée
        """
        print(f"[AccueilManager] Classe changée: {classe}")
        self.active_classe = classe
        
        # Mettre à jour la table des livres
        self._update_books_table()
    
    def _update_available_classes(self):
        """Met à jour la liste des classes disponibles selon le niveau et la langue."""
        if not self.active_niveau or not self.active_langue:
            self.view.update_classes([])
            return
        
        # Récupérer les classes depuis les données
        key = (self.active_niveau, self.active_langue)
        classes = classes_par_niveau.get(key, [])
        
        # Limiter à 5 classes
        classes = classes[:5]
        
        print(f"[AccueilManager] Classes disponibles: {classes}")
        self.view.update_classes(classes)
        
        # Sélectionner automatiquement la première classe
        if classes:
            self.view.combo_classes.setCurrentIndex(0)
    
    def _update_books_table(self):
        """Met à jour la table des livres selon la classe sélectionnée."""
        if not self.active_classe:
            self.view.clear_table()
            return
        
        # Récupérer les livres depuis les données
        livres = livres_par_classe.get(self.active_classe, [])
        
        print(f"[AccueilManager] Livres trouvés: {len(livres)}")
        self.view.update_table(livres)
    
    def refresh(self):
        """Rafraîchit les données affichées."""
        if self.view:
            if self.active_classe:
                self._update_books_table()
            elif self.active_langue:
                self._update_available_classes()
    
    def get_current_state(self) -> dict:
        """
        Retourne l'état actuel du manager.
        
        Returns:
            Dictionnaire avec l'état actuel
        """
        return {
            "niveau": self.active_niveau,
            "langue": self.active_langue,
            "classe": self.active_classe
        }
    
    def load_state(self, state: dict):
        """
        Charge un état sauvegardé.
        
        Args:
            state: Dictionnaire avec l'état à charger
        """
        if not self.view:
            return
        
        niveau = state.get("niveau")
        langue = state.get("langue")
        classe = state.get("classe")
        
        if niveau:
            # Simuler la sélection du niveau
            if niveau == "Maternelle":
                self.view.radio_maternelle.setChecked(True)
            elif niveau == "Primaire":
                self.view.radio_primaire.setChecked(True)
            elif niveau == "Secondaire":
                self.view.radio_secondaire.setChecked(True)
        
        if langue:
            # Simuler la sélection de la langue
            if langue == "Anglophone":
                self.view.checkbox_anglo.setChecked(True)
            elif langue == "Francophone":
                self.view.checkbox_franco.setChecked(True)
        
        if classe:
            # Sélectionner la classe
            index = self.view.combo_classes.findText(classe)
            if index >= 0:
                self.view.combo_classes.setCurrentIndex(index)