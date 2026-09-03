"""
Manager de l'accueil - Logique metier uniquement.
Connecte a SchoolRepository (school_levels, school_systems, school_classes, books).

CHANGELOG (correctifs) :
- BUG CORRIGE (filtres Niveau/Langue -> "0 livre(s)") : update_classes() sur
  la vue peuple le combo Classe avec blockSignals(True) (pour eviter une
  cascade de signaux pendant le remplissage), donc le retour automatique
  sur "Toutes" ne declenchait plus aucun affichage. On appelle desormais
  explicitement l'affichage juste apres avoir peuple le combo, au lieu
  d'attendre une interaction manuelle de l'utilisateur.
- BUG CORRIGE ("Toutes" ignorait le niveau/langue actifs) : selectionner
  "Toutes" dans le combo Classe appelait _update_all_books(), qui affiche
  litteralement TOUS les livres de l'application, sans respecter le
  niveau/langue deja choisis. "Toutes" dans ce contexte doit vouloir dire
  "toutes les classes de ce niveau+langue", pas "tout, sans filtre".
  Nouvelle methode dediee : _update_books_for_niveau_langue().
- BUG CORRIGE (bouton "Actualiser" muet) : le signal refresh_requested de
  la vue (herite de BaseView, comme StockView/SupplierView/etc.) n'etait
  jamais connecte a self.refresh(). Ajoute dans _connect_view_signals().
- Refactor : la construction des lignes de tableau (dict Titre/Matiere/
  Editeur/Prix/Description) etait dupliquee dans _update_all_books() et
  _update_books_table(). Extraite dans _books_to_rows(), un seul endroit
  a modifier si le format d'affichage doit changer.
"""

from PySide6.QtCore import QObject, QTimer, Slot
from src.database.repositories.school_repository import SchoolRepository


class AccueilManager(QObject):
    """Manager de l'accueil - Logique metier."""

    version = "2.3.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.view = None

        self.school_repo = SchoolRepository()

        self.active_niveau = None
        self.active_langue = None
        self.active_classe = None
        self.active_classe_id = None
        self.show_all_books = True

    def get_ui(self):
        if self.view is None:
            from src.ui.views.accueil.accueil_view import AccueilView

            self.view = AccueilView(self.parent)
            self._connect_view_signals()
            self._initialize_default_state()

        return self.view

    def _initialize_default_state(self):
        print("[AccueilManager] Initialisation de l'etat par defaut...")
        QTimer.singleShot(100, self._show_all_books)

    def _show_all_books(self):
        if self.view:
            self.view.all_books_requested.emit()
            print("[AccueilManager] Affichage de tous les livres")

    def _connect_view_signals(self):
        self.view.all_books_requested.connect(self.on_all_books_requested)
        self.view.niveau_changed.connect(self.on_niveau_changed)
        self.view.langue_changed.connect(self.on_langue_changed)
        self.view.classe_changed.connect(self.on_classe_changed)
        # Bouton "Actualiser" (herite de BaseView) : manquait, c'est ce
        # qui le rendait muet malgre sa presence a l'ecran.
        self.view.refresh_requested.connect(self.refresh)

    def _reset_classe_state(self):
        self.active_classe = None
        self.active_classe_id = None

    # ========== HANDLERS DE FILTRES ==========

    @Slot()
    def on_all_books_requested(self):
        print("[AccueilManager] Affichage de tous les livres")
        self.show_all_books = True
        self.active_niveau = None
        self.active_langue = None
        self._reset_classe_state()
        self._update_all_books()

    @Slot(str)
    def on_niveau_changed(self, niveau: str):
        print(f"[AccueilManager] Niveau change: {niveau}")
        self.show_all_books = False
        self.active_niveau = niveau
        self.active_langue = None
        self._reset_classe_state()

        if self.view:
            self.view.clear_table()
            self.view.update_classes([])
            self.view.checkbox_anglo.setChecked(False)
            self.view.checkbox_franco.setChecked(False)

    @Slot(str)
    def on_langue_changed(self, langue: str):
        print(f"[AccueilManager] Langue changee: {langue}")
        self.show_all_books = False
        self.active_langue = langue
        self._reset_classe_state()
        # Peuple le combo Classe (qui revient sur "Toutes" sans emettre de
        # signal, blockSignals oblige) ET affiche immediatement les livres
        # du niveau+langue actifs, sans attendre que l'utilisateur touche
        # au combo lui-meme.
        self._update_available_classes()

    @Slot(str)
    def on_classe_changed(self, classe: str):
        print(f"[AccueilManager] Classe changee: {classe}")

        if classe == "Toutes":
            # "Toutes" = toutes les classes du niveau+langue actifs, PAS
            # tous les livres de l'application (c'est le role de "Tous"
            # au niveau du filtre Niveau, deja gere par
            # on_all_books_requested).
            self._reset_classe_state()
            self._update_books_for_niveau_langue()
            return

        if not classe or classe in ("Selectionnez une langue", "Aucune classe disponible"):
            self._reset_classe_state()
            if self.view:
                self.view.clear_table()
            return

        if not self.active_niveau or not self.active_langue:
            self._reset_classe_state()
            if self.view:
                self.view.clear_table()
            return

        self.active_classe = classe
        self.show_all_books = False

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        match = next((c for c in classes if c["name"] == classe), None)
        self.active_classe_id = match["id"] if match else None

        self._update_books_table()

    # ========== CONSTRUCTION DES LIGNES DE TABLEAU ==========

    @staticmethod
    def _books_to_rows(books: list) -> list:
        """Convertit une liste de livres (dicts issus du repository) en
        lignes affichables par AccueilTable. Seul endroit a modifier si
        le format d'affichage (colonnes, valeurs par defaut) doit changer
        — evite la duplication qui existait entre les deux methodes
        d'affichage."""
        rows = []
        for b in books:
            prix = b.get("price_fcfa")
            if prix is None:
                prix = b.get("sell_price") or 0

            description = b.get("intitule")
            if not description:
                class_name = b.get("class_name", "")
                description = f"Classe: {class_name}" if class_name else "Description non disponible"

            rows.append({
                "Titre": b.get("title") or b.get("product_name") or "",
                "Matiere": b.get("subject") or "-",
                "Editeur": b.get("publisher") or "-",
                "Prix": f"{prix:.0f} FCFA",
                "Description": description,
            })
        return rows

    # ========== AFFICHAGE ==========

    def _update_all_books(self):
        """Affiche TOUS les livres actifs de l'application, sans filtre
        de niveau/langue/classe — utilise uniquement quand le radio
        'Tous' (niveau) est selectionne."""
        if not self.view:
            return

        all_books = self.school_repo.get_all_books_with_classes(active_only=True)
        livres = self._books_to_rows(all_books)

        print(f"[AccueilManager] Tous les livres trouves: {len(livres)}")
        self.view.update_table(livres)

    def _update_available_classes(self):
        if not self.view:
            return

        if not self.active_niveau or not self.active_langue:
            self.view.update_classes([])
            self.view.clear_table()
            return

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        class_names = [c["name"] for c in classes]

        print(f"[AccueilManager] Classes disponibles: {class_names}")
        self.view.update_classes(class_names)

        # Le combo revient sur "Toutes" par defaut mais AUCUN signal n'est
        # emis (blockSignals dans update_classes) : sans cet appel, le
        # tableau resterait vide jusqu'a une interaction manuelle de
        # l'utilisateur avec le combo.
        self._update_books_for_niveau_langue()

    def _update_books_for_niveau_langue(self):
        """Affiche tous les livres du niveau+langue actifs (equivalent de
        'Toutes' dans le combo Classe, une fois un niveau et une langue
        selectionnes)."""
        if not self.view:
            return

        if not self.active_niveau or not self.active_langue:
            self.view.clear_table()
            return

        all_books = self.school_repo.get_all_books_with_classes(active_only=True)
        filtered = [
            b for b in all_books
            if b.get("level_name") == self.active_niveau
            and b.get("system_name") == self.active_langue
        ]
        livres = self._books_to_rows(filtered)

        print(
            f"[AccueilManager] Livres pour {self.active_niveau}/"
            f"{self.active_langue}: {len(livres)}"
        )
        self.view.update_table(livres)

    def _update_books_table(self):
        """Affiche les livres d'UNE classe precise (self.active_classe_id)."""
        if not self.view:
            return

        if not self.active_classe_id:
            self.view.clear_table()
            return

        books = self.school_repo.get_books_for_class(self.active_classe_id)
        livres = self._books_to_rows(books)

        print(f"[AccueilManager] Livres trouves: {len(livres)}")
        self.view.update_table(livres)

    # ========== ACTUALISATION ==========

    @Slot()
    def refresh(self):
        """Reaffiche les donnees selon l'etat de filtre actuel — sans
        reinitialiser les filtres eux-memes (contrairement a
        on_all_books_requested)."""
        if not self.view:
            return
        if self.active_classe_id:
            self._update_books_table()
        elif self.active_niveau and self.active_langue:
            self._update_books_for_niveau_langue()
        elif self.show_all_books:
            self._update_all_books()
        # Sinon : un niveau est choisi mais pas encore de langue —
        # rien de plus a afficher tant que l'utilisateur n'a pas
        # complete son filtre.

    def get_current_state(self) -> dict:
        return {
            "show_all_books": self.show_all_books,
            "niveau": self.active_niveau,
            "langue": self.active_langue,
            "classe": self.active_classe,
        }

    def set_theme(self, is_dark: bool):
        if self.view is not None:
            self.view.set_theme(is_dark)
            print(f"[AccueilManager] Theme applique: {'dark' if is_dark else 'light'}")