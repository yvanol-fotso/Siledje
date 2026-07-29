"""
Manager de l'accueil - Logique metier uniquement.
Connecte a SchoolRepository (school_levels, school_systems, school_classes, books).
"""

from PySide6.QtCore import QObject, QTimer, Slot
from src.database.repositories.school_repository import SchoolRepository


class AccueilManager(QObject):
    """Manager de l'accueil - Logique metier."""

    version = "2.2.0"

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

    def _reset_classe_state(self):
        self.active_classe = None
        self.active_classe_id = None
        if self.view:
            self.view.clear_table()

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
            self.view.update_classes([])
            self.view.checkbox_anglo.setChecked(False)
            self.view.checkbox_franco.setChecked(False)

    @Slot(str)
    def on_langue_changed(self, langue: str):
        print(f"[AccueilManager] Langue changee: {langue}")
        self.show_all_books = False
        self.active_langue = langue
        self._reset_classe_state()
        self._update_available_classes()

    @Slot(str)
    def on_classe_changed(self, classe: str):
        print(f"[AccueilManager] Classe changee: {classe}")

        if classe == "Toutes":
            self._update_all_books()
            return

        if not classe or classe in ("Selectionnez une langue", "Aucune classe disponible"):
            self._reset_classe_state()
            return

        if not self.active_niveau or not self.active_langue:
            self._reset_classe_state()
            return

        self.active_classe = classe
        self.show_all_books = False

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        match = next((c for c in classes if c["name"] == classe), None)
        self.active_classe_id = match["id"] if match else None

        self._update_books_table()

    def _update_all_books(self):
        """Affiche TOUS les livres actifs avec leur description."""
        if not self.view:
            return
        
        all_books = self.school_repo.get_all_books_with_classes(active_only=True)
        
        livres = []
        for b in all_books:
            prix = b.get("price_fcfa")
            if prix is None:
                prix = b.get("sell_price") or 0
            
            # ✅ Description = intitule ou classe ou "Description non disponible"
            description = b.get("intitule")
            if not description:
                class_name = b.get('class_name', '')
                description = f"Classe: {class_name}" if class_name else "Description non disponible"
            
            livres.append({
                "Titre": b.get("title") or b.get("product_name") or "",
                "Matiere": b.get("subject") or "-",
                "Editeur": b.get("publisher") or "-",
                "Prix": f"{prix:.0f} FCFA",
                "Description": description,
            })
        
        print(f"[AccueilManager] Tous les livres trouves: {len(livres)}")
        self.view.update_table(livres)

    def _update_available_classes(self):
        if not self.view:
            return

        if not self.active_niveau or not self.active_langue:
            self.view.update_classes([])
            return

        classes = self.school_repo.get_classes(self.active_niveau, self.active_langue)
        class_names = [c["name"] for c in classes]

        print(f"[AccueilManager] Classes disponibles: {class_names}")
        self.view.update_classes(class_names)

    def _update_books_table(self):
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
            
            # ✅ Description = intitule ou "Description non disponible"
            description = b.get("intitule") or "Description non disponible"
            
            livres.append({
                "Titre": b.get("title") or "",
                "Matiere": b.get("subject") or "-",
                "Editeur": b.get("publisher") or "-",
                "Prix": f"{prix:.0f} FCFA",
                "Description": description,
            })

        print(f"[AccueilManager] Livres trouves: {len(livres)}")
        self.view.update_table(livres)

    def refresh(self):
        if not self.view:
            return
        if self.show_all_books:
            self._update_all_books()
        elif self.active_classe_id:
            self._update_books_table()
        elif self.active_langue:
            self._update_available_classes()

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