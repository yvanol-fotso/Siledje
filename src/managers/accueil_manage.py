"""
Manager de l'accueil - Logique métier uniquement.
Connecté à SchoolRepository (school_levels, school_systems, school_classes, books).

Règle de cascade stricte :
- Changer le NIVEAU efface langue + classe + tableau.
- Changer la LANGUE efface classe + tableau, recalcule les classes disponibles
  (le combo, une fois repeuplé via addItems(), déclenche naturellement
  currentTextChanged -> classe_changed côté vue, pas besoin de forcer un
  second appel manuel ici).
- Changer la CLASSE recharge le tableau des livres.
Aucun état obsolète ne doit survivre à un changement en amont.
"""

from PySide6.QtCore import QObject, Slot
from src.database.repositories.school_repository import SchoolRepository


class AccueilManager(QObject):

    version = "2.2.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None

        self.school_repo = SchoolRepository()

        # État actuel — toujours remis à zéro en cascade
        self.active_niveau = None
        self.active_langue = None
        self.active_classe = None
        self.active_classe_id = None

    def get_ui(self):
        """
        Retourne la vue associée à ce manager.
        Crée la vue et connecte les signaux.
        """
        if self.view is None:
            from src.ui.views.accueil_view import AccueilView

            self.view = AccueilView(self.parent)
            self._connect_view_signals()
            self._initialize_default_state()

        return self.view

    def _initialize_default_state(self):
        """
        Initialise l'état par défaut au démarrage.
        Sélectionne automatiquement Maternelle + Anglophone.
        Ces deux setChecked(True) déclenchent en cascade tous les signaux
        nécessaires (niveau_changed -> langue_changed -> classe_changed)
        via la vue, qui construit tout l'état jusqu'au tableau.
        """
        print("[AccueilManager] Initialisation de l'état par défaut...")
        self.view.radio_maternelle.setChecked(True)
        self.view.checkbox_anglo.setChecked(True)
        print("[AccueilManager] État initial: Maternelle + Anglophone")

    def _connect_view_signals(self):
        """Connecte les signaux de la vue aux slots du manager."""
        self.view.niveau_changed.connect(self.on_niveau_changed)
        self.view.langue_changed.connect(self.on_langue_changed)
        self.view.classe_changed.connect(self.on_classe_changed)

    def _reset_classe_state(self):
        """Efface systématiquement l'état classe + tableau."""
        self.active_classe = None
        self.active_classe_id = None
        if self.view:
            self.view.clear_table()

    @Slot(str)
    def on_niveau_changed(self, niveau: str):
        """Changement de niveau : reset langue + classe + tableau, on attend une langue."""
        print(f"[AccueilManager] Niveau changé: {niveau}")
        self.active_niveau = niveau
        self.active_langue = None
        self._reset_classe_state()

        if self.view:
            # update_classes([]) affiche le placeholder "Sélectionnez une langue"
            # et vide proprement le combo — cohérent avec le reste du flux.
            self.view.update_classes([])

    @Slot(str)
    def on_langue_changed(self, langue: str):
        """Changement de langue : reset classe + tableau, recalcule les classes."""
        print(f"[AccueilManager] Langue changée: {langue}")
        self.active_langue = langue
        self._reset_classe_state()
        self._update_available_classes()

    @Slot(str)
    def on_classe_changed(self, classe: str):
        """Changement de classe : recharge le tableau des livres pour cette classe."""
        print(f"[AccueilManager] Classe changée: {classe}")

        if not classe or not self.active_niveau or not self.active_langue:
            self._reset_classe_state()
            return

        self.active_classe = classe

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        match = next((c for c in classes if c["name"] == classe), None)
        self.active_classe_id = match["id"] if match else None

        self._update_books_table()

    def _update_available_classes(self):
        """
        Met à jour la liste des classes disponibles selon niveau + langue actuels.
        La vue déclenche automatiquement classe_changed via son signal
        currentTextChanged dès que le combo est repeuplé — aucun appel
        manuel supplémentaire n'est nécessaire ici.
        """
        if not self.view:
            return

        if not self.active_niveau or not self.active_langue:
            self.view.update_classes([])
            return

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        class_names = [c["name"] for c in classes][:5]

        print(f"[AccueilManager] Classes disponibles: {class_names}")
        self.view.update_classes(class_names)

    def _update_books_table(self):
        """
        Met à jour la table des livres selon la classe sélectionnée.
        IMPORTANT : les clés du dict doivent correspondre EXACTEMENT à celles
        attendues par AccueilView._add_table_row : "Titre", "Éditeur",
        "Édition", "Prix", "Intitulé" — et toutes les valeurs doivent être
        des chaînes (QTableWidgetItem ne fait pas de conversion implicite).
        """
        if not self.view:
            return

        if not self.active_classe_id:
            self.view.clear_table()
            return

        books = self.school_repo.get_books_for_class(self.active_classe_id)

        livres = []
        for b in books:
            prix = b.get("price_fcfa")
            if prix is None:
                prix = b.get("sell_price") or 0
            livres.append({
                "Titre": b.get("title") or "",
                "Éditeur": b.get("publisher") or "—",
                "Édition": b.get("edition") or "—",
                "Prix": f"{prix:.0f} FCFA",
                "Intitulé": b.get("intitule") or "—",
            })

        print(f"[AccueilManager] Livres trouvés: {len(livres)}")
        self.view.update_table(livres)

    def refresh(self):
        """Rafraîchit les données affichées selon l'état courant."""
        if not self.view:
            return
        if self.active_classe_id:
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
            "classe": self.active_classe,
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

        if niveau == "Maternelle":
            self.view.radio_maternelle.setChecked(True)
        elif niveau == "Primaire":
            self.view.radio_primaire.setChecked(True)
        elif niveau == "Secondaire":
            self.view.radio_secondaire.setChecked(True)

        if langue == "Anglophone":
            self.view.checkbox_anglo.setChecked(True)
        elif langue == "Francophone":
            self.view.checkbox_franco.setChecked(True)

        if classe:
            index = self.view.combo_classes.findText(classe)
            if index >= 0:
                self.view.combo_classes.setCurrentIndex(index)